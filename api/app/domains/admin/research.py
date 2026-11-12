"""Administrative verification, researcher admission, organization, and entitlement workflows."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import Integer, and_, case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.domains.admin.audit import record_admin_action
from app.models import (
    AdminAuditEvent,
    AIInteraction,
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
    record_admin_action(
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
    record_admin_action(
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
    record_admin_action(
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
    record_admin_action(
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
    record_admin_action(
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


def summarize_ai_usage(db: Session, days: int) -> dict[str, object]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(
            AIInteraction.environment,
            AIInteraction.provider,
            AIInteraction.model,
            AIInteraction.pricing_source,
            AIInteraction.input_usd_per_million_tokens,
            AIInteraction.output_usd_per_million_tokens,
            func.count(AIInteraction.id).label("total_interactions"),
            func.sum(AIInteraction.succeeded.cast(Integer)).label("succeeded"),
            func.sum((~AIInteraction.succeeded).cast(Integer)).label("failed"),
            func.sum(AIInteraction.input_characters).label("input_characters"),
            func.sum(AIInteraction.output_characters).label("output_characters"),
            func.sum(AIInteraction.input_tokens).label("input_tokens"),
            func.sum(AIInteraction.output_tokens).label("output_tokens"),
            func.count(AIInteraction.estimated_cost_usd).label("priced_interactions"),
            func.sum(
                case(
                    (
                        and_(
                            AIInteraction.succeeded.is_(True),
                            AIInteraction.estimated_cost_usd.is_(None),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("unpriced_successful_interactions"),
            func.sum(AIInteraction.estimated_cost_usd).label("estimated_cost_usd"),
            func.avg(AIInteraction.latency_ms).label("average_latency_ms"),
        )
        .where(AIInteraction.created_at >= since)
        .group_by(
            AIInteraction.environment,
            AIInteraction.provider,
            AIInteraction.model,
            AIInteraction.pricing_source,
            AIInteraction.input_usd_per_million_tokens,
            AIInteraction.output_usd_per_million_tokens,
        )
        .order_by(
            AIInteraction.environment,
            AIInteraction.provider,
            AIInteraction.model,
            AIInteraction.pricing_source,
            AIInteraction.input_usd_per_million_tokens,
            AIInteraction.output_usd_per_million_tokens,
        )
    ).all()
    groups = [
        {
            "environment": row.environment,
            "provider": row.provider,
            "model": row.model,
            "pricing_source": row.pricing_source,
            "input_usd_per_million_tokens": row.input_usd_per_million_tokens,
            "output_usd_per_million_tokens": row.output_usd_per_million_tokens,
            "total_interactions": int(row.total_interactions),
            "succeeded": int(row.succeeded or 0),
            "failed": int(row.failed or 0),
            "input_characters": int(row.input_characters or 0),
            "output_characters": int(row.output_characters or 0),
            "input_tokens": int(row.input_tokens or 0),
            "output_tokens": int(row.output_tokens or 0),
            "priced_interactions": int(row.priced_interactions or 0),
            "unpriced_successful_interactions": int(row.unpriced_successful_interactions or 0),
            "estimated_cost_usd": row.estimated_cost_usd,
            "average_latency_ms": float(row.average_latency_ms or 0),
        }
        for row in rows
    ]
    priced_interactions = sum(group["priced_interactions"] for group in groups)
    estimated_cost = (
        sum(
            (group["estimated_cost_usd"] or Decimal(0) for group in groups),
            Decimal(0),
        )
        if priced_interactions
        else None
    )
    return {
        "days": days,
        "total_interactions": sum(group["total_interactions"] for group in groups),
        "succeeded": sum(group["succeeded"] for group in groups),
        "failed": sum(group["failed"] for group in groups),
        "input_characters": sum(group["input_characters"] for group in groups),
        "output_characters": sum(group["output_characters"] for group in groups),
        "input_tokens": sum(group["input_tokens"] for group in groups),
        "output_tokens": sum(group["output_tokens"] for group in groups),
        "priced_interactions": priced_interactions,
        "unpriced_successful_interactions": sum(
            group["unpriced_successful_interactions"] for group in groups
        ),
        "estimated_cost_usd": estimated_cost,
        "groups": groups,
    }


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
    record_admin_action(
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
