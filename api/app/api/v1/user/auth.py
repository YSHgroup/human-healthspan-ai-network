"""Shared registration, session, and AI-learning-consent routes."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin, token_digest
from app.api.dependencies.rate_limit import rate_limit
from app.config import get_settings
from app.infrastructure.database import get_db
from app.models import AIConsent, AIInteraction, User, UserSession
from app.schemas.identity import AILearningConsentRequest, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["identity"])
settings = get_settings()
COOKIE_LIFETIME = timedelta(days=settings.session_ttl_days)
CONSENT_VERSION = "v1"
PASSWORD_SCRYPT_N = 2**14


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=PASSWORD_SCRYPT_N, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=PASSWORD_SCRYPT_N, r=8, p=1
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def current_consent(db: Session, user_id: str) -> AIConsent | None:
    return db.scalar(
        select(AIConsent)
        .where(AIConsent.user_id == user_id)
        .order_by(AIConsent.created_at.desc(), AIConsent.id.desc())
        .limit(1)
    )


def user_response(db: Session, user: User) -> UserResponse:
    consent = current_consent(db, user.id)
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        researcher_approved=user.researcher_approved_at is not None,
        ai_learning_consent=consent.allowed if consent else False,
    )


def create_session(db: Session, user: User, response: Response) -> None:
    token = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=token_digest(token),
            created_at=now,
            expires_at=now + COOKIE_LIFETIME,
        )
    )
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=int(COOKIE_LIFETIME.total_seconds()),
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        path="/",
    )


def normalize_email(email: str) -> str:
    return email.strip().casefold()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("register"))],
)
def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    require_trusted_origin(request)
    user = User(
        email=normalize_email(body.email),
        display_name=body.display_name.strip(),
        password_hash=hash_password(body.password),
    )
    if not user.display_name:
        raise HTTPException(status_code=422, detail="Display name cannot be blank")
    db.add(user)
    try:
        db.flush()
        create_session(db, user, response)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    db.refresh(user)
    return user_response(db, user)


@router.post(
    "/login",
    response_model=UserResponse,
    dependencies=[Depends(rate_limit("login"))],
)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    require_trusted_origin(request)
    user = db.scalar(select(User).where(User.email == normalize_email(body.email)))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    create_session(db, user, response)
    db.commit()
    return user_response(db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    require_trusted_origin(request)
    cookie_token = request.cookies.get(settings.session_cookie_name)
    if cookie_token:
        user_session = db.scalar(
            select(UserSession).where(UserSession.token_hash == token_digest(cookie_token))
        )
        if user_session is not None and user_session.revoked_at is None:
            user_session.revoked_at = datetime.now(timezone.utc)
            db.commit()
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.app_env == "production",
        httponly=True,
        samesite="lax",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser, db: Session = Depends(get_db)) -> UserResponse:
    return user_response(db, user)


@router.put("/ai-learning-consent", response_model=UserResponse)
def set_ai_learning_consent(
    body: AILearningConsentRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> UserResponse:
    require_trusted_origin(request)
    consent = AIConsent(user_id=user.id, allowed=body.allowed, version=CONSENT_VERSION)
    db.add(consent)
    if not body.allowed:
        db.query(AIInteraction).filter(AIInteraction.user_id == user.id).update(
            {"prompt_content": None, "response_content": None, "consent_id": None},
            synchronize_session=False,
        )
    db.commit()
    return user_response(db, user)
