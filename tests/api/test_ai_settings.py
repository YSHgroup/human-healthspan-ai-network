from decimal import Decimal

import pytest

from app.config.settings import (
    _parse_ai_model_pricing,
    _validate_production_configuration,
    get_settings,
)


def test_ai_model_pricing_parser_preserves_exact_model_rates() -> None:
    pricing = _parse_ai_model_pricing(
        '{"model-v1":{"input_usd_per_million_tokens":"2.25",'
        '"output_usd_per_million_tokens":"8"}}'
    )

    assert pricing["model-v1"].input_usd_per_million_tokens == Decimal("2.25")
    assert pricing["model-v1"].output_usd_per_million_tokens == Decimal("8")


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("not-json", "valid JSON"),
        ("[]", "object keyed by exact model name"),
        ('{"model-v1":{"input_usd_per_million_tokens":-1,'
         '"output_usd_per_million_tokens":2}}', "finite, non-negative"),
        ('{"model-v1":{"input_usd_per_million_tokens":1}}', "requires valid input and output"),
    ],
)
def test_ai_model_pricing_parser_rejects_invalid_values(value: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _parse_ai_model_pricing(value)


def test_production_requires_a_private_rate_limit_hash_key(monkeypatch) -> None:
    _set_valid_production_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("RATE_LIMIT_HASH_KEY", raising=False)
    get_settings.cache_clear()
    try:
        with pytest.raises(ValueError, match="RATE_LIMIT_HASH_KEY"):
            get_settings()
    finally:
        get_settings.cache_clear()


def _set_valid_production_environment(monkeypatch) -> None:
    monkeypatch.setenv("API_CORS_ORIGINS", "https://social.example.test,https://admin.example.test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@db.example.test/healthspan")
    monkeypatch.setenv("PLATFORM_ADMIN_EMAILS", "admin@example.test")
    monkeypatch.setenv("AI_PROVIDER", "disabled")
    monkeypatch.setenv("SCIENTIST_ENABLED", "false")


def test_production_configuration_accepts_explicit_secure_origins_and_database(monkeypatch) -> None:
    _set_valid_production_environment(monkeypatch)

    _validate_production_configuration()


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("API_CORS_ORIGINS", "http://social.example.test", "HTTPS origins"),
        ("API_CORS_ORIGINS", "", "explicitly configured"),
        ("DATABASE_URL", "sqlite:///./healthspan.db", "PostgreSQL"),
        ("PLATFORM_ADMIN_EMAILS", "", "production administrator"),
        ("SCIENTIST_ENABLED", "true", "cannot be true in production"),
        ("AI_PROVIDER", "unknown", "must be disabled or openai-compatible"),
    ],
)
def test_production_configuration_rejects_unsafe_values(
    monkeypatch,
    name: str,
    value: str,
    message: str,
) -> None:
    _set_valid_production_environment(monkeypatch)
    monkeypatch.setenv(name, value)

    with pytest.raises(ValueError, match=message):
        _validate_production_configuration()


def test_production_ai_provider_requires_https_endpoint(monkeypatch) -> None:
    _set_valid_production_environment(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_BASE_URL", "http://provider.example/v1")

    with pytest.raises(ValueError, match="AI_BASE_URL must use HTTPS"):
        _validate_production_configuration()


def test_production_ai_provider_requires_key_and_model(monkeypatch) -> None:
    _set_valid_production_environment(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_BASE_URL", "https://provider.example/v1")
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("AI_MODEL", raising=False)

    with pytest.raises(ValueError, match="AI_API_KEY and AI_MODEL"):
        _validate_production_configuration()


def test_production_session_lifetime_is_bounded(monkeypatch) -> None:
    _set_valid_production_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATE_LIMIT_HASH_KEY", "a" * 32)
    monkeypatch.setenv("SESSION_TTL_DAYS", "31")
    get_settings.cache_clear()
    try:
        with pytest.raises(ValueError, match="SESSION_TTL_DAYS"):
            get_settings()
    finally:
        get_settings.cache_clear()
