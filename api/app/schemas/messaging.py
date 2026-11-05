"""Text-messaging API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    participant_emails: list[str] = Field(min_length=1, max_length=19)


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str


class ConversationResponse(BaseModel):
    id: str
    participants: list[ParticipantResponse]
    created_at: datetime


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    sender_display_name: str
    body: str
    created_at: datetime
