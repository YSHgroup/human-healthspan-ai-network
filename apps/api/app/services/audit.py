from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models.domain import AuditEvent


def record_audit_event(
    db: Session,
    actor_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: UUID | str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details or {},
            created_at=utc_now(),
        )
    )
