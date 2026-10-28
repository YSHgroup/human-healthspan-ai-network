import argparse
from getpass import getpass

from sqlalchemy import select

from app.db.session import SessionLocal, initialize_database
from app.models.domain import User
from app.schemas.auth import RegisterRequest
from app.services.security import hash_password


def create_admin(email: str) -> None:
    password = getpass("Admin password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")
    payload = RegisterRequest(email=email, password=password, display_name="Platform Administrator")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    initialize_database()
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
            from app.models.domain import Profile

            db.add(Profile(user_id=user.id, display_name=payload.display_name))
        else:
            user.role = "admin"
            user.is_verified = True
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
