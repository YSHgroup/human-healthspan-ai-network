"""Environment-driven settings. Secrets are never committed; see `.env.example`."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
)


def _split(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_CORS_ORIGINS
    return tuple(item.strip().rstrip("/") for item in value.split(",") if item.strip())


def _positive_int(name: str, default: str) -> int:
    value = int(os.environ.get(name, default))
    if value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True)
class Settings:
    app_env: str
    cors_origins: tuple[str, ...]
    database_url: str
    session_ttl_days: int
    session_max_lifetime_days: int
    session_cookie_name: str
    ai_provider: str
    ai_api_key: str | None
    ai_model: str | None
    ai_base_url: str | None
    ai_timeout_seconds: float
    scientist_enabled: bool


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        cors_origins=_split(os.environ.get("API_CORS_ORIGINS")),
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./healthspan.db"),
        session_ttl_days=_positive_int("SESSION_TTL_DAYS", "14"),
        session_max_lifetime_days=_positive_int("SESSION_MAX_LIFETIME_DAYS", "60"),
        session_cookie_name=os.environ.get("SESSION_COOKIE_NAME", "healthspan_session"),
        ai_provider=os.environ.get("AI_PROVIDER", "disabled").strip().lower(),
        ai_api_key=os.environ.get("AI_API_KEY") or None,
        ai_model=os.environ.get("AI_MODEL") or None,
        ai_base_url=os.environ.get("AI_BASE_URL") or None,
        ai_timeout_seconds=float(os.environ.get("AI_TIMEOUT_SECONDS", "45")),
        scientist_enabled=os.environ.get("SCIENTIST_ENABLED", "false").lower() == "true",
    )
