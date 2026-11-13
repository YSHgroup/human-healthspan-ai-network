"""Database-backed fixed-window limits for sensitive API routes."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import case, delete
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.config import get_settings
from app.config.settings import Settings
from app.infrastructure.database import get_db
from app.models import RateLimitBucket

RateLimitCategory = Literal["register", "login", "ai_chat"]
WINDOW_SECONDS: dict[RateLimitCategory, int] = {
    "register": 60 * 60,
    "login": 15 * 60,
    "ai_chat": 60,
}


def _configured_limit(category: RateLimitCategory, settings: Settings) -> int:
    if category == "register":
        return settings.auth_register_rate_limit
    if category == "login":
        return settings.auth_login_rate_limit
    return settings.ai_chat_rate_limit


def rate_limit(category: RateLimitCategory):
    def consume(db: Session, key_material: str, limit: int) -> None:
        settings = get_settings()
        window_seconds = WINDOW_SECONDS[category]
        now = datetime.now(timezone.utc)
        window_start = datetime.fromtimestamp(
            int(now.timestamp()) // window_seconds * window_seconds,
            tz=timezone.utc,
        )
        bucket_id = hmac.new(
            settings.rate_limit_hash_key.encode("utf-8"),
            f"{category}:{key_material}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        dialect_name = db.get_bind().dialect.name
        if dialect_name == "sqlite":
            insert = sqlite_insert
        elif dialect_name == "postgresql":
            insert = postgresql_insert
        else:
            raise RuntimeError(f"Unsupported database for rate limiting: {dialect_name}")

        statement = insert(RateLimitBucket).values(
            id=bucket_id,
            window_started_at=window_start,
            request_count=1,
        )
        statement = statement.on_conflict_do_update(
            index_elements=[RateLimitBucket.id],
            set_={
                "request_count": case(
                    (
                        RateLimitBucket.window_started_at == window_start,
                        RateLimitBucket.request_count + 1,
                    ),
                    else_=1,
                ),
                "window_started_at": window_start,
            },
        ).returning(RateLimitBucket.request_count)
        request_count = db.scalar(statement)
        if request_count is None:
            db.rollback()
            raise RuntimeError("Rate-limit counter did not return an updated request count")
        if request_count == 1:
            db.execute(
                delete(RateLimitBucket).where(
                    RateLimitBucket.window_started_at
                    < now - timedelta(seconds=max(WINDOW_SECONDS.values()))
                )
            )
        db.commit()

        if request_count > limit:
            retry_after = max(
                1,
                int((window_start + timedelta(seconds=window_seconds) - now).total_seconds()),
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests; try again after the rate limit window resets",
                headers={"Retry-After": str(retry_after)},
            )

    def client_peer(request: Request) -> str:
        require_trusted_origin(request)
        peer = request.client.host if request.client is not None else None
        if not peer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Request rate limiting is unavailable",
            )
        return peer

    if category == "ai_chat":

        async def enforce_authenticated_rate_limit(
            request: Request,
            user: CurrentUser,
            db: Session = Depends(get_db),
        ) -> None:
            client_peer(request)
            consume(db, f"user:{user.id}", _configured_limit(category, get_settings()))

        return enforce_authenticated_rate_limit

    async def enforce_ip_rate_limit(
        request: Request,
        db: Session = Depends(get_db),
    ) -> None:
        peer = client_peer(request)
        consume(db, f"peer:{peer}", _configured_limit(category, get_settings()))

    return enforce_ip_rate_limit
