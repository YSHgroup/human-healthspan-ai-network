from uuid import UUID

from sqlalchemy.orm import Session

from app.models.platform import Notification


def notify(
    db: Session,
    user_id: UUID,
    kind: str,
    title: str,
    body: str | None = None,
    resource_type: str | None = None,
    resource_id: UUID | str | None = None,
    actor_id: UUID | None = None,
) -> None:
    """Queue an in-app notification. Callers commit; members are never notified about themselves."""
    if actor_id is not None and actor_id == user_id:
        return
    db.add(
        Notification(
            user_id=user_id,
            kind=kind,
            title=title[:200],
            body=body[:500] if body else None,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
        )
    )
