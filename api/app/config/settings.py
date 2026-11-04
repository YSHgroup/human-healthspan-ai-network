"""Environment-driven settings. Secrets are never committed; see `.env.example`."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        cors_origins=_split(os.environ.get("API_CORS_ORIGINS")),
    )
