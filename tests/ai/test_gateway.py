from functools import partial
import asyncio

import httpx
import pytest

from healthspan_ai.gateway.providers.openai_compatible import (
    ProviderConfigurationError,
    ProviderRequestError,
    complete,
)
from healthspan_ai.gateway.providers import claude, groq, ollama, openai
from healthspan_ai.gateway.service import AccessDeniedError, complete_chat
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


def test_openai_compatible_provider_sends_server_side_credentials(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("authorization")
        seen["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [
                    {
                        "message": {
                            "content": "A sourced answer.",
                            "sources": ["https://example.test/source/1"],
                            "source_notice": "Source-backed answer.",
                        }
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4},
            },
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        "healthspan_ai.gateway.providers.openai_compatible.httpx.AsyncClient",
        partial(original_client, transport=httpx.MockTransport(handler)),
    )
    config = GatewayConfig(
        provider="openai-compatible",
        model="test-model",
        api_key="test-key",
        base_url="https://provider.example/v1",
        timeout_seconds=2,
    )
    completion = asyncio.run(complete(config, [ChatMessage(role="user", content="Question")]))

    assert completion.content == "A sourced answer."
    assert completion.input_tokens == 10
    assert completion.output_tokens == 4
    assert completion.sources == ("https://example.test/source/1",)
    assert completion.source_notice == "Source-backed answer."
    assert seen["authorization"] == "Bearer test-key"
    assert '"content":"Question"' in str(seen["body"])


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 429, 500])
def test_provider_http_errors_report_status_without_exposing_response_body(
    monkeypatch,
    status_code: int,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"error": "private provider detail"})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        "healthspan_ai.gateway.providers.openai_compatible.httpx.AsyncClient",
        partial(original_client, transport=httpx.MockTransport(handler)),
    )
    config = GatewayConfig(
        provider="groq",
        model="openai/gpt-oss-20b",
        api_key="test-key",
        base_url="https://api.groq.com/openai/v1",
        timeout_seconds=2,
    )

    with pytest.raises(ProviderRequestError, match=f"HTTP {status_code}") as error:
        asyncio.run(complete(config, [ChatMessage(role="user", content="Question")]))

    assert "private provider detail" not in str(error.value)


@pytest.mark.parametrize(
    ("provider", "adapter", "expected_url", "api_key", "expected_auth"),
    [
        ("openai", openai.complete, "https://api.openai.com/v1/chat/completions", "test-key", "Bearer test-key"),
        ("groq", groq.complete, "https://api.groq.com/openai/v1/chat/completions", "test-key", "Bearer test-key"),
        ("ollama", ollama.complete, "http://localhost:11434/v1/chat/completions", None, None),
    ],
)
def test_openai_protocol_providers_use_their_default_endpoints(
    monkeypatch,
    provider: str,
    adapter,
    expected_url: str,
    api_key: str | None,
    expected_auth: str | None,
) -> None:
    seen: dict[str, str | None] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["authorization"] = request.headers.get("authorization")
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": "Provider response"}}],
            },
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        "healthspan_ai.gateway.providers.openai_compatible.httpx.AsyncClient",
        partial(original_client, transport=httpx.MockTransport(handler)),
    )
    config = GatewayConfig(
        provider=provider,
        model="test-model",
        api_key=api_key,
        base_url=None,
        timeout_seconds=2,
    )

    completion = asyncio.run(adapter(config, [ChatMessage(role="user", content="Question")]))

    assert completion.content == "Provider response"
    assert seen == {"url": expected_url, "authorization": expected_auth}


def test_claude_uses_messages_api_and_converts_system_prompt(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["api_key"] = request.headers.get("x-api-key")
        seen["version"] = request.headers.get("anthropic-version")
        seen["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "model": "claude-test",
                "content": [{"type": "text", "text": "Claude response"}],
                "usage": {"input_tokens": 11, "output_tokens": 7},
            },
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        "healthspan_ai.gateway.providers.claude.httpx.AsyncClient",
        partial(original_client, transport=httpx.MockTransport(handler)),
    )
    config = GatewayConfig(
        provider="claude",
        model="claude-test",
        api_key="test-key",
        base_url=None,
        timeout_seconds=2,
    )

    completion = asyncio.run(
        claude.complete(
            config,
            [
                ChatMessage(role="system", content="System instructions"),
                ChatMessage(role="user", content="Question"),
            ],
        )
    )

    assert completion.content == "Claude response"
    assert completion.input_tokens == 11
    assert completion.output_tokens == 7
    assert seen["url"] == "https://api.anthropic.com/v1/messages"
    assert seen["api_key"] == "test-key"
    assert seen["version"] == "2023-06-01"
    assert '"system":"System instructions"' in str(seen["body"])
    assert '"role":"user","content":"Question"' in str(seen["body"])


def test_gateway_requires_a_configured_provider() -> None:
    config = GatewayConfig(
        provider="openai-compatible",
        model=None,
        api_key=None,
        base_url=None,
        timeout_seconds=2,
    )
    with pytest.raises(ProviderConfigurationError):
        asyncio.run(complete_chat(config, "general", [ChatMessage(role="user", content="Question")]))


def test_groq_provider_routes_general_chat_through_general_workflow(monkeypatch) -> None:
    seen: dict[str, object] = {}

    async def fake_provider(config, messages):
        seen["provider"] = config.provider
        seen["messages"] = messages
        return Completion(
            provider=config.provider,
            model=config.model or "",
            content="Groq response",
        )

    monkeypatch.setattr(
        "healthspan_ai.general.services.chat.complete_provider",
        fake_provider,
    )
    config = GatewayConfig(
        provider="groq",
        model="openai/gpt-oss-20b",
        api_key="test-key",
        base_url="https://api.groq.com/openai/v1",
        timeout_seconds=2,
    )

    completion = asyncio.run(
        complete_chat(config, "general", [ChatMessage(role="user", content="Question")])
    )

    assert completion.provider == "groq"
    assert seen["provider"] == "groq"
    messages = seen["messages"]
    assert isinstance(messages, list)
    assert messages[0].role == "system"
    assert "public and general knowledge only" in messages[0].content
    assert messages[1] == ChatMessage(role="user", content="Question")


def test_gateway_denies_unapproved_scientist_access_before_provider_dispatch() -> None:
    config = GatewayConfig(
        provider="openai-compatible",
        model="test-model",
        api_key="test-key",
        base_url="https://provider.example/v1",
        timeout_seconds=2,
    )
    with pytest.raises(AccessDeniedError, match="Approved researcher"):
        asyncio.run(
            complete_chat(
                config,
                "scientist",
                [ChatMessage(role="user", content="Question")],
                scientist_enabled=True,
                email_verified=True,
            )
        )


def test_completion_keeps_explicit_source_metadata() -> None:
    completion = Completion(
        provider="openai-compatible",
        model="test-model",
        content="A sourced answer.",
        sources=("https://example.test/source",),
        source_notice="This answer has source metadata.",
    )

    assert completion.sources == ("https://example.test/source",)
    assert completion.source_notice == "This answer has source metadata."
