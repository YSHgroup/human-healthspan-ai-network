"""Personal health data access rules (Architecture 3.3.4, 3.3.5, 13.2).

Health data is private by default. It is readable only by its owner, or by a grantee holding an
active (unexpired, unrevoked) share that covers the record's category. Every non-owner read is audited.
Nothing in this module is imported by research, search or AI retrieval code, and tests assert that.
"""
import hashlib
import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.common import is_past
from app.domains.organizations.service import RESEARCH_ROLES, membership
from app.models.domain import User
from app.models.platform import HealthRecord, HealthShare


def hash_link_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_link_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_link_token(token)


def share_is_active(share: HealthShare) -> bool:
    return share.revoked_at is None and not is_past(share.expires_at)


def records_for_share(db: Session, share: HealthShare, limit: int = 200) -> list[HealthRecord]:
    return list(
        db.scalars(
            select(HealthRecord)
            .where(
                HealthRecord.user_id == share.owner_id,
                HealthRecord.deleted_at.is_(None),
                HealthRecord.category.in_(share.categories or []),
            )
            .order_by(HealthRecord.recorded_at.desc())
            .limit(limit)
        )
    )


def user_may_use_share(db: Session, user: User, share: HealthShare) -> bool:
    """Grantee check for user shares and organization shares (research-capable org roles only)."""
    if not share_is_active(share) or share.token_hash is not None:
        return False
    if share.grantee_user_id is not None:
        return share.grantee_user_id == user.id
    if share.grantee_organization_id is not None:
        member = membership(db, share.grantee_organization_id, user.id)
        return member is not None and member.role in RESEARCH_ROLES
    return False


def share_by_token(db: Session, token: str) -> HealthShare | None:
    share = db.scalar(select(HealthShare).where(HealthShare.token_hash == hash_link_token(token)))
    if share is None or not share_is_active(share):
        return None
    return share


def owner_id_of(share: HealthShare) -> UUID:
    return share.owner_id
