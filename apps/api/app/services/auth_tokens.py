import hashlib
import secrets
from datetime import timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models.domain import AuthToken, User


def create_one_time_token(db: Session, user: User, purpose: str, lifetime: timedelta) -> str:
    now = utc_now()
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    previous_tokens = db.scalars(
        select(AuthToken).where(
            AuthToken.user_id == user.id,
            AuthToken.purpose == purpose,
            AuthToken.consumed_at.is_(None),
        )
    )
    for previous in previous_tokens:
        previous.consumed_at = now
    db.add(
        AuthToken(
            user_id=user.id,
            token_hash=digest,
            purpose=purpose,
            expires_at=now + lifetime,
            created_at=now,
        )
    )
    db.flush()
    return token


def consume_one_time_token(db: Session, token: str, purpose: str) -> AuthToken | None:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    record = db.scalar(
        select(AuthToken).where(
            AuthToken.token_hash == digest,
            AuthToken.purpose == purpose,
            AuthToken.consumed_at.is_(None),
        )
    )
    if record is None:
        return None
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= utc_now():
        return None
    record.consumed_at = utc_now()
    return record
