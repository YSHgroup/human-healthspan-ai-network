"""AI calls and privacy-preserving usage records."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AIConsent, AIInteraction, User
from healthspan_ai.shared.contracts.chat import ChatMessage, GatewayConfig
from healthspan_ai.gateway.service import (
    ProviderConfigurationError,
    ProviderRequestError,
    complete_chat,
)

settings = get_settings()


def gateway_config() -> GatewayConfig:
    return GatewayConfig(
        provider=settings.ai_provider,
        model=settings.ai_model,
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
        timeout_seconds=settings.ai_timeout_seconds,
    )


def latest_consent(db: Session, user_id: str) -> AIConsent | None:
    return db.scalar(
        select(AIConsent)
        .where(AIConsent.user_id == user_id)
        .order_by(AIConsent.created_at.desc(), AIConsent.id.desc())
        .limit(1)
    )


def record_interaction(
    db: Session,
    *,
    user: User,
    environment: str,
    messages: list[ChatMessage],
    provider: str,
    model: str | None,
    answer: str | None,
    latency_ms: int,
    succeeded: bool,
    error_code: str | None = None,
) -> None:
    consent = latest_consent(db, user.id)
    retain_content = consent is not None and consent.allowed and succeeded
    db.add(
        AIInteraction(
            user_id=user.id,
            consent_id=consent.id if retain_content and consent else None,
            environment=environment,
            provider=provider,
            model=model,
            prompt_content=(
                "\n".join(f"{message.role}: {message.content}" for message in messages)
                if retain_content
                else None
            ),
            response_content=answer if retain_content else None,
            input_characters=sum(len(message.content) for message in messages),
            output_characters=len(answer or ""),
            latency_ms=latency_ms,
            succeeded=succeeded,
            error_code=error_code,
            training_eligible=False,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


async def run_chat(
    db: Session,
    user: User,
    environment: str,
    messages: list[ChatMessage],
):
    started = perf_counter()
    try:
        completion = await complete_chat(gateway_config(), environment, messages)
    except (ProviderConfigurationError, ProviderRequestError) as exc:
        record_interaction(
            db,
            user=user,
            environment=environment,
            messages=messages,
            provider=settings.ai_provider,
            model=settings.ai_model,
            answer=None,
            latency_ms=int((perf_counter() - started) * 1000),
            succeeded=False,
            error_code=type(exc).__name__,
        )
        raise

    record_interaction(
        db,
        user=user,
        environment=environment,
        messages=messages,
        provider=completion.provider,
        model=completion.model,
        answer=completion.content,
        latency_ms=int((perf_counter() - started) * 1000),
        succeeded=True,
    )
    return completion
