"""Authenticated-user and browser-origin dependencies."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.infrastructure.database import get_db
from app.models import User, UserSession

settings = get_settings()


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def require_trusted_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is None or not any(
        hmac.compare_digest(origin.rstrip("/"), allowed) for allowed in settings.cors_origins
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Untrusted request origin")


def get_current_user(
    request: Request,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
    db: Session = Depends(get_db),
) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    now = datetime.now(timezone.utc)
    user_session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == token_digest(session_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
    )
    user = db.get(User, user_session.user_id) if user_session else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    request.state.user = user
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
