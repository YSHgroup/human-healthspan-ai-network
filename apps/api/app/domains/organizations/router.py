from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.notifications.service import notify
from app.domains.organizations.service import (
    LEAD_ROLES,
    MANAGE_ROLES,
    create_default_badges,
    membership,
    organization_or_404,
    require_member,
    unique_slug,
)
from app.domains.professional.router import record_out
from app.domains.research.access import has_research_access, project_or_404
from app.domains.subscriptions.service import list_entitlements, use_feature
from app.models.domain import Profile, ResearchProject, User
from app.models.platform import (
    Badge,
    Organization,
    OrganizationInvitation,
    OrganizationMember,
    ProfessionalRecord,
    ProjectOrganization,
    UserBadge,
    WorkHistoryEntry,
)
from app.schemas.platform import (
    BadgeAward,
    BadgeOut,
    EntitlementOut,
    InvitationOut,
    OrgBadgeCreate,
    OrganizationCreate,
    OrganizationDetailOut,
    OrganizationInviteCreate,
    OrganizationMemberOut,
    OrganizationOut,
    OrganizationRoleUpdate,
    OrganizationUpdate,
    ProfessionalRecordOut,
    ProjectAttach,
    WorkHistoryOut,
)
from app.schemas.research import ResearchProjectOut
from app.services.audit import record_audit_event
from app.services.authorization import AuthorizationService

router = APIRouter(tags=["organizations"])
invitations_router = APIRouter(tags=["invitations"])


def _detail(db: Session, organization: Organization, user: User | None) -> OrganizationDetailOut:
    count = db.scalar(
        select(func.count()).select_from(OrganizationMember).where(OrganizationMember.organization_id == organization.id)
    ) or 0
    member = membership(db, organization.id, user.id) if user is not None else None
    out = OrganizationDetailOut.model_validate(organization)
    out.member_count = count
    out.my_role = member.role if member else None
    return out


@router.post("", response_model=OrganizationDetailOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationDetailOut:
    if not has_research_access(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creating an organization requires approved researcher membership.")
    if not use_feature(db, "user", user.id, "organization.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creating an organization is a premium feature. Purchase or request an organization entitlement first.",
        )
    organization = Organization(
        slug=unique_slug(db, payload.name),
        name=payload.name,
        description=payload.description,
        website=payload.website,
        created_by=user.id,
        policy={"ai_external_provider_allowed": False},
    )
    db.add(organization)
    db.flush()
    db.add(OrganizationMember(organization_id=organization.id, user_id=user.id, role="founder"))
    create_default_badges(db, organization)
    record_audit_event(db, user.id, "organization.created", "organization", organization.id)
    db.commit()
    db.refresh(organization)
    return _detail(db, organization, user)


@router.get("", response_model=list[OrganizationDetailOut])
def my_organizations(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[OrganizationDetailOut]:
    organizations = db.scalars(
        select(Organization)
        .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
        .where(OrganizationMember.user_id == user.id, Organization.is_active.is_(True))
        .order_by(Organization.name.asc())
    )
    return [_detail(db, organization, user) for organization in organizations]


@router.get("/discover", response_model=list[OrganizationOut])
def discover_organizations(
    q: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    db: Session = Depends(get_db),
) -> list[Organization]:
    query = select(Organization).where(Organization.is_active.is_(True))
    if q:
        query = query.where(Organization.name.ilike(f"%{q.strip()}%"))
    return list(db.scalars(query.order_by(Organization.name.asc()).limit(limit)))


@router.get("/{organization_id}", response_model=OrganizationDetailOut)
def get_organization(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> OrganizationDetailOut:
    return _detail(db, organization_or_404(db, organization_id), user)


@router.patch("/{organization_id}", response_model=OrganizationDetailOut)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationDetailOut:
    require_member(db, user, organization_id, MANAGE_ROLES)
    organization = organization_or_404(db, organization_id)
    changes = payload.model_dump(exclude_unset=True)
    if "policy" in changes and changes["policy"] is not None:
        # Only known policy keys are accepted; the policy is configuration, not free-form data.
        allowed = {"ai_external_provider_allowed"}
        if set(changes["policy"]) - allowed:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown organization policy key.")
        organization.policy = {**(organization.policy or {}), **changes.pop("policy")}
    else:
        changes.pop("policy", None)
    for field, value in changes.items():
        setattr(organization, field, value)
    record_audit_event(db, user.id, "organization.updated", "organization", organization.id)
    db.commit()
    db.refresh(organization)
    return _detail(db, organization, user)


# ------------------------------------------------------------------ members and invitations
@router.get("/{organization_id}/members", response_model=list[OrganizationMemberOut])
def list_members(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[OrganizationMemberOut]:
    require_member(db, user, organization_id)
    rows = db.execute(
        select(OrganizationMember, Profile.display_name)
        .outerjoin(Profile, Profile.user_id == OrganizationMember.user_id)
        .where(OrganizationMember.organization_id == organization_id)
        .order_by(OrganizationMember.created_at.asc())
    )
    return [OrganizationMemberOut(user_id=member.user_id, display_name=name or "Member", role=member.role) for member, name in rows]


@router.post("/{organization_id}/invitations", status_code=status.HTTP_201_CREATED)
def invite_member(
    organization_id: UUID,
    payload: OrganizationInviteCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    actor = require_member(db, user, organization_id, MANAGE_ROLES)
    organization = organization_or_404(db, organization_id)
    if payload.role == "founder" or (payload.role in {"owner", "administrator"} and actor.role not in {"founder", "owner"}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot grant that organization role.")
    target = db.get(User, payload.user_id)
    if target is None or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if membership(db, organization_id, target.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This user is already a member.")
    pending = db.scalar(
        select(OrganizationInvitation.id).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.invited_user_id == target.id,
            OrganizationInvitation.status == "pending",
        )
    )
    if pending is None:
        invitation = OrganizationInvitation(
            organization_id=organization_id, invited_user_id=target.id, invited_by=user.id, role=payload.role
        )
        db.add(invitation)
        db.flush()
        notify(db, target.id, "organization.invitation", f"Invitation to join {organization.name}", None, "organization", organization_id, user.id)
        record_audit_event(db, user.id, "organization.invited", "organization", organization_id, {"invited": str(target.id), "role": payload.role})
        db.commit()
    return {"status": "invited"}


@router.patch("/{organization_id}/members/{member_user_id}", response_model=OrganizationMemberOut)
def change_member_role(
    organization_id: UUID,
    member_user_id: UUID,
    payload: OrganizationRoleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMemberOut:
    actor = require_member(db, user, organization_id, MANAGE_ROLES)
    target = membership(db, organization_id, member_user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")
    if target.role == "founder" or payload.role == "founder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The founder role cannot be assigned or changed.")
    if (payload.role in {"owner", "administrator"} or target.role in {"owner", "administrator"}) and actor.role not in {"founder", "owner"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a founder or owner can manage administrators and owners.")
    target.role = payload.role
    record_audit_event(db, user.id, "organization.role_changed", "organization", organization_id, {"member": str(member_user_id), "role": payload.role})
    db.commit()
    profile = db.scalar(select(Profile).where(Profile.user_id == member_user_id))
    return OrganizationMemberOut(user_id=member_user_id, display_name=profile.display_name if profile else "Member", role=target.role)


@router.delete("/{organization_id}/members/{member_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    organization_id: UUID,
    member_user_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    actor = require_member(db, user, organization_id)
    target = membership(db, organization_id, member_user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")
    if target.role == "founder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The founder cannot be removed.")
    if member_user_id != user.id:
        if actor.role not in MANAGE_ROLES or (target.role in {"owner", "administrator"} and actor.role not in {"founder", "owner"}):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot remove this member.")
    db.delete(target)
    record_audit_event(db, user.id, "organization.member_removed", "organization", organization_id, {"member": str(member_user_id)})
    db.commit()


@invitations_router.get("", response_model=list[InvitationOut])
def my_invitations(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InvitationOut]:
    rows = db.execute(
        select(OrganizationInvitation, Organization.name)
        .join(Organization, Organization.id == OrganizationInvitation.organization_id)
        .where(OrganizationInvitation.invited_user_id == user.id, OrganizationInvitation.status == "pending")
        .order_by(OrganizationInvitation.created_at.desc())
    )
    results = []
    for invitation, name in rows:
        out = InvitationOut.model_validate(invitation)
        out.organization_name = name
        results.append(out)
    return results


def _respond(db: Session, user: User, invitation_id: UUID, accept: bool) -> dict[str, str]:
    invitation = db.get(OrganizationInvitation, invitation_id)
    if invitation is None or invitation.invited_user_id != user.id or invitation.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")
    organization = db.get(Organization, invitation.organization_id)
    invitation.responded_at = utc_now()
    if accept and organization is not None and organization.is_active:
        invitation.status = "accepted"
        if membership(db, invitation.organization_id, user.id) is None:
            db.add(OrganizationMember(organization_id=invitation.organization_id, user_id=user.id, role=invitation.role))
        notify(db, invitation.invited_by, "organization.invitation_accepted", "An invitation was accepted", organization.name, "organization", organization.id, user.id)
        record_audit_event(db, user.id, "organization.joined", "organization", invitation.organization_id)
    else:
        invitation.status = "declined" if not accept else "expired"
    db.commit()
    return {"status": invitation.status}


@invitations_router.post("/{invitation_id}/accept")
def accept_invitation(invitation_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    return _respond(db, user, invitation_id, True)


@invitations_router.post("/{invitation_id}/decline")
def decline_invitation(invitation_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    return _respond(db, user, invitation_id, False)


# ------------------------------------------------------------------ organization projects
@router.post("/{organization_id}/projects", status_code=status.HTTP_201_CREATED)
def attach_project(
    organization_id: UUID,
    payload: ProjectAttach,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    from app.domains.organizations.service import RESEARCH_ROLES

    require_member(db, user, organization_id, RESEARCH_ROLES)
    project = project_or_404(db, payload.project_id)
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project owner can attach it to an organization.")
    existing = db.scalar(select(ProjectOrganization).where(ProjectOrganization.project_id == project.id))
    if existing is not None:
        if existing.organization_id == organization_id:
            return {"status": "already_attached"}
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This project already belongs to another organization.")
    db.add(ProjectOrganization(project_id=project.id, organization_id=organization_id, attached_by=user.id))
    record_audit_event(db, user.id, "organization.project_attached", "organization", organization_id, {"project": str(project.id)})
    db.commit()
    return {"status": "attached"}


@router.get("/{organization_id}/projects", response_model=list[ResearchProjectOut])
def organization_projects(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ResearchProject]:
    require_member(db, user, organization_id)
    attached = select(ProjectOrganization.project_id).where(ProjectOrganization.organization_id == organization_id)
    readable = AuthorizationService(db).readable_project_ids(user)
    return list(
        db.scalars(
            select(ResearchProject)
            .where(ResearchProject.id.in_(attached), ResearchProject.id.in_(readable))
            .order_by(ResearchProject.created_at.desc())
        )
    )


# ------------------------------------------------------------------ verification
@router.post(
    "/{organization_id}/members/{member_user_id}/professional/{record_id}/verify",
    response_model=ProfessionalRecordOut,
)
def verify_professional_record(
    organization_id: UUID,
    member_user_id: UUID,
    record_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalRecordOut:
    require_member(db, user, organization_id, LEAD_ROLES)
    if membership(db, organization_id, member_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")
    record = db.get(ProfessionalRecord, record_id)
    if record is None or record.user_id != member_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional record not found.")
    record.verification_status = "verified"
    record.verified_by = user.id
    record.verified_by_organization_id = organization_id
    record.verified_at = utc_now()
    notify(db, member_user_id, "professional.verified", "A professional record was verified", record.title, "professional_record", record.id, user.id)
    record_audit_event(db, user.id, "professional.verified", "professional_record", record.id, {"organization": str(organization_id)})
    db.commit()
    db.refresh(record)
    return record_out(record)


@router.post("/{organization_id}/work-history/{entry_id}/verify", response_model=WorkHistoryOut)
def verify_work_history(
    organization_id: UUID,
    entry_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkHistoryEntry:
    require_member(db, user, organization_id, LEAD_ROLES)
    entry = db.get(WorkHistoryEntry, entry_id)
    if entry is None or entry.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work history entry not found.")
    entry.verification_status = "verified"
    entry.verified_by = user.id
    entry.verified_at = utc_now()
    record_audit_event(db, user.id, "work_history.verified", "work_history", entry.id, {"organization": str(organization_id)})
    db.commit()
    db.refresh(entry)
    return entry


# ------------------------------------------------------------------ badges and entitlements
@router.get("/{organization_id}/badges", response_model=list[BadgeOut])
def organization_badges(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Badge]:
    require_member(db, user, organization_id)
    return list(db.scalars(select(Badge).where(Badge.organization_id == organization_id).order_by(Badge.created_at.asc())))


@router.post("/{organization_id}/badges", response_model=BadgeOut, status_code=status.HTTP_201_CREATED)
def create_organization_badge(
    organization_id: UUID,
    payload: OrgBadgeCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Badge:
    require_member(db, user, organization_id, MANAGE_ROLES)
    organization = organization_or_404(db, organization_id)
    if not use_feature(db, "organization", organization_id, "organization.badge"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Two contributor badges come with every organization; additional badges must be purchased.",
        )
    from app.domains.organizations.service import slugify

    slug = f"{organization.slug}-{slugify(payload.name)}"
    if db.scalar(select(Badge.id).where(Badge.slug == slug)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A badge with this name already exists.")
    badge = Badge(
        slug=slug, name=payload.name, description=payload.description, kind="organization_contributor", organization_id=organization_id
    )
    db.add(badge)
    db.flush()
    record_audit_event(db, user.id, "organization.badge_created", "badge", badge.id)
    db.commit()
    db.refresh(badge)
    return badge


@router.post("/{organization_id}/badges/{badge_id}/award", status_code=status.HTTP_204_NO_CONTENT)
def award_organization_badge(
    organization_id: UUID,
    badge_id: UUID,
    payload: BadgeAward,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    require_member(db, user, organization_id, LEAD_ROLES)
    badge = db.get(Badge, badge_id)
    if badge is None or badge.organization_id != organization_id or not badge.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found.")
    if membership(db, organization_id, payload.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")
    if db.scalar(select(UserBadge.id).where(UserBadge.user_id == payload.user_id, UserBadge.badge_id == badge_id)) is None:
        db.add(UserBadge(user_id=payload.user_id, badge_id=badge_id, awarded_by=user.id))
        notify(db, payload.user_id, "badge.awarded", f"You received the badge: {badge.name}", None, "badge", badge.id, user.id)
        record_audit_event(db, user.id, "organization.badge_awarded", "badge", badge.id, {"member": str(payload.user_id)})
        db.commit()


@router.get("/{organization_id}/entitlements", response_model=list[EntitlementOut])
def organization_entitlements(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_member(db, user, organization_id, MANAGE_ROLES)
    return list_entitlements(db, "organization", organization_id)


