"""Provider-independent AI gateway entry point."""

from healthspan_ai.gateway.providers.openai_compatible import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


async def complete_chat(
    config: GatewayConfig,
    environment: str,
    messages: list[ChatMessage],
) -> Completion:
    if config.provider == "openai-compatible":
        if environment == "general":
            from healthspan_ai.general.services.chat import answer

            return await answer(config, messages)
        if environment == "scientist":
            from healthspan_ai.scientist.services.chat import answer

            return await answer(config, messages)
        raise ProviderConfigurationError("Unsupported AI environment")
    if config.provider == "disabled":
        raise ProviderConfigurationError("No AI provider is configured")
    raise ProviderConfigurationError(f"Unsupported AI provider: {config.provider}")


__all__ = ["ProviderConfigurationError", "ProviderRequestError", "complete_chat"]
