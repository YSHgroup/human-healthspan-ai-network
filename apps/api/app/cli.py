import argparse
from getpass import getpass

from sqlalchemy import select

from app.db.base import utc_now
from app.db.session import SessionLocal, seed_communities
from app.models.domain import AuditEvent, Profile, User
from app.schemas.auth import RegisterRequest
from app.services.security import hash_password


def create_admin(email: str) -> None:
    password = getpass("Admin password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")
    payload = RegisterRequest(email=email, password=password, display_name="Platform Administrator")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    seed_communities()
    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
        if user is None:
            user = User(
                email=str(payload.email).lower(),
                password_hash=hash_password(password),
                role="admin",
                is_verified=True,
            )
            db.add(user)
            db.flush()
            db.add(Profile(user_id=user.id, display_name=payload.display_name))
        else:
            user.role = "admin"
            user.is_active = True
            user.is_verified = True
            if db.scalar(select(Profile.id).where(Profile.user_id == user.id)) is None:
                db.add(Profile(user_id=user.id, display_name=payload.display_name))
        db.add(
            AuditEvent(
                actor_id=None,
                action="admin.bootstrap",
                resource_type="user",
                resource_id=str(user.id),
                details={"email": user.email, "operator_initiated": True},
                created_at=utc_now(),
            )
        )
    print(f"Administrator role granted to {payload.email}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage local API administration.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    admin_parser = subparsers.add_parser("create-admin", help="Create or promote an administrator account.")
    admin_parser.add_argument("email")
    args = parser.parse_args()

    if args.command == "create-admin":
        create_admin(args.email)


if __name__ == "__main__":
    main()
