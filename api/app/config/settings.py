"""Environment-driven settings. Secrets are never committed; see `.env.example`."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
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


def _positive_int(name: str, default: int) -> int:
    value = int(os.environ.get(name, str(default)))
    if not 1 <= value <= 100_000:
        raise ValueError(f"{name} must be between 1 and 100000")
    return value


@dataclass(frozen=True)
class AIModelPricing:
    input_usd_per_million_tokens: Decimal
    output_usd_per_million_tokens: Decimal


def _parse_ai_model_pricing(value: str) -> dict[str, AIModelPricing]:
    try:
        raw_pricing = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("AI_MODEL_PRICING_JSON must be valid JSON") from exc
    if not isinstance(raw_pricing, dict):
        raise ValueError("AI_MODEL_PRICING_JSON must be an object keyed by exact model name")

    pricing: dict[str, AIModelPricing] = {}
    for model, raw_rates in raw_pricing.items():
        if not isinstance(model, str) or not model.strip() or not isinstance(raw_rates, dict):
            raise ValueError("AI model pricing entries must map non-empty model names to rate objects")
        try:
            input_rate = Decimal(str(raw_rates["input_usd_per_million_tokens"]))
            output_rate = Decimal(str(raw_rates["output_usd_per_million_tokens"]))
        except (KeyError, InvalidOperation, ValueError) as exc:
            raise ValueError(
                f"AI pricing for {model!r} requires valid input and output USD rates"
            ) from exc
        if (
            not input_rate.is_finite()
            or not output_rate.is_finite()
            or input_rate < 0
            or output_rate < 0
            or input_rate > Decimal("1000000000")
            or output_rate > Decimal("1000000000")
        ):
            raise ValueError(
                f"AI pricing rates for {model!r} must be finite, non-negative and no greater than 1e9"
            )
        pricing[model.strip()] = AIModelPricing(
            input_usd_per_million_tokens=input_rate,
            output_usd_per_million_tokens=output_rate,
        )
    return pricing


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
    ai_model_pricing: dict[str, AIModelPricing]
    ai_pricing_source: str | None
    scientist_enabled: bool
    research_file_storage_path: Path
    auth_register_rate_limit: int
    auth_login_rate_limit: int
    ai_chat_rate_limit: int
    rate_limit_hash_key: str


@lru_cache
def get_settings() -> Settings:
    app_env = os.environ.get("APP_ENV", "development").strip().lower()
    pricing_source = os.environ.get("AI_PRICING_SOURCE", "").strip() or None
    if pricing_source is not None and len(pricing_source) > 256:
        raise ValueError("AI_PRICING_SOURCE must be no longer than 256 characters")
    rate_limit_hash_key = os.environ.get("RATE_LIMIT_HASH_KEY", "").strip()
    if app_env == "production" and len(rate_limit_hash_key) < 32:
        raise ValueError("RATE_LIMIT_HASH_KEY must be configured with at least 32 characters in production")
    if not rate_limit_hash_key:
        rate_limit_hash_key = "development-only-rate-limit-key"
    return Settings(
        app_env=app_env,
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
        ai_model_pricing=_parse_ai_model_pricing(os.environ.get("AI_MODEL_PRICING_JSON", "{}")),
        ai_pricing_source=pricing_source,
        scientist_enabled=os.environ.get("SCIENTIST_ENABLED", "false").lower() == "true",
        research_file_storage_path=Path(
            os.environ.get(
                "RESEARCH_FILE_STORAGE_PATH",
                str(Path(__file__).resolve().parents[3] / ".data" / "research-files"),
            )
        ).resolve(),
        auth_register_rate_limit=_positive_int("AUTH_REGISTER_RATE_LIMIT", 10),
        auth_login_rate_limit=_positive_int("AUTH_LOGIN_RATE_LIMIT", 30),
        ai_chat_rate_limit=_positive_int("AI_CHAT_RATE_LIMIT", 20),
        rate_limit_hash_key=rate_limit_hash_key,
    )
