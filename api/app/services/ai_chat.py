"""AI calls and privacy-preserving usage records."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.config.settings import AIModelPricing
from app.models import AIConsent, AIInteraction, User
from healthspan_ai.gateway.service import (
    AccessDeniedError,
    ProviderConfigurationError,
    ProviderRequestError,
    complete_chat,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

settings = get_settings()
MAX_RECORDED_TOKEN_COUNT = 2_147_483_647
MAX_RECORDED_COST_USD = Decimal("9999999999.9999999999")


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
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    input_usd_per_million_tokens: Decimal | None = None,
    output_usd_per_million_tokens: Decimal | None = None,
    estimated_cost_usd: Decimal | None = None,
    pricing_source: str | None = None,
) -> None:
    consent = latest_consent(db, user.id)
    retain_content = consent is not None and consent.allowed and succeeded
    if type(input_tokens) is not int or not 0 <= input_tokens <= MAX_RECORDED_TOKEN_COUNT:
        input_tokens = None
    if type(output_tokens) is not int or not 0 <= output_tokens <= MAX_RECORDED_TOKEN_COUNT:
        output_tokens = None
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
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_usd_per_million_tokens=input_usd_per_million_tokens,
            output_usd_per_million_tokens=output_usd_per_million_tokens,
            estimated_cost_usd=estimated_cost_usd,
            pricing_source=pricing_source,
            latency_ms=latency_ms,
            succeeded=succeeded,
            error_code=error_code,
            training_eligible=False,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


def estimate_cost_usd(
    model: str | None,
    input_tokens: int | None,
    output_tokens: int | None,
    pricing: dict[str, AIModelPricing],
    pricing_source: str | None,
) -> Decimal | None:
    if (
        not model
        or input_tokens is None
        or output_tokens is None
        or type(input_tokens) is not int
        or type(output_tokens) is not int
        or not 0 <= input_tokens <= MAX_RECORDED_TOKEN_COUNT
        or not 0 <= output_tokens <= MAX_RECORDED_TOKEN_COUNT
        or not pricing_source
    ):
        return None
    model_pricing = pricing.get(model)
    if model_pricing is None:
        return None
    estimated_cost = (
        Decimal(input_tokens) * model_pricing.input_usd_per_million_tokens
        + Decimal(output_tokens) * model_pricing.output_usd_per_million_tokens
    ) / Decimal(1_000_000)
    if estimated_cost > MAX_RECORDED_COST_USD:
        return None
    return estimated_cost.quantize(Decimal("0.0000000001"))


async def run_chat(
    db: Session,
    user: User,
    environment: str,
    messages: list[ChatMessage],
) -> Completion:
    started = perf_counter()
    try:
        completion = await complete_chat(
            gateway_config(),
            environment,
            messages,
            scientist_enabled=settings.scientist_enabled,
            email_verified=user.email_verified_at is not None,
            researcher_approved=user.researcher_approved_at is not None,
        )
    except AccessDeniedError:
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
            error_code="AccessDeniedError",
        )
        raise
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

    model_pricing = (
        settings.ai_model_pricing.get(completion.model)
        if completion.model and settings.ai_pricing_source
        else None
    )
    estimated_cost = estimate_cost_usd(
        completion.model,
        completion.input_tokens,
        completion.output_tokens,
        settings.ai_model_pricing,
        settings.ai_pricing_source,
    )
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
        input_tokens=completion.input_tokens,
        output_tokens=completion.output_tokens,
        input_usd_per_million_tokens=(
            model_pricing.input_usd_per_million_tokens if model_pricing else None
        ),
        output_usd_per_million_tokens=(
            model_pricing.output_usd_per_million_tokens if model_pricing else None
        ),
        estimated_cost_usd=estimated_cost,
        pricing_source=settings.ai_pricing_source if model_pricing else None,
    )
    return completion
