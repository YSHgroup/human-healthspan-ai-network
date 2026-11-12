"""General Platform AI and restricted Scientist prototype routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.config import get_settings
from app.infrastructure.database import get_db
from app.models import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai_chat import run_chat
from healthspan_ai.gateway.service import ProviderConfigurationError, ProviderRequestError
from healthspan_ai.shared.contracts.chat import ChatMessage

router = APIRouter()
settings = get_settings()


async def respond(
    environment: str,
    messages: list[ChatMessage],
    user: User,
    db: Session,
) -> ChatResponse:
    try:
        completion = await run_chat(db, user, environment, messages)
    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The configured AI provider could not complete the request",
        ) from exc
    return ChatResponse(
        answer=completion.content,
        provider=completion.provider,
        model=completion.model,
        sources=list(completion.sources),
        source_notice=(
            completion.source_notice
            or "This prototype has no verified retrieval sources. Check claims and citations "
            "independently; AI-generated hypotheses are not validated findings."
        ),
    )


@router.post("/social/ai/chat", response_model=ChatResponse, tags=["general-ai"])
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


@router.post("/researcher/ai/chat", response_model=ChatResponse, tags=["private-ai-scientist"])
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
