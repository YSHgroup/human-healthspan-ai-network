"""Authenticated direct and group text messaging."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.infrastructure.database import get_db
from app.models import Conversation, ConversationParticipant, Message, User
from app.schemas.messaging import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ParticipantResponse,
)

router = APIRouter(prefix="/messages", tags=["messaging"])


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


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
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
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_display_name=user.display_name,
        body=message.body,
        created_at=message.created_at,
    )
