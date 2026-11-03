"""Centralized, backend-enforced entitlements (Architecture v1.2 section 12).

The frontend is never the authority for premium access. A feature is available when the
subject has an active subscription whose plan includes it, or an unexpired, unrevoked
entitlement with remaining quantity.
"""
from typing import Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.common import is_past
from app.models.platform import Entitlement, Purchase, Subscription, SubscriptionPlan

FEATURE_CATALOG: Final[dict[str, dict[str, object]]] = {
    "organization.create": {"label": "Create an organization", "countable": True, "subject": "user"},
    "event.create": {"label": "Create events", "countable": False, "subject": "user"},
    "organization.badge": {"label": "Additional organization contributor badge", "countable": True, "subject": "organization"},
    "organization.ai": {"label": "Organization AI instance", "countable": True, "subject": "organization"},
}


def feature_known(feature: str) -> bool:
    return feature in FEATURE_CATALOG


def subscription_features(db: Session, user_id: UUID) -> set[str]:
    rows = db.execute(
        select(Subscription, SubscriptionPlan)
        .join(SubscriptionPlan, SubscriptionPlan.id == Subscription.plan_id)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            SubscriptionPlan.is_active.is_(True),
        )
    ).all()
    features: set[str] = set()
    for subscription, plan in rows:
        if is_past(subscription.current_period_end):
            continue
        features.update(plan.features or [])
    return features


def _usable_entitlements(db: Session, subject_type: str, subject_id: UUID, feature: str) -> list[Entitlement]:
    rows = db.scalars(
        select(Entitlement)
        .where(
            Entitlement.subject_type == subject_type,
            Entitlement.subject_id == subject_id,
            Entitlement.feature == feature,
            Entitlement.revoked_at.is_(None),
        )
        .order_by(Entitlement.created_at.asc())
    )
    return [row for row in rows if not is_past(row.expires_at) and row.quantity_used < row.quantity_total]


def has_feature(db: Session, subject_type: str, subject_id: UUID, feature: str) -> bool:
    if subject_type == "user" and feature in subscription_features(db, subject_id):
        return True
    return bool(_usable_entitlements(db, subject_type, subject_id, feature))


def use_feature(db: Session, subject_type: str, subject_id: UUID, feature: str) -> bool:
    """Authorize use of a feature, consuming one unit for countable features. Caller commits."""
    if subject_type == "user" and feature in subscription_features(db, subject_id):
        return True
    usable = _usable_entitlements(db, subject_type, subject_id, feature)
    if not usable:
        return False
    if FEATURE_CATALOG.get(feature, {}).get("countable", False):
        usable[0].quantity_used += 1
    return True


def grant_entitlement(
    db: Session,
    subject_type: str,
    subject_id: UUID,
    feature: str,
    quantity: int = 1,
    source: str = "admin_grant",
    purchase_id: UUID | None = None,
    expires_at=None,
) -> Entitlement:
    entitlement = Entitlement(
        subject_type=subject_type,
        subject_id=subject_id,
        feature=feature,
        quantity_total=quantity,
        quantity_used=0,
        source=source,
        purchase_id=purchase_id,
        expires_at=expires_at,
    )
    db.add(entitlement)
    db.flush()
    return entitlement


def subject_for_feature(feature: str, user_id: UUID, organization_id: UUID | None) -> tuple[str, UUID]:
    if FEATURE_CATALOG[feature]["subject"] == "organization":
        if organization_id is None:
            raise ValueError("This feature is granted to an organization; provide organization_id.")
        return "organization", organization_id
    return "user", user_id


def fulfil_purchase(db: Session, purchase: Purchase) -> Entitlement:
    """Turn a paid purchase into an entitlement for the user or organization it was bought for."""
    subject_type, subject_id = subject_for_feature(purchase.feature, purchase.user_id, purchase.organization_id)
    return grant_entitlement(db, subject_type, subject_id, purchase.feature, purchase.quantity, "purchase", purchase.id)


def list_entitlements(db: Session, subject_type: str, subject_id: UUID) -> list[Entitlement]:
    return list(
        db.scalars(
            select(Entitlement)
            .where(Entitlement.subject_type == subject_type, Entitlement.subject_id == subject_id)
            .order_by(Entitlement.created_at.desc())
        )
    )
