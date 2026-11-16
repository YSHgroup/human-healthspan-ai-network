"""Groq OpenAI-compatible provider."""

from healthspan_ai.gateway.providers.openai_compatible import complete_compatible
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"


async def complete(config: GatewayConfig, messages: list[ChatMessage]) -> Completion:
    return await complete_compatible(
        config,
        messages,
        default_base_url=DEFAULT_BASE_URL,
    )
