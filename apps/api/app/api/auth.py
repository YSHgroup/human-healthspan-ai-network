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
    ProfileOut,
    RefreshRequest,
    RegistrationOut,
    RegisterRequest,
    TokenPair,
    UserOut,
    UserProfileUpdate,
)
from app.services.security import (
    create_access_token,
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
    email = str(payload.email).strip().lower()
    existing = db.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    profile = Profile(user_id=user.id, display_name=payload.display_name.strip())
    db.add(profile)
    try:
        tokens = create_session_tokens(user, db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.") from None
    db.refresh(user)
    db.refresh(profile)
    return RegistrationOut(user=build_user_out(user, profile), tokens=TokenPair(**tokens))


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    tokens = create_session_tokens(user, db)
    db.commit()
    return TokenPair(**tokens)


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

    access_expiry = utc_now() + timedelta(minutes=settings.access_token_minutes)
    return TokenPair(
        access_token=create_access_token(user, auth_session.id, access_expiry),
        refresh_token=token,
        expires_in=int((access_expiry - utc_now()).total_seconds()),
    )


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
