from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.domain import Profile, User
from app.models.platform import Badge, ProfessionalRecord, UserBadge, WorkHistoryEntry
from app.db.base import utc_now
from app.schemas.platform import (
    BadgeOut,
    ProfessionalRecordCreate,
    ProfessionalRecordOut,
    ProfessionalRecordUpdate,
    PublicProfileOut,
    WorkHistoryAmend,
    WorkHistoryOut,
)
from app.services.audit import record_audit_event

professional_router = APIRouter(tags=["professional"])
profile_router = APIRouter(tags=["profiles"])


def record_out(record: ProfessionalRecord) -> ProfessionalRecordOut:
    out = ProfessionalRecordOut.model_validate(record)
    out.verification_color = "green" if record.verification_status == "verified" else "yellow"
    return out


def user_badges(db: Session, user_id: UUID) -> list[Badge]:
    return list(
        db.scalars(
            select(Badge)
            .join(UserBadge, UserBadge.badge_id == Badge.id)
            .where(UserBadge.user_id == user_id, Badge.is_active.is_(True))
            .order_by(UserBadge.awarded_at.desc())
        )
    )


def _own_record_or_404(db: Session, user: User, record_id: UUID) -> ProfessionalRecord:
    record = db.get(ProfessionalRecord, record_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional record not found.")
    return record


@professional_router.post("", response_model=ProfessionalRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: ProfessionalRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalRecordOut:
    record = ProfessionalRecord(user_id=user.id, **payload.model_dump())  # always starts unverified
    db.add(record)
    db.flush()
    record_audit_event(db, user.id, "professional.created", "professional_record", record.id)
    db.commit()
    db.refresh(record)
    return record_out(record)


@professional_router.get("", response_model=list[ProfessionalRecordOut])
def list_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProfessionalRecordOut]:
    records = db.scalars(
        select(ProfessionalRecord)
        .where(ProfessionalRecord.user_id == user.id)
        .order_by(ProfessionalRecord.start_year.desc().nulls_last(), ProfessionalRecord.created_at.desc())
    )
    return [record_out(record) for record in records]


@professional_router.patch("/{record_id}", response_model=ProfessionalRecordOut)
def update_record(
    record_id: UUID,
    payload: ProfessionalRecordUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalRecordOut:
    record = _own_record_or_404(db, user, record_id)
    changes = {key: value for key, value in payload.model_dump(exclude_unset=True).items() if value is not None}
    substantive = set(changes) - {"is_public"}
    for field, value in changes.items():
        setattr(record, field, value)
    if substantive and record.verification_status == "verified":
        # Editing verified facts invalidates the verification; it must be re-verified.
        record.verification_status = "unverified"
        record.verified_by = None
        record.verified_by_organization_id = None
        record.verified_at = None
    record_audit_event(db, user.id, "professional.updated", "professional_record", record.id)
    db.commit()
    db.refresh(record)
    return record_out(record)


@professional_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    record = _own_record_or_404(db, user, record_id)
    db.delete(record)
    record_audit_event(db, user.id, "professional.deleted", "professional_record", record.id)
    db.commit()


@professional_router.get("/work-history/entries", response_model=list[WorkHistoryOut])
def my_work_history(
    include_superseded: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkHistoryEntry]:
    query = select(WorkHistoryEntry).where(WorkHistoryEntry.user_id == user.id)
    if not include_superseded:
        superseded = select(WorkHistoryEntry.supersedes_id).where(WorkHistoryEntry.supersedes_id.is_not(None))
        query = query.where(WorkHistoryEntry.id.not_in(superseded))
    return list(db.scalars(query.order_by(WorkHistoryEntry.created_at.desc()).limit(limit)))


@professional_router.post(
    "/work-history/entries/{entry_id}/amend", response_model=WorkHistoryOut, status_code=status.HTTP_201_CREATED
)
def amend_work_history(
    entry_id: UUID,
    payload: WorkHistoryAmend,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkHistoryEntry:
    """Work history is append-only: a correction is a new, unverified entry that supersedes the old one."""
    original = db.get(WorkHistoryEntry, entry_id)
    if original is None or original.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work history entry not found.")
    already = db.scalar(select(WorkHistoryEntry.id).where(WorkHistoryEntry.supersedes_id == original.id))
    if already is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This entry has already been amended.")
    amendment = WorkHistoryEntry(
        user_id=user.id,
        organization_id=original.organization_id,
        project_id=original.project_id,
        task_id=original.task_id,
        kind=original.kind,
        summary=payload.summary,
        verification_status="unverified",
        supersedes_id=original.id,
        created_at=utc_now(),
    )
    db.add(amendment)
    db.flush()
    record_audit_event(db, user.id, "work_history.amended", "work_history", amendment.id, {"supersedes": str(original.id)})
    db.commit()
    db.refresh(amendment)
    return amendment


@profile_router.get("/me/badges", response_model=list[BadgeOut])
def my_badges(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Badge]:
    return user_badges(db, user.id)


@profile_router.get("/profile/{user_id}", response_model=PublicProfileOut)
def public_profile(user_id: UUID, db: Session = Depends(get_db)) -> PublicProfileOut:
    """Public professional view: only public profiles, public records, and active badges."""
    user = db.get(User, user_id)
    profile = db.scalar(select(Profile).where(Profile.user_id == user_id))
    if user is None or profile is None or not user.is_active or not profile.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    records = db.scalars(
        select(ProfessionalRecord)
        .where(ProfessionalRecord.user_id == user_id, ProfessionalRecord.is_public.is_(True))
        .order_by(ProfessionalRecord.start_year.desc().nulls_last())
    )
    return PublicProfileOut(
        id=user.id,
        role=user.role,
        display_name=profile.display_name,
        bio=profile.bio,
        expertise=list(profile.expertise or []),
        badges=[BadgeOut.model_validate(badge) for badge in user_badges(db, user_id)],
        professional_records=[record_out(record) for record in records],
    )
