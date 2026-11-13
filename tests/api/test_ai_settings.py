from decimal import Decimal

import pytest

from app.config.settings import _parse_ai_model_pricing, get_settings


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
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("RATE_LIMIT_HASH_KEY", raising=False)
    get_settings.cache_clear()
    try:
        with pytest.raises(ValueError, match="RATE_LIMIT_HASH_KEY"):
            get_settings()
    finally:
        get_settings.cache_clear()
