"""Shared persistence helper for platform-administrator decisions."""

from sqlalchemy.orm import Session

from app.models import AdminAuditEvent, User


def record_admin_action(
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
