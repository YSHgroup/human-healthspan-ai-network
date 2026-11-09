"""Administrative verification, researcher admission, organization, and entitlement workflows."""

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AdminAuditEvent,
    Entitlement,
    Organization,
    OrganizationCreationRequest,
    OrganizationMembership,
    ResearchEvent,
    ResearcherApplication,
    User,
)


class ResearchAdminError(ValueError):
    pass


class AdminResourceNotFound(ResearchAdminError):
    pass


class AdminResourceConflict(ResearchAdminError):
    pass


def _record_admin_action(
    db: Session,
    actor: User,
    action: str,
    target_type: str,
    target_id: str,
    summary: str,
) -> None:
    db.add(
        AdminAuditEvent(
            actor_id=actor.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            summary=summary[:500],
        )
    )


def list_users(db: Session, limit: int) -> list[User]:
    return list(
        db.scalars(
            select(User).order_by(User.created_at.desc(), User.id).limit(limit)
        ).all()
    )


def set_user_verification(
    db: Session,
    actor: User,
    user_id: str,
    verified: bool,
) -> User:
    target = db.get(User, user_id)
    if target is None:
        raise AdminResourceNotFound("User not found")
    target.email_verified_at = datetime.now(timezone.utc) if verified else None
    _record_admin_action(
        db,
        actor,
        "user_verification_changed",
        "user",
        target.id,
        f"Email verification {'granted' if verified else 'revoked'} for {target.email}",
    )
    db.commit()
    db.refresh(target)
    return target


def list_pending_researcher_applications(db: Session) -> list[ResearcherApplication]:
    return list(
        db.scalars(
            select(ResearcherApplication)
            .options(joinedload(ResearcherApplication.applicant))
            .where(ResearcherApplication.status == "pending")
            .order_by(ResearcherApplication.created_at, ResearcherApplication.id)
        ).unique().all()
    )


def decide_researcher_application(
    db: Session,
    actor: User,
    application_id: str,
    decision: str,
) -> ResearcherApplication:
    application = db.scalar(
        select(ResearcherApplication)
        .options(joinedload(ResearcherApplication.applicant))
        .where(ResearcherApplication.id == application_id)
        .with_for_update()
    )
    if application is None:
        raise AdminResourceNotFound("Researcher application not found")
    if application.status != "pending":
        raise AdminResourceConflict("Researcher application has already been reviewed")
    if decision == "approve" and application.applicant.email_verified_at is None:
        raise AdminResourceConflict("Verify the account email before approving researcher access")

    reviewed_at = datetime.now(timezone.utc)
    application.status = "approved" if decision == "approve" else "rejected"
    application.reviewed_at = reviewed_at
    application.reviewed_by_id = actor.id
    if decision == "approve":
        application.applicant.researcher_approved_at = reviewed_at
    _record_admin_action(
        db,
        actor,
        "researcher_application_decided",
        "researcher_application",
        application.id,
        f"{decision.title()} researcher application for {application.applicant.email}",
    )
    db.commit()
    db.refresh(application)
    return application


def list_pending_organization_requests(db: Session) -> list[OrganizationCreationRequest]:
    return list(
        db.scalars(
            select(OrganizationCreationRequest)
            .options(joinedload(OrganizationCreationRequest.requester))
            .where(OrganizationCreationRequest.status == "pending")
            .order_by(OrganizationCreationRequest.created_at, OrganizationCreationRequest.id)
        ).unique().all()
    )


def has_active_entitlement(db: Session, user_id: str, key: str) -> bool:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(Entitlement.id).where(
            Entitlement.user_id == user_id,
            Entitlement.key == key,
            Entitlement.revoked_at.is_(None),
            or_(Entitlement.expires_at.is_(None), Entitlement.expires_at > now),
        )
    ) is not None


def decide_organization_request(
    db: Session,
    actor: User,
    request_id: str,
    decision: str,
) -> tuple[OrganizationCreationRequest, Organization | None]:
    creation_request = db.scalar(
        select(OrganizationCreationRequest)
        .options(joinedload(OrganizationCreationRequest.requester))
        .where(OrganizationCreationRequest.id == request_id)
        .with_for_update()
    )
    if creation_request is None:
        raise AdminResourceNotFound("Organization request not found")
    if creation_request.status != "pending":
        raise AdminResourceConflict("Organization request has already been reviewed")
    if decision == "approve" and not has_active_entitlement(
        db, creation_request.requester_id, "organization_create"
    ):
        raise AdminResourceConflict("An active organization-creation entitlement is required")
    if decision == "approve" and db.scalar(
        select(Organization.id).where(Organization.slug == creation_request.slug)
    ):
        raise AdminResourceConflict("Organization slug is already in use")

    reviewed_at = datetime.now(timezone.utc)
    organization = None
    if decision == "approve":
        organization = Organization(
            slug=creation_request.slug,
            name=creation_request.name,
            description=creation_request.description,
            website=creation_request.website,
            verification_status="verified",
            created_by_id=creation_request.requester_id,
            verified_at=reviewed_at,
            verified_by_id=actor.id,
        )
        db.add(organization)
        db.flush()
        db.add(
            OrganizationMembership(
                organization_id=organization.id,
                user_id=creation_request.requester_id,
                role="owner",
                status="active",
            )
        )
        creation_request.status = "approved"
    else:
        creation_request.status = "rejected"
    creation_request.reviewed_at = reviewed_at
    creation_request.reviewed_by_id = actor.id
    _record_admin_action(
        db,
        actor,
        "organization_request_decided",
        "organization_request",
        creation_request.id,
        f"{decision.title()} organization request for {creation_request.name}",
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AdminResourceConflict("Organization could not be provisioned") from exc
    db.refresh(creation_request)
    if organization is not None:
        db.refresh(organization)
    return creation_request, organization


def list_organizations(db: Session, limit: int) -> list[Organization]:
    return list(
        db.scalars(
            select(Organization)
            .order_by(Organization.created_at.desc(), Organization.id)
            .limit(limit)
        ).all()
    )


def list_user_entitlements(db: Session, user_id: str) -> list[Entitlement]:
    return list(
        db.scalars(
            select(Entitlement)
            .where(Entitlement.user_id == user_id)
            .order_by(Entitlement.granted_at.desc(), Entitlement.id)
        ).all()
    )


def grant_user_entitlement(
    db: Session,
    actor: User,
    user_id: str,
    key: str,
    expires_at: datetime | None,
) -> Entitlement:
    target = db.get(User, user_id)
    if target is None:
        raise AdminResourceNotFound("User not found")
    if key != "organization_create":
        raise AdminResourceConflict("Unsupported entitlement key")
    if expires_at is not None and (
        expires_at.tzinfo is None or expires_at <= datetime.now(timezone.utc)
    ):
        raise AdminResourceConflict("Entitlement expiry must be a future timezone-aware date")
    entitlement = Entitlement(
        user_id=target.id,
        key=key,
        granted_by_id=actor.id,
        expires_at=expires_at,
    )
    db.add(entitlement)
    db.flush()
    _record_admin_action(
        db,
        actor,
        "entitlement_granted",
        "entitlement",
        entitlement.id,
        f"Granted {key} to {target.email}",
    )
    db.commit()
    db.refresh(entitlement)
    return entitlement


def revoke_user_entitlement(
    db: Session,
    actor: User,
    entitlement_id: str,
) -> Entitlement:
    entitlement = db.get(Entitlement, entitlement_id)
    if entitlement is None:
        raise AdminResourceNotFound("Entitlement not found")
    if entitlement.revoked_at is not None:
        raise AdminResourceConflict("Entitlement has already been revoked")
    entitlement.revoked_at = datetime.now(timezone.utc)
    _record_admin_action(
        db,
        actor,
        "entitlement_revoked",
        "entitlement",
        entitlement.id,
        f"Revoked {entitlement.key} entitlement for {entitlement.user.email}",
    )
    db.commit()
    db.refresh(entitlement)
    return entitlement


def list_research_events(db: Session, limit: int) -> list[ResearchEvent]:
    return list(
        db.scalars(
            select(ResearchEvent)
            .options(joinedload(ResearchEvent.organization))
            .order_by(ResearchEvent.starts_at.desc(), ResearchEvent.id)
            .limit(limit)
        ).unique().all()
    )


def cancel_research_event(
    db: Session,
    actor: User,
    event_id: str,
) -> ResearchEvent:
    event = db.get(ResearchEvent, event_id)
    if event is None:
        raise AdminResourceNotFound("Research event not found")
    if event.status == "cancelled":
        raise AdminResourceConflict("Research event is already cancelled")
    event.status = "cancelled"
    _record_admin_action(
        db,
        actor,
        "research_event_cancelled",
        "research_event",
        event.id,
        f"Cancelled research event {event.title}",
    )
    db.commit()
    db.refresh(event)
    return event


def list_admin_audit_events(db: Session, limit: int) -> list[AdminAuditEvent]:
    return list(
        db.scalars(
            select(AdminAuditEvent)
            .options(joinedload(AdminAuditEvent.actor))
            .order_by(AdminAuditEvent.created_at.desc(), AdminAuditEvent.id)
            .limit(limit)
        ).unique().all()
    )
