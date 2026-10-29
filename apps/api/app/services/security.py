from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import utc_now
from app.models.domain import AuthSession, User

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_session_tokens(user: User, db: Session) -> dict[str, str | int]:
    now = utc_now()
    session_expiry = now + timedelta(days=settings.refresh_token_days)
    auth_session = AuthSession(user_id=user.id, expires_at=session_expiry, created_at=now)
    db.add(auth_session)
    db.flush()
    access_expiry = now + timedelta(minutes=settings.access_token_minutes)
    access_token = create_access_token(user, auth_session.id, access_expiry, now)
    refresh_expiry = session_expiry
    refresh_token = jwt.encode(
        {
            "iss": settings.jwt_issuer,
            "sub": str(user.id),
            "sid": str(auth_session.id),
            "iat": now,
            "typ": "refresh",
            "exp": refresh_expiry,
        },
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int((access_expiry - now).total_seconds()),
        "refresh_expires_in": int((refresh_expiry - now).total_seconds()),
    }


def create_access_token(
    user: User,
    session_id: UUID,
    expires_at: datetime | None = None,
    now: datetime | None = None,
) -> str:
    issued_at = now or utc_now()
    access_expiry = expires_at or issued_at + timedelta(minutes=settings.access_token_minutes)
    shared = {
        "iss": settings.jwt_issuer,
        "sub": str(user.id),
        "sid": str(session_id),
        "iat": issued_at,
    }
    return jwt.encode(
        {**shared, "typ": "access", "exp": access_expiry},
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )


def decode_token(token: str, expected_type: str) -> dict:
    claims = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITHM],
        issuer=settings.jwt_issuer,
        options={"require": ["exp", "iat", "sub", "sid", "typ", "iss"]},
    )
    if claims["typ"] != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type.")
    UUID(claims["sub"])
    UUID(claims["sid"])
    return claims


def get_active_session(db: Session, session_id: UUID) -> AuthSession | None:
    auth_session = db.scalar(select(AuthSession).where(AuthSession.id == session_id))
    if auth_session is None or auth_session.revoked_at is not None:
        return None
    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= utc_now():
        return None
    return auth_session
