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


@dataclass(frozen=True)
class Settings:
    app_env: str
    cors_origins: tuple[str, ...]
    platform_admin_emails: tuple[str, ...]
    database_url: str
    session_ttl_days: int
    session_cookie_name: str
    ai_provider: str
    ai_api_key: str | None
    ai_model: str | None
    ai_base_url: str | None
    ai_timeout_seconds: float
    scientist_enabled: bool
    research_file_storage_path: Path


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        cors_origins=_split(os.environ.get("API_CORS_ORIGINS")),
        platform_admin_emails=tuple(
            email.strip().casefold()
            for email in os.environ.get("PLATFORM_ADMIN_EMAILS", "").split(",")
            if email.strip()
        ),
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./healthspan.db"),
        session_ttl_days=int(os.environ.get("SESSION_TTL_DAYS", "30")),
        session_cookie_name=os.environ.get("SESSION_COOKIE_NAME", "healthspan_session"),
        ai_provider=os.environ.get("AI_PROVIDER", "disabled").strip().lower(),
        ai_api_key=os.environ.get("AI_API_KEY") or None,
        ai_model=os.environ.get("AI_MODEL") or None,
        ai_base_url=os.environ.get("AI_BASE_URL") or None,
        ai_timeout_seconds=float(os.environ.get("AI_TIMEOUT_SECONDS", "45")),
        scientist_enabled=os.environ.get("SCIENTIST_ENABLED", "false").lower() == "true",
        research_file_storage_path=Path(
            os.environ.get(
                "RESEARCH_FILE_STORAGE_PATH",
                str(Path(__file__).resolve().parents[3] / ".data" / "research-files"),
            )
        ).resolve(),
    )
