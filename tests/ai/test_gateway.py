from functools import partial
import asyncio

import httpx
import pytest

from healthspan_ai.gateway.providers.openai_compatible import (
    ProviderConfigurationError,
    complete,
)
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
    assert seen["authorization"] == "******"
    assert '"content":"Question"' in str(seen["body"])


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
