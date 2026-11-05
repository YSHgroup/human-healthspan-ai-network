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


async def answer(
    config: GatewayConfig,
    messages: list[ChatMessage],
) -> Completion:
    return await complete_provider(
        config,
        [ChatMessage(role="system", content=GENERAL_SYSTEM_MESSAGE), *messages],
    )
