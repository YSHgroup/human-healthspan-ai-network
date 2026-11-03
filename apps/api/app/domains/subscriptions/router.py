from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.domains.organizations.service import MANAGE_ROLES, require_member
from app.domains.subscriptions.service import FEATURE_CATALOG, list_entitlements, subscription_features
from app.models.domain import User
from app.models.platform import Purchase, SubscriptionPlan
from app.schemas.platform import EntitlementOut, PlanOut, PurchaseCreate, PurchaseOut
from app.services.audit import record_audit_event

router = APIRouter(tags=["entitlements"])

# Placeholder price list in cents; real pricing belongs to the (not yet integrated) payment provider.
LIST_PRICE_CENTS = {"organization.create": 0, "event.create": 0, "organization.badge": 0, "organization.ai": 0}


@router.get("/features")
def feature_catalog() -> list[dict]:
    return [{"feature": key, "label": value["label"], "countable": value["countable"], "subject": value["subject"]} for key, value in FEATURE_CATALOG.items()]


@router.get("/plans", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)) -> list[SubscriptionPlan]:
    return list(db.scalars(select(SubscriptionPlan).where(SubscriptionPlan.is_active.is_(True)).order_by(SubscriptionPlan.name)))


@router.get("/entitlements")
def my_entitlements(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return {
        "subscription_features": sorted(subscription_features(db, user.id)),
        "entitlements": [EntitlementOut.model_validate(item) for item in list_entitlements(db, "user", user.id)],
    }


@router.post("/purchases", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
def request_purchase(
    payload: PurchaseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Purchase:
    """Create a pending purchase. No payment processor is integrated: an administrator confirms payment."""
    if FEATURE_CATALOG[payload.feature]["subject"] == "organization":
        if payload.organization_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="organization_id is required for this feature.")
        require_member(db, user, payload.organization_id, MANAGE_ROLES)
    elif payload.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This feature is purchased for a user, not an organization.")
    purchase = Purchase(
        user_id=user.id,
        organization_id=payload.organization_id,
        feature=payload.feature,
        quantity=payload.quantity,
        amount_cents=LIST_PRICE_CENTS[payload.feature] * payload.quantity,
    )
    db.add(purchase)
    db.flush()
    record_audit_event(db, user.id, "purchase.requested", "purchase", purchase.id, {"feature": payload.feature})
    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/purchases", response_model=list[PurchaseOut])
def my_purchases(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Purchase]:
    return list(db.scalars(select(Purchase).where(Purchase.user_id == user.id).order_by(Purchase.created_at.desc())))
