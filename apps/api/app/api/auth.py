from datetime import timedelta
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import bearer_scheme, get_current_user
from app.core.config import settings
from app.db.base import utc_now
from app.db.session import get_db
from app.models.domain import AuthSession, Profile, User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    ProfileOut,
    RefreshRequest,
    RegistrationOut,
    RegisterRequest,
    TokenPair,
    UserOut,
    UserProfileUpdate,
    VerificationRequest,
)
from app.services.audit import record_audit_event
from app.services.auth_tokens import consume_one_time_token, create_one_time_token
from app.services.email import EmailDeliveryError, email_delivery_configured, send_action_email
from app.services.security import (
    create_session_tokens,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["identity"])


def build_user_out(user: User, profile: Profile | None) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        profile=ProfileOut.model_validate(profile) if profile else None,
    )


@router.post("/register", response_model=RegistrationOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegistrationOut:
    if settings.app_env.lower() not in {"development", "dev", "test"} and not email_delivery_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verification delivery is not configured.",
        )
    email = str(payload.email).strip().lower()
    existing = db.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    try:
        user = User(email=email, password_hash=hash_password(payload.password))
        db.add(user)
        db.flush()
        profile = Profile(user_id=user.id, display_name=payload.display_name.strip())
        db.add(profile)
        verification_token = create_one_time_token(db, user, "verify_email", timedelta(hours=24))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.") from None
    db.refresh(user)
    db.refresh(profile)
    development_token = None
    if email_delivery_configured():
        try:
            send_action_email(email, "verify-email", verification_token)
        except EmailDeliveryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The account was created, but verification email delivery failed. Request a new email.",
            ) from exc
    elif settings.app_env.lower() in {"development", "dev", "test"}:
        development_token = verification_token
    return RegistrationOut(
        user=build_user_out(user, profile),
        verification_required=True,
        verification_token=development_token,
    )


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if (
        user is None
        or not user.is_active
        or not user.is_verified
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    tokens = create_session_tokens(user, db)
    db.commit()
    return TokenPair(**tokens)


@router.post("/verify-email")
def verify_email(payload: VerificationRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    token_record = consume_one_time_token(db, payload.token, "verify_email")
    if token_record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired.")
    user = db.get(User, token_record.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired.")
    user.is_verified = True
    record_audit_event(db, user.id, "auth.email_verified", "user", user.id)
    db.commit()
    return {"status": "verified"}


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> dict[str, str | None]:
    if settings.app_env.lower() not in {"development", "dev", "test"} and not email_delivery_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured.",
        )
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    development_token = None
    if user is not None and not user.is_verified:
        token = create_one_time_token(db, user, "verify_email", timedelta(hours=24))
        db.commit()
        if email_delivery_configured():
            try:
                send_action_email(email, "verify-email", token)
            except EmailDeliveryError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Verification email delivery failed.",
                ) from exc
        else:
            development_token = token
    return {"status": "accepted", "verification_token": development_token}


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    if settings.app_env.lower() not in {"development", "dev", "test"} and not email_delivery_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured.",
        )
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    development_token = None
    if user is not None:
        token = create_one_time_token(db, user, "password_reset", timedelta(hours=1))
        db.commit()
        if email_delivery_configured():
            try:
                send_action_email(email, "password-reset", token)
            except EmailDeliveryError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Password reset email delivery failed.",
                ) from exc
        else:
            development_token = token
    return {"status": "accepted", "reset_token": development_token}


@router.post("/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    token_record = consume_one_time_token(db, payload.token, "password_reset")
    if token_record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token is invalid or expired.")
    user = db.get(User, token_record.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token is invalid or expired.")
    user.password_hash = hash_password(payload.new_password)
    for session in db.scalars(
        select(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
    ):
        session.revoked_at = utc_now()
    record_audit_event(db, user.id, "auth.password_reset", "user", user.id)
    db.commit()
    return {"status": "password_updated"}


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    token = payload.refresh_token
    try:
        claims = decode_token(token, "refresh")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from None
    session_id = UUID(claims["sid"])
    auth_session = db.scalar(select(AuthSession).where(AuthSession.id == session_id))
    if auth_session is None or auth_session.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=utc_now().tzinfo)
    if expires_at <= utc_now() or str(auth_session.user_id) != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    user = db.get(User, auth_session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    auth_session.revoked_at = utc_now()
    tokens = create_session_tokens(user, db)
    record_audit_event(db, user.id, "auth.session_refreshed", "auth_session", auth_session.id)
    db.commit()
    return TokenPair(**tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
    claims = decode_token(credentials.credentials, "access")
    auth_session = db.get(AuthSession, UUID(claims["sid"]))
    if auth_session is not None and auth_session.user_id == user.id and auth_session.revoked_at is None:
        auth_session.revoked_at = utc_now()
        db.commit()


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    return build_user_out(user, profile)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return build_user_out(user, profile)
