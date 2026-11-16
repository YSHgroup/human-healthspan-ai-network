"""Authenticated direct and group text messaging."""

import hmac
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.api.dependencies.identity import CurrentUser, require_trusted_origin, token_digest
from app.config import get_settings
from app.domains.messaging.realtime import message_connections
from app.infrastructure.database import get_db
from app.models import Conversation, ConversationParticipant, Message, User, UserSession
from app.schemas.messaging import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ParticipantResponse,
)

router = APIRouter(prefix="/messages", tags=["messaging"])
settings = get_settings()


def participant_ids(db: Session, conversation_id: str) -> set[str]:
    return set(
        db.scalars(
            select(ConversationParticipant.user_id).where(
                ConversationParticipant.conversation_id == conversation_id
            )
        )
    )


def conversation_response(db: Session, conversation: Conversation) -> ConversationResponse:
    users = db.scalars(
        select(User)
        .join(ConversationParticipant, ConversationParticipant.user_id == User.id)
        .where(ConversationParticipant.conversation_id == conversation.id)
        .order_by(User.display_name, User.id)
    ).all()
    return ConversationResponse(
        id=conversation.id,
        participants=[ParticipantResponse.model_validate(user) for user in users],
        created_at=conversation.created_at,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(user: CurrentUser, db: Session = Depends(get_db)) -> list[ConversationResponse]:
    conversations = db.scalars(
        select(Conversation)
        .join(ConversationParticipant)
        .where(ConversationParticipant.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    ).unique().all()
    return [conversation_response(db, conversation) for conversation in conversations]


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    body: ConversationCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    require_trusted_origin(request)
    emails = {email.strip().casefold() for email in body.participant_emails if email.strip()}
    if not emails:
        raise HTTPException(status_code=422, detail="At least one participant email is required")
    participants = db.scalars(select(User).where(User.email.in_(emails))).all()
    if len(participants) != len(emails) or user.email in emails:
        raise HTTPException(status_code=404, detail="One or more participants are unavailable")

    conversation = Conversation(created_by_id=user.id)
    db.add(conversation)
    db.flush()
    db.add_all(
        [
            ConversationParticipant(conversation_id=conversation.id, user_id=participant_id)
            for participant_id in [user.id, *(participant.id for participant in participants)]
        ]
    )
    db.commit()
    db.refresh(conversation)
    return conversation_response(db, conversation)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(
    conversation_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    before: datetime | None = None,
) -> list[MessageResponse]:
    if user.id not in participant_ids(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    statement = (
        select(Message)
        .options(joinedload(Message.sender))
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    )
    if before is not None:
        statement = statement.where(Message.created_at < before)
    messages = list(db.scalars(statement).unique().all())
    messages.reverse()
    return [
        MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            sender_display_name=message.sender.display_name,
            body=message.body,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.websocket("/conversations/{conversation_id}/ws")
async def message_stream(
    websocket: WebSocket,
    conversation_id: str,
    db: Session = Depends(get_db),
) -> None:
    origin = websocket.headers.get("origin")
    if origin is None or not any(
        hmac.compare_digest(origin.rstrip("/"), allowed) for allowed in settings.cors_origins
    ):
        await websocket.close(code=4403, reason="Untrusted request origin")
        return

    await websocket.accept()
    session_token = websocket.cookies.get(settings.session_cookie_name)
    if not session_token:
        await websocket.close(code=4401, reason="Authentication required")
        return

    now = datetime.now(timezone.utc)
    user_session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == token_digest(session_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
    )
    user = db.get(User, user_session.user_id) if user_session else None
    if user is None:
        await websocket.close(code=4401, reason="Session is invalid or expired")
        return
    if user.id not in participant_ids(db, conversation_id):
        await websocket.close(code=4404, reason="Conversation not found")
        return

    await message_connections.connect(conversation_id, websocket)
    try:
        while True:
            event = await websocket.receive()
            if event["type"] == "websocket.disconnect":
                break
    finally:
        await message_connections.disconnect(conversation_id, websocket)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: str,
    body: MessageCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> MessageResponse:
    require_trusted_origin(request)
    if user.id not in participant_ids(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    message = Message(
        conversation_id=conversation_id,
        sender_id=user.id,
        body=body.body.strip(),
        created_at=datetime.now(timezone.utc),
    )
    if not message.body:
        raise HTTPException(status_code=422, detail="Message cannot be blank")
    db.add(message)
    db.commit()
    db.refresh(message)
    response = MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_display_name=user.display_name,
        body=message.body,
        created_at=message.created_at,
    )
    await message_connections.broadcast(
        conversation_id,
        response.model_dump(mode="json"),
    )
    return response
