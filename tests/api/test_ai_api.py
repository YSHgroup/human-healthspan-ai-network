import json
from dataclasses import replace
from decimal import Decimal

from fastapi.testclient import TestClient

import app.api.v1.user.ai_chat as ai_routes
from app.config.settings import AIModelPricing
from app.models import AIInteraction
from healthspan_ai.gateway.providers.errors import ProviderRequestError
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


def test_private_scientist_is_gated_to_approved_researchers(
    api_client: TestClient,
    monkeypatch,
) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "member@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    monkeypatch.setattr(ai_routes, "settings", replace(ai_routes.settings, scientist_enabled=True))
    response = api_client.post(
        "/api/v1/user/researcher/ai/chat",
        headers={"Origin": "http://localhost:3002"},
        json={"messages": [{"role": "user", "content": "Summarize this paper"}]},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_general_chat_reports_disabled_provider_without_claiming_answer(
    api_client: TestClient,
    monkeypatch,
) -> None:
    response = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "member@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert response.status_code == 201
    import app.services.ai_chat as ai_service

    monkeypatch.setattr(ai_routes, "settings", replace(ai_routes.settings, ai_provider="disabled"))
    monkeypatch.setattr(ai_service, "settings", replace(ai_service.settings, ai_provider="disabled"))
    response = api_client.post(
        "/api/v1/user/social/ai/chat",
        headers={"Origin": "http://localhost:3000"},
        json={"messages": [{"role": "user", "content": "What is healthspan?"}]},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "service_unavailable"


def test_ai_chat_records_token_cost_without_retaining_content_and_marks_sources_unverified(
    api_client: TestClient,
    monkeypatch,
) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "member@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    import app.services.ai_chat as ai_service

    ai_pricing = {
        "test-model": AIModelPricing(
            input_usd_per_million_tokens=Decimal("2"),
            output_usd_per_million_tokens=Decimal("10"),
        )
    }
    monkeypatch.setattr(
        ai_service,
        "settings",
        replace(
            ai_service.settings,
            ai_model_pricing=ai_pricing,
            ai_pricing_source="test provider rate card",
        ),
    )

    async def fake_complete_chat(
        config: GatewayConfig,
        environment: str,
        messages: list[ChatMessage],
        *,
        scientist_enabled: bool = False,
        email_verified: bool = False,
        researcher_approved: bool = False,
    ) -> Completion:
        return Completion(
            provider="test-provider",
            model="test-model",
            content="A generated answer.",
            input_tokens=1000,
            output_tokens=500,
            sources=("https://example.test/paper",),
            source_notice="The provider claims this is source-backed.",
        )

    monkeypatch.setattr(ai_service, "complete_chat", fake_complete_chat)
    response = api_client.post(
        "/api/v1/user/social/ai/chat",
        headers={"Origin": "http://localhost:3000"},
        json={"messages": [{"role": "user", "content": "Summarize this paper"}]},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sources"] == ["https://example.test/paper"]
    assert payload["sources_verified"] is False
    assert "unverified" in payload["source_notice"]

    with api_client.app.state.test_session_factory() as db:
        interaction = db.query(AIInteraction).one()
        assert interaction.input_tokens == 1000
        assert interaction.output_tokens == 500
        assert interaction.input_usd_per_million_tokens == Decimal("2.0000000000")
        assert interaction.output_usd_per_million_tokens == Decimal("10.0000000000")
        assert interaction.estimated_cost_usd == Decimal("0.0070000000")
        assert interaction.pricing_source == "test provider rate card"
        assert interaction.prompt_content is None
        assert interaction.response_content is None
        assert interaction.training_eligible is False


def test_general_chat_stream_emits_deltas_and_records_completed_interaction(
    api_client: TestClient,
    monkeypatch,
) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "streaming-member@example.test",
            "display_name": "Streaming Member",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    import app.services.ai_chat as ai_service

    async def fake_stream_chat(*args, **kwargs):
        yield "A streamed "
        yield "answer."

    monkeypatch.setattr(ai_service, "stream_provider_chat", fake_stream_chat)
    response = api_client.post(
        "/api/v1/user/social/ai/chat/stream",
        headers={"Origin": "http://localhost:3000"},
        json={"messages": [{"role": "user", "content": "Question"}]},
    )

    assert response.status_code == 200
    events = [
        json.loads(line[6:])
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert events == [
        {"type": "delta", "content": "A streamed "},
        {"type": "delta", "content": "answer."},
        {
            "type": "done",
            "source_notice": (
                "This prototype has no verified retrieval sources. Check claims and citations "
                "independently; AI-generated hypotheses are not validated findings."
            ),
            "sources_verified": False,
        },
    ]

    with api_client.app.state.test_session_factory() as db:
        interaction = db.query(AIInteraction).one()
        assert interaction.output_characters == len("A streamed answer.")
        assert interaction.succeeded is True
        assert interaction.response_content is None


def test_general_chat_stream_reports_provider_failure_as_sse_error(
    api_client: TestClient,
    monkeypatch,
) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "streaming-error@example.test",
            "display_name": "Streaming Error",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    import app.services.ai_chat as ai_service

    async def failing_stream(*args, **kwargs):
        if False:
            yield ""
        raise ProviderRequestError("AI provider request failed")

    monkeypatch.setattr(ai_service, "stream_provider_chat", failing_stream)
    response = api_client.post(
        "/api/v1/user/social/ai/chat/stream",
        headers={"Origin": "http://localhost:3000"},
        json={"messages": [{"role": "user", "content": "Question"}]},
    )

    assert response.status_code == 200
    assert json.loads(response.text.removeprefix("data: ").strip()) == {
        "type": "error",
        "message": "AI provider request failed",
    }
    with api_client.app.state.test_session_factory() as db:
        interaction = db.query(AIInteraction).one()
        assert interaction.succeeded is False
        assert interaction.error_code == "ProviderRequestError"
