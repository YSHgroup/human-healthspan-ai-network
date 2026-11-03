from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.models.domain import User
from app.models.platform import Notification
from app.schemas.platform import NotificationOut

router = APIRouter(tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    offset: Annotated[int, Query(ge=0)] = 0,
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    return list(db.scalars(query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)))


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, int]:
    count = db.scalar(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == user.id, Notification.read_at.is_(None)
        )
    )
    return {"unread": count or 0}


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.read_at.is_(None))
        .values(read_at=utc_now())
    )
    db.commit()


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    if notification.read_at is None:
        notification.read_at = utc_now()
        db.commit()
        db.refresh(notification)
    return notification

