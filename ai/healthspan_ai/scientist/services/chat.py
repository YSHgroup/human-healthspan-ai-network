"""Restricted Private AI Scientist prototype workflow."""

from healthspan_ai.gateway.providers.openai_compatible import complete as complete_provider
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

SCIENTIST_SYSTEM_MESSAGE = (
    "You are a restricted Private AI Scientist prototype for an approved researcher. "
    "No private scientific corpus, project files, or retrieval tools are connected in this "
    "prototype. Use only material provided in the current conversation and general knowledge. "
    "Preserve uncertainty, do not invent citations, and label hypotheses as proposals requiring "
    "independent validation. Do not claim to have searched literature or project documents."
)
NO_VERIFIED_SOURCES_NOTICE = (
    "This prototype has no verified retrieval sources or literature search. Treat all outputs as "
    "proposals requiring independent validation before use."
)


async def answer(
    config: GatewayConfig,
    messages: list[ChatMessage],
) -> Completion:
    completion = await complete_provider(
        config,
        [ChatMessage(role="system", content=SCIENTIST_SYSTEM_MESSAGE), *messages],
    )
    if completion.source_notice is None:
        return Completion(
            provider=completion.provider,
            model=completion.model,
            content=completion.content,
            input_tokens=completion.input_tokens,
            output_tokens=completion.output_tokens,
            sources=completion.sources,
            source_notice=NO_VERIFIED_SOURCES_NOTICE,
        )
    return completion
