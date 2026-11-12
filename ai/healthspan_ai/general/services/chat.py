"""General Platform AI workflow."""

from healthspan_ai.gateway.providers.openai_compatible import complete as complete_provider
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

GENERAL_SYSTEM_MESSAGE = (
    "You are the General Platform AI for a human healthspan and science community. "
    "Use public and general knowledge only. Never claim access to private research or personal "
    "health records. Distinguish established evidence from uncertainty and hypotheses. "
    "Do not present medical diagnosis or treatment advice as a substitute for a clinician. "
    "Provide traceable source details when you know them; never invent citations. "
    "Label AI-generated hypotheses as proposals, not validated findings."
)
NO_VERIFIED_SOURCES_NOTICE = (
    "This prototype has no verified retrieval sources. Check claims and citations independently; "
    "AI-generated hypotheses are not validated findings."
)


async def answer(
    config: GatewayConfig,
    messages: list[ChatMessage],
) -> Completion:
    completion = await complete_provider(
        config,
        [ChatMessage(role="system", content=GENERAL_SYSTEM_MESSAGE), *messages],
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
