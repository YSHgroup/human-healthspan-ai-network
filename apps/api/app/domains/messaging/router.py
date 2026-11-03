"""Member-to-member messaging as one shared backend service (Architecture 3.2.D).

Mounted under both the Social and Personal portals; both talk to this single implementation.
Audio/video/media messages carry a reference URL; binary upload and scanning are a later phase.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.common import as_utc
from app.domains.notifications.service import notify
from app.models.domain import Profile, User
from app.models.platform import Conversation, ConversationParticipant, Message
from app.schemas.platform import ConversationOut, MessageCreate, MessageOut
from app.services.audit import record_audit_event

router = APIRouter(tags=["messaging"])


def _participant_or_404(db: Session, user: User, conversation_id: UUID) -> ConversationParticipant:
    participant = db.scalar(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user.id,
        )
    )
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return participant


def _direct_conversation_id(db: Session, me: UUID, other: UUID) -> UUID | None:
    mine, theirs = aliased(ConversationParticipant), aliased(ConversationParticipant)
    return db.scalar(
        select(mine.conversation_id)
        .join(theirs, theirs.conversation_id == mine.conversation_id)
        .join(Conversation, Conversation.id == mine.conversation_id)
        .where(mine.user_id == me, theirs.user_id == other, Conversation.kind == "direct")
        .limit(1)
    )


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    if payload.conversation_id is not None:
        _participant_or_404(db, user, payload.conversation_id)
        conversation_id = payload.conversation_id
    else:
        recipient = db.get(User, payload.recipient_id)
        if recipient is None or not recipient.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found.")
        if recipient.id == user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot message yourself.")
        conversation_id = _direct_conversation_id(db, user.id, recipient.id)
        if conversation_id is None:
            conversation = Conversation(kind="direct")
            db.add(conversation)
            db.flush()
            conversation_id = conversation.id
            db.add(ConversationParticipant(conversation_id=conversation_id, user_id=user.id))
            db.add(ConversationParticipant(conversation_id=conversation_id, user_id=recipient.id))
    message = Message(
        conversation_id=conversation_id,
        sender_id=user.id,
        kind=payload.kind,
        body=payload.body.strip(),
        media_url=payload.media_url,
    )
    db.add(message)
    conversation = db.get(Conversation, conversation_id)
    conversation.last_message_at = utc_now()
    db.flush()
    others = db.scalars(
        select(ConversationParticipant.user_id).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id != user.id,
        )
    )
    for other_id in others:
        notify(db, other_id, "message.received", "New message", None, "conversation", conversation_id, user.id)
    record_audit_event(db, user.id, "message.sent", "conversation", conversation_id)
    db.commit()
    db.refresh(message)
    return message


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationOut]:
    mine = list(
        db.execute(
            select(Conversation, ConversationParticipant)
            .join(ConversationParticipant, ConversationParticipant.conversation_id == Conversation.id)
            .where(ConversationParticipant.user_id == user.id)
            .order_by(Conversation.last_message_at.desc().nulls_last(), Conversation.created_at.desc())
            .limit(limit)
        ).all()
    )
    results: list[ConversationOut] = []
    for conversation, participant in mine:
        others = db.execute(
            select(ConversationParticipant.user_id, Profile.display_name)
            .outerjoin(Profile, Profile.user_id == ConversationParticipant.user_id)
            .where(
                ConversationParticipant.conversation_id == conversation.id,
                ConversationParticipant.user_id != user.id,
            )
        ).all()
        unread_query = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation.id,
            Message.sender_id != user.id,
            Message.deleted_at.is_(None),
        )
        if participant.last_read_at is not None:
            unread_query = unread_query.where(Message.created_at > as_utc(participant.last_read_at))
        results.append(
            ConversationOut(
                id=conversation.id,
                participant_ids=[row[0] for row in others],
                participant_names=[row[1] or "Member" for row in others],
                last_message_at=conversation.last_message_at,
                unread_count=db.scalar(unread_query) or 0,
            )
        )
    return results


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def conversation_messages(
    conversation_id: UUID,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    participant = _participant_or_404(db, user, conversation_id)
    messages = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.deleted_at.is_(None))
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
    )
    participant.last_read_at = utc_now()
    db.commit()
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    message = db.get(Message, message_id)
    if message is None or message.sender_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")
    if message.deleted_at is None:
        message.deleted_at = utc_now()
        record_audit_event(db, user.id, "message.deleted", "message", message.id)
        db.commit()
