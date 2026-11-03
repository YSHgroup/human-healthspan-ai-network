from datetime import timedelta
from statistics import mean
from typing import Annotated, Final
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.health.service import (
    new_link_token,
    records_for_share,
    share_by_token,
    share_is_active,
    user_may_use_share,
)
from app.domains.notifications.service import notify
from app.domains.organizations.service import RESEARCH_ROLES, organization_or_404
from app.models.domain import AuditEvent, User
from app.models.platform import ConsentRecord, HealthRecord, HealthShare, OrganizationMember
from app.schemas.platform import (
    ConsentOut,
    ConsentUpdate,
    HealthRecordCreate,
    HealthRecordOut,
    HealthRecordUpdate,
    HealthShareCreate,
    HealthShareCreated,
    HealthShareOut,
)
from app.services.audit import record_audit_event

CONSENT_PURPOSES: Final[tuple[str, ...]] = ("research_use", "ai_training", "interest_personalization")

records_router = APIRouter(tags=["health"])
sharing_router = APIRouter(tags=["health-sharing"])
consent_router = APIRouter(tags=["consent"])


def _own_record_or_404(db: Session, user: User, record_id: UUID) -> HealthRecord:
    record = db.get(HealthRecord, record_id)
    if record is None or record.user_id != user.id or record.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found.")
    return record


def _share_out(share: HealthShare) -> HealthShareOut:
    out = HealthShareOut.model_validate(share)
    out.is_link = share.token_hash is not None
    return out


# ------------------------------------------------------------------ records (owner only)
@records_router.post("/records", response_model=HealthRecordOut, status_code=status.HTTP_201_CREATED)
def create_health_record(
    payload: HealthRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthRecord:
    data = payload.model_dump()
    if data.get("recorded_at") is None:
        data["recorded_at"] = utc_now()
    record = HealthRecord(user_id=user.id, **data)
    db.add(record)
    db.flush()
    # Audit that something was written; never store health values in the audit log.
    record_audit_event(db, user.id, "health.record_created", "health_record", record.id, {"category": record.category})
    db.commit()
    db.refresh(record)
    return record


@records_router.get("/records", response_model=list[HealthRecordOut])
def list_health_records(
    category: str | None = Query(default=None, max_length=32),
    metric: str | None = Query(default=None, max_length=120),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[HealthRecord]:
    query = select(HealthRecord).where(HealthRecord.user_id == user.id, HealthRecord.deleted_at.is_(None))
    if category:
        query = query.where(HealthRecord.category == category)
    if metric:
        query = query.where(HealthRecord.metric == metric)
    return list(db.scalars(query.order_by(HealthRecord.recorded_at.desc()).limit(limit).offset(offset)))


@records_router.get("/records/{record_id}", response_model=HealthRecordOut)
def get_health_record(
    record_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> HealthRecord:
    return _own_record_or_404(db, user, record_id)


@records_router.patch("/records/{record_id}", response_model=HealthRecordOut)
def update_health_record(
    record_id: UUID,
    payload: HealthRecordUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthRecord:
    record = _own_record_or_404(db, user, record_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(record, field, value)
    record_audit_event(db, user.id, "health.record_updated", "health_record", record.id)
    db.commit()
    db.refresh(record)
    return record


@records_router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_record(
    record_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    record = _own_record_or_404(db, user, record_id)
    record.deleted_at = utc_now()
    record_audit_event(db, user.id, "health.record_deleted", "health_record", record.id)
    db.commit()


@records_router.get("/trends")
def health_trends(
    metric: Annotated[str, Query(min_length=1, max_length=120)],
    days: Annotated[int, Query(ge=1, le=3650)] = 90,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    since = utc_now() - timedelta(days=days)
    rows = list(
        db.scalars(
            select(HealthRecord)
            .where(
                HealthRecord.user_id == user.id,
                HealthRecord.deleted_at.is_(None),
                HealthRecord.metric == metric,
                HealthRecord.value_number.is_not(None),
                HealthRecord.recorded_at >= since,
            )
            .order_by(HealthRecord.recorded_at.asc())
        )
    )
    values = [row.value_number for row in rows if row.value_number is not None]
    return {
        "metric": metric,
        "unit": rows[-1].unit if rows else None,
        "points": [{"recorded_at": row.recorded_at, "value": row.value_number} for row in rows],
        "count": len(values),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "average": round(mean(values), 4) if values else None,
        "latest": values[-1] if values else None,
        "note": "Personal trend summary only; it is not a diagnosis or clinical interpretation.",
    }


@records_router.get("/access-log")
def health_access_log(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    events = db.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.resource_type == "health_records",
            AuditEvent.resource_id == str(user.id),
            or_(AuditEvent.action == "health.shared_read", AuditEvent.action == "health.link_read"),
        )
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "action": event.action,
            "accessor_id": str(event.actor_id) if event.actor_id else None,
            "share_id": event.details.get("share_id"),
            "record_count": event.details.get("record_count"),
            "created_at": event.created_at,
        }
        for event in events
    ]


# ------------------------------------------------------------------ sharing
@sharing_router.post("", response_model=HealthShareCreated, status_code=status.HTTP_201_CREATED)
def create_health_share(
    payload: HealthShareCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthShareCreated:
    if payload.grantee_user_id is not None:
        grantee = db.get(User, payload.grantee_user_id)
        if grantee is None or not grantee.is_active or grantee.id == user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grantee not found.")
    if payload.grantee_organization_id is not None:
        organization_or_404(db, payload.grantee_organization_id)
    token, token_hash = (None, None)
    if payload.create_link:
        token, token_hash = new_link_token()
    share = HealthShare(
        owner_id=user.id,
        grantee_user_id=payload.grantee_user_id,
        grantee_organization_id=payload.grantee_organization_id,
        token_hash=token_hash,
        categories=sorted(set(payload.categories)),
        label=payload.label,
        expires_at=utc_now() + timedelta(hours=payload.expires_in_hours) if payload.expires_in_hours else None,
    )
    db.add(share)
    db.flush()
    record_audit_event(
        db,
        user.id,
        "health.share_created",
        "health_share",
        share.id,
        {"categories": share.categories, "link": token is not None},
    )
    if payload.grantee_user_id is not None:
        notify(db, payload.grantee_user_id, "health.share_granted", "A member shared health data with you", None, "health_share", share.id, user.id)
    db.commit()
    db.refresh(share)
    created = HealthShareCreated.model_validate(share)
    created.is_link = token is not None
    created.link_token = token
    return created


@sharing_router.get("", response_model=list[HealthShareOut])
def list_my_shares(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[HealthShareOut]:
    shares = db.scalars(
        select(HealthShare).where(HealthShare.owner_id == user.id).order_by(HealthShare.created_at.desc())
    )
    return [_share_out(share) for share in shares]


@sharing_router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_share(share_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    share = db.get(HealthShare, share_id)
    if share is None or share.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found.")
    if share.revoked_at is None:
        share.revoked_at = utc_now()
        record_audit_event(db, user.id, "health.share_revoked", "health_share", share.id)
        db.commit()


@sharing_router.get("/received", response_model=list[HealthShareOut])
def received_shares(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[HealthShareOut]:
    org_ids = select(OrganizationMember.organization_id).where(
        OrganizationMember.user_id == user.id, OrganizationMember.role.in_(sorted(RESEARCH_ROLES))
    )
    shares = db.scalars(
        select(HealthShare)
        .where(
            HealthShare.token_hash.is_(None),
            or_(HealthShare.grantee_user_id == user.id, HealthShare.grantee_organization_id.in_(org_ids)),
        )
        .order_by(HealthShare.created_at.desc())
    )
    return [_share_out(share) for share in shares if share_is_active(share)]


@sharing_router.get("/received/{share_id}/records", response_model=list[HealthRecordOut])
def read_shared_records(
    share_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[HealthRecord]:
    share = db.get(HealthShare, share_id)
    if share is None or not user_may_use_share(db, user, share):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found.")
    records = records_for_share(db, share)
    record_audit_event(
        db,
        user.id,
        "health.shared_read",
        "health_records",
        share.owner_id,
        {"share_id": str(share.id), "record_count": len(records)},
    )
    db.commit()
    return records


@sharing_router.get("/links/{token}/records", response_model=list[HealthRecordOut])
def read_link_records(token: str, db: Session = Depends(get_db)) -> list[HealthRecord]:
    """Time-limited share link: the unguessable token is the credential, so no login is required."""
    share = share_by_token(db, token)
    if share is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found.")
    records = records_for_share(db, share)
    record_audit_event(
        db,
        None,
        "health.link_read",
        "health_records",
        share.owner_id,
        {"share_id": str(share.id), "record_count": len(records)},
    )
    db.commit()
    return records


# ------------------------------------------------------------------ consent
@consent_router.get("", response_model=list[ConsentOut])
def list_consents(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ConsentOut]:
    stored = {
        record.purpose: record
        for record in db.scalars(select(ConsentRecord).where(ConsentRecord.user_id == user.id))
    }
    return [
        ConsentOut(
            purpose=purpose,
            granted=bool(stored[purpose].granted) if purpose in stored else False,
            updated_at=stored[purpose].updated_at if purpose in stored else None,
        )
        for purpose in CONSENT_PURPOSES
    ]


@consent_router.post("/{purpose}", response_model=ConsentOut)
def update_consent(
    purpose: str,
    payload: ConsentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConsentOut:
    if purpose not in CONSENT_PURPOSES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown consent purpose.")
    record = db.scalar(
        select(ConsentRecord).where(ConsentRecord.user_id == user.id, ConsentRecord.purpose == purpose)
    )
    if record is None:
        record = ConsentRecord(user_id=user.id, purpose=purpose, granted=payload.granted)
        db.add(record)
    else:
        record.granted = payload.granted
    record.withdrawn_at = None if payload.granted else utc_now()
    record_audit_event(db, user.id, "consent.updated", "consent", user.id, {"purpose": purpose, "granted": payload.granted})
    db.commit()
    db.refresh(record)
    return ConsentOut(purpose=purpose, granted=record.granted, updated_at=record.updated_at)
