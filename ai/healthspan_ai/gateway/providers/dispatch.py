"""Select the provider adapter configured for a chat request."""

from healthspan_ai.gateway.providers import claude, groq, ollama, openai
from healthspan_ai.gateway.providers.openai_compatible import (
    complete as complete_compatible,
    stream_compatible,
)
from healthspan_ai.gateway.providers.errors import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


async def complete(config: GatewayConfig, messages: list[ChatMessage]) -> Completion:
    provider = config.provider.strip().lower()
    adapters = {
        "claude": claude.complete,
        "groq": groq.complete,
        "ollama": ollama.complete,
        "openai": openai.complete,
        "openai-compatible": complete_compatible,
    }
    adapter = adapters.get(provider)
    if adapter is None:
        if provider == "disabled":
            raise ProviderConfigurationError("No AI provider is configured")
        raise ProviderConfigurationError(f"Unsupported AI provider: {config.provider}")
    return await adapter(config, messages)


async def stream(config: GatewayConfig, messages: list[ChatMessage]):
    provider = config.provider.strip().lower()
    adapters = {
        "claude": claude.stream,
        "groq": groq.stream,
        "ollama": ollama.stream,
        "openai": openai.stream,
        "openai-compatible": stream_compatible,
    }
    adapter = adapters.get(provider)
    if adapter is None:
        if provider == "disabled":
            raise ProviderConfigurationError("No AI provider is configured")
        raise ProviderConfigurationError(f"Unsupported AI provider: {config.provider}")
    return await adapter(config, messages)


__all__ = ["ProviderConfigurationError", "ProviderRequestError", "complete"]