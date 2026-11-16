"""Provider-independent AI gateway entry point."""

from collections.abc import AsyncIterator

from healthspan_ai.gateway.providers.dispatch import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.gateway.providers import dispatch as provider_dispatch
from healthspan_ai.governance.permissions import AccessDeniedError, ensure_environment_allowed
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


async def complete_chat(
    config: GatewayConfig,
    environment: str,
    messages: list[ChatMessage],
    *,
    scientist_enabled: bool = False,
    email_verified: bool = False,
    researcher_approved: bool = False,
) -> Completion:
    provider = (config.provider or "").strip().lower()
    try:
        environment_name = ensure_environment_allowed(
            environment,
            scientist_enabled=scientist_enabled,
            email_verified=email_verified,
            researcher_approved=researcher_approved,
        )
    except ValueError as exc:
        raise ProviderConfigurationError(str(exc)) from exc

    if provider in {"openai", "openai-compatible", "claude", "groq", "ollama"}:
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


async def stream_chat(
    config: GatewayConfig,
    environment: str,
    messages: list[ChatMessage],
    *,
    scientist_enabled: bool = False,
    email_verified: bool = False,
    researcher_approved: bool = False,
) -> AsyncIterator[str]:
    try:
        environment_name = ensure_environment_allowed(
            environment,
            scientist_enabled=scientist_enabled,
            email_verified=email_verified,
            researcher_approved=researcher_approved,
        )
    except ValueError as exc:
        raise ProviderConfigurationError(str(exc)) from exc

    if environment_name == "general":
        from healthspan_ai.general.services.chat import GENERAL_SYSTEM_MESSAGE

        messages = [ChatMessage(role="system", content=GENERAL_SYSTEM_MESSAGE), *messages]
    elif environment_name == "scientist":
        from healthspan_ai.scientist.services.chat import SCIENTIST_SYSTEM_MESSAGE

        messages = [ChatMessage(role="system", content=SCIENTIST_SYSTEM_MESSAGE), *messages]
    async for content in await provider_dispatch.stream(config, messages):
        yield content


__all__ = [
    "AccessDeniedError",
    "ProviderConfigurationError",
    "ProviderRequestError",
    "complete_chat",
    "stream_chat",
]
