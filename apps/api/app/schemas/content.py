from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class PostCreate(BaseModel):
    author_id: str | None = None
    community_id: UUID | None = None
    body: str = Field(min_length=1, max_length=10000)
    classification: Literal[
        "personal_experience",
        "opinion",
        "scientific_evidence",
        "expert_interpretation",
        "research_hypothesis",
        "ai_generated_hypothesis",
        "speculation",
    ] = "personal_experience"

class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    community_id: UUID | None
    body: str
    classification: str
    created_at: datetime


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
