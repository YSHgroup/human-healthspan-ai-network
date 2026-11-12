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
    provider = (config.provider or "").strip().lower()
    environment_name = (environment or "").strip().lower()

    if provider == "openai-compatible":
        if environment_name == "general":
            from healthspan_ai.general.services.chat import answer

            return await answer(config, messages)
        if environment_name == "scientist":
            from healthspan_ai.scientist.services.chat import answer

            return await answer(config, messages)
        raise ProviderConfigurationError(f"Unsupported AI environment: {environment}")
    if provider == "disabled":
        raise ProviderConfigurationError("No AI provider is configured")
    raise ProviderConfigurationError(f"Unsupported AI provider: {config.provider}")


__all__ = ["ProviderConfigurationError", "ProviderRequestError", "complete_chat"]
