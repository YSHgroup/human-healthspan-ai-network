"""General Platform AI and restricted Scientist prototype routes."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.api.dependencies.rate_limit import rate_limit
from app.config import get_settings
from app.infrastructure.database import get_db
from app.models import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai_chat import run_chat, stream_chat
from healthspan_ai.gateway.service import (
    AccessDeniedError,
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.shared.contracts.chat import ChatMessage

router = APIRouter()
settings = get_settings()


def _event(event_type: str, **payload: object) -> str:
    return f"data: {json.dumps({'type': event_type, **payload}, ensure_ascii=False)}\n\n"


async def respond(
    environment: str,
    messages: list[ChatMessage],
    user: User,
    db: Session,
) -> ChatResponse:
    try:
        completion = await run_chat(db, user, environment, messages)
    except AccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    source_notice = completion.source_notice
    if completion.sources or completion.source_notice:
        source_notice = (
            "Provider-supplied source details and notices are unverified. "
            f"{source_notice or 'No verified retrieval sources are connected.'}"
        )
    else:
        source_notice = source_notice or (
            "This prototype has no verified retrieval sources. Check claims and citations "
            "independently; AI-generated hypotheses are not validated findings."
        )

    return ChatResponse(
        answer=completion.content,
        provider=completion.provider,
        model=completion.model,
        sources=list(completion.sources),
        sources_verified=False,
        source_notice=source_notice,
    )


@router.post(
    "/social/ai/chat",
    response_model=ChatResponse,
    tags=["general-ai"],
    dependencies=[Depends(rate_limit("ai_chat"))],
)
async def general_ai_chat(
    body: ChatRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ChatResponse:
    require_trusted_origin(request)
    return await respond(
        "general",
        [ChatMessage(role=turn.role, content=turn.content.strip()) for turn in body.messages],
        user,
        db,
    )


@router.post(
    "/social/ai/chat/stream",
    tags=["general-ai"],
    dependencies=[Depends(rate_limit("ai_chat"))],
)
async def general_ai_chat_stream(
    body: ChatRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    require_trusted_origin(request)
    messages = [ChatMessage(role=turn.role, content=turn.content.strip()) for turn in body.messages]

    async def events():
        try:
            async for content in stream_chat(db, user, "general", messages):
                yield _event("delta", content=content)
            yield _event(
                "done",
                source_notice=(
                    "This prototype has no verified retrieval sources. Check claims and citations "
                    "independently; AI-generated hypotheses are not validated findings."
                ),
                sources_verified=False,
            )
        except (AccessDeniedError, ProviderConfigurationError, ProviderRequestError) as exc:
            yield _event("error", message=str(exc))

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


@router.post(
    "/researcher/ai/chat",
    response_model=ChatResponse,
    tags=["private-ai-scientist"],
    dependencies=[Depends(rate_limit("ai_chat"))],
)
async def scientist_chat(
    body: ChatRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ChatResponse:
    require_trusted_origin(request)
    if not settings.scientist_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Private AI Scientist prototype is disabled",
        )
    if user.email_verified_at is None or user.researcher_approved_at is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approved researcher access required")
    return await respond(
        "scientist",
        [ChatMessage(role=turn.role, content=turn.content.strip()) for turn in body.messages],
        user,
        db,
    )


@router.post(
    "/researcher/ai/chat/stream",
    tags=["private-ai-scientist"],
    dependencies=[Depends(rate_limit("ai_chat"))],
)
async def scientist_chat_stream(
    body: ChatRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    require_trusted_origin(request)
    if not settings.scientist_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Private AI Scientist prototype is disabled",
        )
    if user.email_verified_at is None or user.researcher_approved_at is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approved researcher access required")
    messages = [ChatMessage(role=turn.role, content=turn.content.strip()) for turn in body.messages]

    async def events():
        try:
            async for content in stream_chat(db, user, "scientist", messages):
                yield _event("delta", content=content)
            yield _event(
                "done",
                source_notice=(
                    "This prototype has no verified retrieval sources or literature search. Treat all "
                    "outputs as proposals requiring independent validation before use."
                ),
                sources_verified=False,
            )
        except (AccessDeniedError, ProviderConfigurationError, ProviderRequestError) as exc:
            yield _event("error", message=str(exc))

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )
