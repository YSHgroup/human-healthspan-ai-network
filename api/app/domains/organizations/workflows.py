"""Organization requests, tenant membership, and invitation workflows."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Organization,
    OrganizationCreationRequest,
    OrganizationInvitation,
    OrganizationMembership,
    User,
)


class OrganizationWorkflowError(ValueError):
    pass


class OrganizationNotFound(OrganizationWorkflowError):
    pass


class OrganizationAccessDenied(OrganizationWorkflowError):
    pass


class OrganizationConflict(OrganizationWorkflowError):
    pass


def _is_expired(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)


def get_active_organization_membership(
    db: Session,
    organization_id: str,
    user_id: str,
) -> OrganizationMembership | None:
    return db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == "active",
        )
    )


def submit_organization_request(
    db: Session,
    requester: User,
    *,
    slug: str,
    name: str,
    description: str,
    website: str,
) -> OrganizationCreationRequest:
    normalized_slug = slug.strip().lower()
    existing_org = db.scalar(select(Organization.id).where(Organization.slug == normalized_slug))
    pending_request = db.scalar(
        select(OrganizationCreationRequest.id).where(
            OrganizationCreationRequest.slug == normalized_slug,
            OrganizationCreationRequest.status == "pending",
        )
    )
    if existing_org is not None or pending_request is not None:
        raise OrganizationConflict("Organization slug is already in use or under review")
    request = OrganizationCreationRequest(
        requester_id=requester.id,
        slug=normalized_slug,
        name=name.strip(),
        description=description.strip(),
        website=website.strip(),
    )
    db.add(request)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise OrganizationConflict("Organization request could not be submitted") from exc
    db.refresh(request)
    return request


def list_organization_requests(db: Session, user: User) -> list[OrganizationCreationRequest]:
    return list(
        db.scalars(
            select(OrganizationCreationRequest)
            .where(OrganizationCreationRequest.requester_id == user.id)
            .order_by(OrganizationCreationRequest.created_at.desc(), OrganizationCreationRequest.id)
        ).all()
    )


def list_member_organizations(db: Session, user: User) -> list[OrganizationMembership]:
    return list(
        db.scalars(
            select(OrganizationMembership)
            .options(joinedload(OrganizationMembership.organization))
            .where(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.status == "active",
            )
            .order_by(OrganizationMembership.joined_at.desc())
        ).unique().all()
    )


def list_pending_invitations(db: Session, user: User) -> list[OrganizationInvitation]:
    now = datetime.now(timezone.utc)
    expired = db.scalars(
        select(OrganizationInvitation).where(
            func.lower(OrganizationInvitation.email) == user.email.casefold(),
            OrganizationInvitation.status == "pending",
            OrganizationInvitation.expires_at <= now,
        )
    ).all()
    for invitation in expired:
        invitation.status = "expired"
    if expired:
        db.commit()
    return list(
        db.scalars(
            select(OrganizationInvitation)
            .options(joinedload(OrganizationInvitation.organization))
            .where(
                func.lower(OrganizationInvitation.email) == user.email.casefold(),
                OrganizationInvitation.status == "pending",
                OrganizationInvitation.expires_at > now,
            )
            .order_by(OrganizationInvitation.created_at.desc(), OrganizationInvitation.id)
        ).unique().all()
    )


def invite_organization_member(
    db: Session,
    inviter: User,
    organization_id: str,
    email: str,
    role: str,
) -> OrganizationInvitation:
    membership = get_active_organization_membership(db, organization_id, inviter.id)
    if membership is None or membership.role not in {"owner", "admin"}:
        raise OrganizationAccessDenied("Organization owner or admin access required")
    if role == "admin" and membership.role != "owner":
        raise OrganizationAccessDenied("Only the organization owner can invite admins")

    normalized_email = email.strip().casefold()
    invitee = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
    if invitee and get_active_organization_membership(db, organization_id, invitee.id):
        raise OrganizationConflict("User is already an organization member")
    existing_invitation = db.scalar(
        select(OrganizationInvitation.id).where(
            OrganizationInvitation.organization_id == organization_id,
            func.lower(OrganizationInvitation.email) == normalized_email,
            OrganizationInvitation.status == "pending",
            OrganizationInvitation.expires_at > datetime.now(timezone.utc),
        )
    )
    if existing_invitation:
        raise OrganizationConflict("An active invitation already exists for this email")

    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=normalized_email,
        role=role,
        inviter_id=inviter.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


def accept_organization_invitation(
    db: Session,
    user: User,
    invitation_id: str,
) -> OrganizationMembership:
    invitation = db.scalar(
        select(OrganizationInvitation)
        .where(OrganizationInvitation.id == invitation_id)
        .with_for_update()
    )
    if invitation is None:
        raise OrganizationNotFound("Invitation not found")
    if invitation.email.casefold() != user.email.casefold():
        raise OrganizationAccessDenied("Invitation is addressed to another account")
    if invitation.status != "pending":
        raise OrganizationConflict("Invitation is no longer pending")
    if _is_expired(invitation.expires_at):
        invitation.status = "expired"
        db.commit()
        raise OrganizationConflict("Invitation has expired")
    if get_active_organization_membership(db, invitation.organization_id, user.id):
        raise OrganizationConflict("User is already an organization member")

    membership = OrganizationMembership(
        organization_id=invitation.organization_id,
        user_id=user.id,
        role=invitation.role,
    )
    invitation.status = "accepted"
    db.add(membership)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise OrganizationConflict("Organization membership already exists") from exc
    db.refresh(membership)
    return membership


def decline_organization_invitation(db: Session, user: User, invitation_id: str) -> None:
    invitation = db.scalar(
        select(OrganizationInvitation)
        .where(OrganizationInvitation.id == invitation_id)
        .with_for_update()
    )
    if invitation is None:
        raise OrganizationNotFound("Invitation not found")
    if invitation.email.casefold() != user.email.casefold():
        raise OrganizationAccessDenied("Invitation is addressed to another account")
    if invitation.status != "pending":
        raise OrganizationConflict("Invitation is no longer pending")
    invitation.status = "declined"
    db.commit()


def list_organization_members(
    db: Session,
    user: User,
    organization_id: str,
) -> list[OrganizationMembership]:
    if get_active_organization_membership(db, organization_id, user.id) is None:
        raise OrganizationAccessDenied("Organization membership required")
    return list(
        db.scalars(
            select(OrganizationMembership)
            .options(joinedload(OrganizationMembership.user))
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.status == "active",
            )
            .order_by(OrganizationMembership.joined_at, OrganizationMembership.id)
        ).unique().all()
    )


def organization_invitation_response(invitation: OrganizationInvitation) -> dict[str, object]:
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "organization_name": invitation.organization.name,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "expires_at": invitation.expires_at,
    }


def organization_summary(membership: OrganizationMembership) -> dict[str, object]:
    organization = membership.organization
    return {
        "id": organization.id,
        "slug": organization.slug,
        "name": organization.name,
        "description": organization.description,
        "website": organization.website,
        "verification_status": organization.verification_status,
        "role": membership.role,
    }
