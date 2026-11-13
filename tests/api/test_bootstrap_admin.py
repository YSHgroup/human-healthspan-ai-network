import pytest
from sqlalchemy import select

from app.api.v1.user.auth import verify_password
from app.bootstrap_admin import bootstrap_initial_admin
from app.models import User


def test_bootstrap_creates_verified_allowlisted_admin(api_client):
    session_factory = api_client.app.state.test_session_factory
    with session_factory() as db:
        created = bootstrap_initial_admin(
            db,
            "admin@example.test",
            "a-secure-initial-password",
            "Platform Administrator",
            ("admin@example.test",),
        )
        user = db.scalar(select(User).where(User.email == "admin@example.test"))

    assert created is True
    assert user is not None
    assert user.email_verified_at is not None
    assert verify_password("a-secure-initial-password", user.password_hash)


def test_bootstrap_does_not_reset_verified_account_password(api_client):
    session_factory = api_client.app.state.test_session_factory
    with session_factory() as db:
        bootstrap_initial_admin(
            db,
            "admin@example.test",
            "a-secure-initial-password",
            "Platform Administrator",
            ("admin@example.test",),
        )
        created = bootstrap_initial_admin(
            db,
            "admin@example.test",
            "a-different-initial-password",
            "Platform Administrator",
            ("admin@example.test",),
        )
        user = db.scalar(select(User).where(User.email == "admin@example.test"))

    assert created is False
    assert user is not None
    assert verify_password("a-secure-initial-password", user.password_hash)
    assert not verify_password("a-different-initial-password", user.password_hash)


def test_bootstrap_promotes_existing_unverified_account(api_client):
    session_factory = api_client.app.state.test_session_factory
    with session_factory() as db:
        db.add(
            User(
                email="admin@example.test",
                display_name="Unverified Admin",
                password_hash="old-password-hash",
            )
        )
        db.commit()

        created = bootstrap_initial_admin(
            db,
            "admin@example.test",
            "a-secure-initial-password",
            "Platform Administrator",
            ("admin@example.test",),
        )
        user = db.scalar(select(User).where(User.email == "admin@example.test"))

    assert created is True
    assert user is not None
    assert user.email_verified_at is not None
    assert verify_password("a-secure-initial-password", user.password_hash)


def test_bootstrap_rejects_email_not_in_platform_allowlist(api_client):
    session_factory = api_client.app.state.test_session_factory
    with session_factory() as db:
        with pytest.raises(ValueError, match="PLATFORM_ADMIN_EMAILS"):
            bootstrap_initial_admin(
                db,
                "admin@example.test",
                "a-secure-initial-password",
                "Platform Administrator",
                ("another-admin@example.test",),
            )

        assert db.scalar(select(User).where(User.email == "admin@example.test")) is None
