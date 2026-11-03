"""Admin API (Architecture 7.2). Everything here is staff-only and audited; the admin portal
never gets broader database access than these endpoints."""
from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.providers import provider_status
from app.api.dependencies import require_roles
from app.core.config import settings
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.notifications.service import notify
from app.domains.professional.router import record_out
from app.domains.subscriptions.service import FEATURE_CATALOG, fulfil_purchase, grant_entitlement, subject_for_feature
from app.models.domain import AuditEvent, User
from app.models.platform import (
    AIFeedback,
    AIRun,
    Badge,
    Entitlement,
    Event,
    EventRegistration,
    Organization,
    OrganizationMember,
    ProfessionalRecord,
    Purchase,
    ResearchMembership,
    Subscription,
    SubscriptionPlan,
    UserBadge,
)
from app.schemas.platform import (
    AdminBadgeAward,
    BadgeCreate,
    BadgeOut,
    EntitlementGrant,
    EntitlementOut,
    EventModeration,
    EventOut,
    OrganizationActivation,
    OrganizationOut,
    OrganizationVerification,
    PaymentDecision,
    PlanCreate,
    PlanOut,
    ProfessionalRecordOut,
    ProfessionalVerification,
    PurchaseOut,
    ResearchMembershipDecision,
    ResearchMembershipOut,
    SubscriptionGrant,
    SubscriptionOut,
)
from app.services.audit import record_audit_event

router = APIRouter(tags=["admin"])

ADMIN = require_roles("admin")
STAFF_READ = require_roles("admin", "read_only_auditor", "support_operator")
AUDIT_READ = require_roles("admin", "read_only_auditor")
RESEARCH_REVIEW = require_roles("admin", "scientific_reviewer")


def _audited(db: Session, actor: User, action: str, resource_type: str, resource_id, reason: str, **details) -> None:
    record_audit_event(db, actor.id, action, resource_type, resource_id, {"reason": reason, **details})


# ------------------------------------------------------------------ organizations
@router.get("/organizations", response_model=list[OrganizationOut])
def admin_organizations(
    verification_status: str | None = Query(default=None, pattern="^(unverified|verified|rejected)$"),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[Organization]:
    query = select(Organization)
    if verification_status:
        query = query.where(Organization.verification_status == verification_status)
    return list(db.scalars(query.order_by(Organization.created_at.desc()).limit(limit)))


def _organization_or_404(db: Session, organization_id: UUID) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    return organization


@router.patch("/organizations/{organization_id}/verification", response_model=OrganizationOut)
def admin_verify_organization(
    organization_id: UUID,
    payload: OrganizationVerification,
    actor: User = Depends(ADMIN),
    db: Session = Depends(get_db),
) -> Organization:
    organization = _organization_or_404(db, organization_id)
    organization.verification_status = payload.verification_status
    _audited(db, actor, "admin.organization.verification", "organization", organization.id, payload.reason, status=payload.verification_status)
    db.commit()
    db.refresh(organization)
    return organization


@router.patch("/organizations/{organization_id}/activation", response_model=OrganizationOut)
def admin_activate_organization(
    organization_id: UUID,
    payload: OrganizationActivation,
    actor: User = Depends(ADMIN),
    db: Session = Depends(get_db),
) -> Organization:
    organization = _organization_or_404(db, organization_id)
    organization.is_active = payload.is_active
    _audited(db, actor, "admin.organization.activation", "organization", organization.id, payload.reason, is_active=payload.is_active)
    db.commit()
    db.refresh(organization)
    return organization


# ------------------------------------------------------------------ events
@router.get("/events", response_model=list[EventOut])
def admin_events(
    status_filter: Annotated[str | None, Query(alias="status", pattern="^(scheduled|cancelled|removed)$")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[EventOut]:
    query = select(Event)
    if status_filter:
        query = query.where(Event.status == status_filter)
    results = []
    for event in db.scalars(query.order_by(Event.starts_at.desc()).limit(limit)):
        out = EventOut.model_validate(event)
        out.registered_count = db.scalar(
            select(func.count()).select_from(EventRegistration).where(
                EventRegistration.event_id == event.id, EventRegistration.status == "registered"
            )
        ) or 0
        results.append(out)
    return results


@router.patch("/events/{event_id}/moderation", response_model=EventOut)
def admin_moderate_event(
    event_id: UUID,
    payload: EventModeration,
    actor: User = Depends(ADMIN),
    db: Session = Depends(get_db),
) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")
    event.status = payload.status
    if payload.status != "scheduled":
        notify(db, event.organizer_id, "event.moderated", f"Your event was set to {payload.status}", payload.reason[:200], "event", event.id)
    _audited(db, actor, "admin.event.moderation", "event", event.id, payload.reason, status=payload.status)
    db.commit()
    db.refresh(event)
    return event


# ------------------------------------------------------------------ plans, subscriptions, payments, entitlements
@router.get("/subscription-plans", response_model=list[PlanOut])
def admin_plans(_: User = Depends(STAFF_READ), db: Session = Depends(get_db)) -> list[SubscriptionPlan]:
    return list(db.scalars(select(SubscriptionPlan).order_by(SubscriptionPlan.created_at.desc())))


@router.post("/subscription-plans", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def admin_create_plan(payload: PlanCreate, actor: User = Depends(ADMIN), db: Session = Depends(get_db)) -> SubscriptionPlan:
    if db.scalar(select(SubscriptionPlan.id).where(SubscriptionPlan.slug == payload.slug)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A plan with this slug already exists.")
    plan = SubscriptionPlan(**payload.model_dump())
    db.add(plan)
    db.flush()
    record_audit_event(db, actor.id, "admin.plan.created", "subscription_plan", plan.id, {"slug": plan.slug})
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/subscriptions", response_model=list[SubscriptionOut])
def admin_subscriptions(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[Subscription]:
    return list(db.scalars(select(Subscription).order_by(Subscription.created_at.desc()).limit(limit)))


@router.post("/subscriptions", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def admin_grant_subscription(
    payload: SubscriptionGrant, actor: User = Depends(ADMIN), db: Session = Depends(get_db)
) -> Subscription:
    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.slug == payload.plan_slug, SubscriptionPlan.is_active.is_(True)))
    target = db.get(User, payload.user_id)
    if plan is None or target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan or user not found.")
    subscription = Subscription(
        user_id=target.id,
        plan_id=plan.id,
        status="active",
        current_period_end=utc_now() + timedelta(days=payload.period_days) if payload.period_days else None,
    )
    db.add(subscription)
    db.flush()
    _audited(db, actor, "admin.subscription.granted", "subscription", subscription.id, payload.reason, plan=plan.slug, user=str(target.id))
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/payments", response_model=list[PurchaseOut])
def admin_payments(
    status_filter: Annotated[str | None, Query(alias="status", pattern="^(pending|paid|cancelled|refunded)$")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[Purchase]:
    query = select(Purchase)
    if status_filter:
        query = query.where(Purchase.status == status_filter)
    return list(db.scalars(query.order_by(Purchase.created_at.desc()).limit(limit)))


@router.post("/payments/{purchase_id}/decision", response_model=PurchaseOut)
def admin_payment_decision(
    purchase_id: UUID,
    payload: PaymentDecision,
    actor: User = Depends(ADMIN),
    db: Session = Depends(get_db),
) -> Purchase:
    """Manual reconciliation until a payment provider is integrated. 'paid' creates the entitlement once."""
    purchase = db.get(Purchase, purchase_id)
    if purchase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found.")
    if purchase.status == payload.status:
        return purchase
    if payload.status == "paid":
        if purchase.status != "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending purchases can be marked paid.")
        entitlement = fulfil_purchase(db, purchase)
        notify(db, purchase.user_id, "purchase.paid", "Your purchase is active", purchase.feature, "purchase", purchase.id)
    elif payload.status == "refunded":
        if purchase.status != "paid":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only paid purchases can be refunded.")
        for entitlement in db.scalars(select(Entitlement).where(Entitlement.purchase_id == purchase.id)):
            entitlement.revoked_at = utc_now()
    elif purchase.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending purchases can be cancelled.")
    purchase.status = payload.status
    purchase.external_reference = payload.external_reference or purchase.external_reference
    _audited(db, actor, "admin.payment.decision", "purchase", purchase.id, payload.reason, status=payload.status)
    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/entitlements", response_model=list[EntitlementOut])
def admin_entitlements(
    subject_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[Entitlement]:
    query = select(Entitlement)
    if subject_id:
        query = query.where(Entitlement.subject_id == subject_id)
    return list(db.scalars(query.order_by(Entitlement.created_at.desc()).limit(limit)))


@router.post("/entitlements", response_model=EntitlementOut, status_code=status.HTTP_201_CREATED)
def admin_grant_entitlement(
    payload: EntitlementGrant, actor: User = Depends(ADMIN), db: Session = Depends(get_db)
) -> Entitlement:
    if payload.feature not in FEATURE_CATALOG:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown feature.")
    try:
        subject_type, subject_id = subject_for_feature(payload.feature, payload.user_id or actor.id, payload.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if subject_type == "user" and (payload.user_id is None or db.get(User, payload.user_id) is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if subject_type == "organization" and db.get(Organization, subject_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    entitlement = grant_entitlement(db, subject_type, subject_id, payload.feature, payload.quantity, "admin_grant", None, payload.expires_at)
    _audited(db, actor, "admin.entitlement.granted", "entitlement", entitlement.id, payload.reason, feature=payload.feature)
    db.commit()
    db.refresh(entitlement)
    return entitlement


@router.post("/entitlements/{entitlement_id}/revoke", response_model=EntitlementOut)
def admin_revoke_entitlement(
    entitlement_id: UUID, actor: User = Depends(ADMIN), db: Session = Depends(get_db)
) -> Entitlement:
    entitlement = db.get(Entitlement, entitlement_id)
    if entitlement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entitlement not found.")
    if entitlement.revoked_at is None:
        entitlement.revoked_at = utc_now()
        record_audit_event(db, actor.id, "admin.entitlement.revoked", "entitlement", entitlement.id)
        db.commit()
        db.refresh(entitlement)
    return entitlement


# ------------------------------------------------------------------ badges, certifications, verification
@router.get("/badges", response_model=list[BadgeOut])
def admin_badges(
    kind: str | None = Query(default=None, pattern="^(platform|certification|organization_contributor)$"),
    _: User = Depends(STAFF_READ),
    db: Session = Depends(get_db),
) -> list[Badge]:
    query = select(Badge)
    if kind:
        query = query.where(Badge.kind == kind)
    return list(db.scalars(query.order_by(Badge.created_at.desc()).limit(200)))


@router.get("/certifications", response_model=list[BadgeOut])
def admin_certifications(_: User = Depends(STAFF_READ), db: Session = Depends(get_db)) -> list[Badge]:
    return list(db.scalars(select(Badge).where(Badge.kind == "certification").order_by(Badge.created_at.desc())))


@router.post("/badges", response_model=BadgeOut, status_code=status.HTTP_201_CREATED)
def admin_create_badge(payload: BadgeCreate, actor: User = Depends(ADMIN), db: Session = Depends(get_db)) -> Badge:
    if db.scalar(select(Badge.id).where(Badge.slug == payload.slug)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A badge with this slug already exists.")
    badge = Badge(**payload.model_dump())
    db.add(badge)
    db.flush()
    record_audit_event(db, actor.id, "admin.badge.created", "badge", badge.id)
    db.commit()
    db.refresh(badge)
    return badge


@router.post("/badges/{badge_id}/award", status_code=status.HTTP_204_NO_CONTENT)
def admin_award_badge(
    badge_id: UUID, payload: AdminBadgeAward, actor: User = Depends(ADMIN), db: Session = Depends(get_db)
) -> None:
    badge = db.get(Badge, badge_id)
    if badge is None or not badge.is_active or badge.kind == "organization_contributor":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found.")
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if db.scalar(select(UserBadge.id).where(UserBadge.user_id == payload.user_id, UserBadge.badge_id == badge_id)) is None:
        db.add(UserBadge(user_id=payload.user_id, badge_id=badge_id, awarded_by=actor.id))
        notify(db, payload.user_id, "badge.awarded", f"You received the badge: {badge.name}", None, "badge", badge.id, actor.id)
        _audited(db, actor, "admin.badge.awarded", "badge", badge.id, payload.reason, user=str(payload.user_id))
        db.commit()


@router.post("/users/{user_id}/professional/{record_id}/verification", response_model=ProfessionalRecordOut)
def admin_verify_professional(
    user_id: UUID,
    record_id: UUID,
    payload: ProfessionalVerification,
    actor: User = Depends(ADMIN),
    db: Session = Depends(get_db),
) -> ProfessionalRecordOut:
    record = db.get(ProfessionalRecord, record_id)
    if record is None or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional record not found.")
    record.verification_status = payload.verification_status
    record.verified_by = actor.id if payload.verification_status == "verified" else None
    record.verified_by_organization_id = None
    record.verified_at = utc_now() if payload.verification_status == "verified" else None
    _audited(db, actor, "admin.professional.verification", "professional_record", record.id, payload.reason, status=payload.verification_status)
    db.commit()
    db.refresh(record)
    return record_out(record)


# ------------------------------------------------------------------ researcher access
@router.get("/research-memberships", response_model=list[ResearchMembershipOut])
def admin_research_memberships(
    status_filter: Annotated[str | None, Query(alias="status", pattern="^(pending|approved|rejected|revoked)$")] = "pending",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    _: User = Depends(RESEARCH_REVIEW),
    db: Session = Depends(get_db),
) -> list[ResearchMembership]:
    query = select(ResearchMembership)
    if status_filter:
        query = query.where(ResearchMembership.status == status_filter)
    return list(db.scalars(query.order_by(ResearchMembership.created_at.asc()).limit(limit)))


@router.post("/research-memberships/{user_id}/decision", response_model=ResearchMembershipOut)
def admin_research_membership_decision(
    user_id: UUID,
    payload: ResearchMembershipDecision,
    actor: User = Depends(RESEARCH_REVIEW),
    db: Session = Depends(get_db),
) -> ResearchMembership:
    record = db.scalar(select(ResearchMembership).where(ResearchMembership.user_id == user_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    new_status = {"approve": "approved", "reject": "rejected", "revoke": "revoked"}[payload.decision]
    if payload.decision == "revoke" and record.status != "approved":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved memberships can be revoked.")
    if payload.decision in {"approve", "reject"} and record.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending applications can be approved or rejected.")
    record.status, record.reviewed_by, record.reviewed_at, record.review_note = new_status, actor.id, utc_now(), payload.note
    notify(db, user_id, "research_membership.decision", f"Researcher application {new_status}", payload.note[:200], "research_membership", record.id, actor.id)
    _audited(db, actor, "admin.research_membership.decision", "research_membership", record.id, payload.note, status=new_status)
    db.commit()
    db.refresh(record)
    return record


# ------------------------------------------------------------------ AI monitoring, configuration, audit
@router.get("/ai-monitoring")
def admin_ai_monitoring(actor: User = Depends(AUDIT_READ), db: Session = Depends(get_db)) -> dict:
    by_system = db.execute(
        select(AIRun.system, AIRun.status, func.count(), func.avg(AIRun.latency_ms)).group_by(AIRun.system, AIRun.status)
    ).all()
    external = db.scalar(select(func.count()).select_from(AIRun).where(AIRun.external_provider_used.is_(True))) or 0
    feedback = dict(db.execute(select(AIFeedback.rating, func.count()).group_by(AIFeedback.rating)).all())
    fallbacks = db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.action == "ai.provider_fallback")) or 0
    total = sum(row[2] for row in by_system)
    record_audit_event(db, actor.id, "admin.ai_monitoring.read", "ai_monitoring")
    db.commit()
    return {
        "status": "ok",
        "provider": provider_status(),
        "total_runs": total,
        "external_provider_runs": external,
        "provider_fallbacks": fallbacks,
        "feedback": {"up": feedback.get("up", 0), "down": feedback.get("down", 0)},
        "by_system": [
            {"system": system, "status": run_status, "runs": count, "avg_latency_ms": round(float(avg or 0), 1)}
            for system, run_status, count, avg in by_system
        ],
        "note": "Prompts are not stored in AI runs or audit events; only system, sources, provider and timing are monitored.",
    }


@router.get("/configuration")
def admin_configuration(_: User = Depends(AUDIT_READ)) -> dict:
    """Read-only operational configuration. Secrets are never returned."""
    return {
        "environment": settings.app_env,
        "ai": provider_status(),
        "features": [{"feature": key, "label": value["label"]} for key, value in FEATURE_CATALOG.items()],
        "payments": {"provider": "manual", "note": "No payment processor is integrated; purchases are reconciled by administrators."},
    }


@router.get("/audit")
def admin_audit(
    action: str | None = Query(default=None, max_length=100),
    resource_type: str | None = Query(default=None, max_length=40),
    actor_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    actor: User = Depends(AUDIT_READ),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = select(AuditEvent)
    if action:
        query = query.where(AuditEvent.action.like(f"{action}%"))
    if resource_type:
        query = query.where(AuditEvent.resource_type == resource_type)
    if actor_id:
        query = query.where(AuditEvent.actor_id == actor_id)
    record_audit_event(db, actor.id, "admin.audit.read", "audit_event_collection", details={"limit": limit})
    db.commit()
    return [
        {
            "id": str(event.id),
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "details": event.details,
            "created_at": event.created_at,
        }
        for event in db.scalars(query.order_by(AuditEvent.created_at.desc()).limit(limit))
    ]


@router.get("/overview")
def admin_overview(_: User = Depends(STAFF_READ), db: Session = Depends(get_db)) -> dict:
    def count(model, *conditions) -> int:
        return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    return {
        "users": count(User),
        "organizations": count(Organization, Organization.is_active.is_(True)),
        "unverified_organizations": count(Organization, Organization.verification_status == "unverified"),
        "pending_researcher_applications": count(ResearchMembership, ResearchMembership.status == "pending"),
        "pending_purchases": count(Purchase, Purchase.status == "pending"),
        "scheduled_events": count(Event, Event.status == "scheduled"),
        "organization_memberships": count(OrganizationMember),
    }
