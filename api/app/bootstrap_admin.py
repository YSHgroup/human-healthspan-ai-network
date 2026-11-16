"""Create the first allowlisted, email-verified platform administrator."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.user.auth import hash_password, normalize_email
from app.config import get_settings
from app.infrastructure.database import SessionLocal
from app.models import User
from app.schemas.identity import RegisterRequest


def bootstrap_initial_admin(
    db: Session,
    email: str,
    password: str,
    display_name: str,
    allowlisted_emails: tuple[str, ...],
) -> bool:
    email = normalize_email(email)
    display_name = display_name.strip()
    try:
        RegisterRequest(email=email, password=password, display_name=display_name)
    except ValidationError:
        raise ValueError(
            "Initial admin email, display name, or password is invalid. "
            "Use a valid email and a password between 12 and 128 characters."
        ) from None

    allowlist = {normalize_email(allowed) for allowed in allowlisted_emails}
    if email not in allowlist:
        raise ValueError("INITIAL_ADMIN_EMAIL must also be listed in PLATFORM_ADMIN_EMAILS.")

    user = db.scalar(select(User).where(User.email == email))
    if user is not None and user.email_verified_at is not None:
        return False

    now = datetime.now(timezone.utc)
    if user is None:
        user = User(
            email=email,
            display_name=display_name,
            password_hash=hash_password(password),
            email_verified_at=now,
        )
        db.add(user)
    else:
        user.display_name = display_name
        user.password_hash = hash_password(password)
        user.email_verified_at = now

    db.commit()
    return True


def main() -> None:
    email = os.environ.get("INITIAL_ADMIN_EMAIL", "").strip()
    password = os.environ.get("INITIAL_ADMIN_PASSWORD", "")
    display_name = os.environ.get("INITIAL_ADMIN_DISPLAY_NAME", "Platform Administrator").strip()
    if not email or not password:
        raise SystemExit(
            "Set INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PASSWORD in .env before bootstrapping."
        )

    settings = get_settings()
    try:
        with SessionLocal() as db:
            created = bootstrap_initial_admin(
                db,
                email,
                password,
                display_name,
                settings.platform_admin_emails,
            )
    except ValueError as exc:
        raise SystemExit(str(exc)) from None

    if created:
        print(f"Initial verified platform administrator provisioned for {normalize_email(email)}.")
    else:
        print(
            f"{normalize_email(email)} is already verified; existing account credentials were not changed."
        )


if __name__ == "__main__":
    main()
