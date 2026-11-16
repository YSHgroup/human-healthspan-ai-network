"""OpenAI Chat Completions provider."""

from collections.abc import AsyncIterator

from healthspan_ai.gateway.providers.openai_compatible import (
    complete_compatible,
    stream_compatible,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

DEFAULT_BASE_URL = "https://api.openai.com/v1"


async def complete(config: GatewayConfig, messages: list[ChatMessage]) -> Completion:
    return await complete_compatible(
        config,
        messages,
        default_base_url=DEFAULT_BASE_URL,
    )


async def stream(config: GatewayConfig, messages: list[ChatMessage]) -> AsyncIterator[str]:
    return await stream_compatible(config, messages, default_base_url=DEFAULT_BASE_URL)
