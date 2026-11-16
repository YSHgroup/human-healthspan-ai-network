from dataclasses import replace

from fastapi.testclient import TestClient

import app.api.dependencies.rate_limit as rate_limit
from app.models import RateLimitBucket
from healthspan_ai.gateway.service import ProviderConfigurationError


def test_login_rate_limit_is_shared_and_returns_retry_after(
    api_client: TestClient,
    monkeypatch,
) -> None:
    settings = rate_limit.get_settings()
    monkeypatch.setattr(
        rate_limit,
        "get_settings",
        lambda: replace(settings, auth_login_rate_limit=2),
    )
    request = {
        "headers": {"Origin": "http://localhost:3000"},
        "json": {"email": "missing@example.test", "password": "not-the-password"},
    }

    untrusted = api_client.post(
        "/api/v1/user/auth/login",
        headers={"Origin": "https://untrusted.example"},
        json=request["json"],
    )
    assert untrusted.status_code == 403
    assert api_client.post("/api/v1/user/auth/login", **request).status_code == 401
    assert api_client.post("/api/v1/user/auth/login", **request).status_code == 401
    limited = api_client.post("/api/v1/user/auth/login", **request)

    assert limited.status_code == 429
    assert limited.json()["code"] == "rate_limited"
    assert int(limited.headers["Retry-After"]) > 0

    with api_client.app.state.test_session_factory() as db:
        bucket = db.query(RateLimitBucket).one()
        assert bucket.request_count == 3


def test_ai_rate_limit_requires_authentication_and_is_per_account(
    api_client: TestClient,
    monkeypatch,
) -> None:
    settings = rate_limit.get_settings()
    monkeypatch.setattr(
        rate_limit,
        "get_settings",
        lambda: replace(settings, ai_chat_rate_limit=1),
    )
    import app.services.ai_chat as ai_service

    async def unavailable_provider(*args, **kwargs):
        raise ProviderConfigurationError("No AI provider is configured")

    monkeypatch.setattr(ai_service, "complete_chat", unavailable_provider)
    request = {
        "headers": {"Origin": "http://localhost:3000"},
        "json": {"messages": [{"role": "user", "content": "Question"}]},
    }

    unauthenticated = api_client.post("/api/v1/user/social/ai/chat", **request)
    assert unauthenticated.status_code == 401
    with api_client.app.state.test_session_factory() as db:
        assert db.query(RateLimitBucket).count() == 0

    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "rate-limit@example.test",
            "display_name": "Rate Limited",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    assert api_client.post("/api/v1/user/social/ai/chat", **request).status_code == 503
    limited = api_client.post("/api/v1/user/social/ai/chat", **request)
    assert limited.status_code == 429
    assert limited.json()["code"] == "rate_limited"
