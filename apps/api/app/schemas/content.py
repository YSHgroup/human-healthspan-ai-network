from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

class PostCreate(BaseModel):
    author_id: str | None = None
    community_id: UUID | None = None
    body: str = Field(min_length=1, max_length=10000)
    content_type: Literal["post", "question"] = "post"
    classification: Literal[
        "personal_experience",
        "opinion",
        "scientific_evidence",
        "expert_interpretation",
        "research_hypothesis",
        "ai_generated_hypothesis",
        "speculation",
    ] = "personal_experience"

    @field_validator("body")
    @classmethod
    def body_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Post body cannot be blank.")
        return value.strip()


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    community_id: UUID | None
    body: str
    content_type: str
    classification: str
    created_at: datetime


class FeedPostOut(PostOut):
    author_display_name: str
    author_role: str
    comment_count: int
    reaction_count: int
    is_reacted: bool = False
    is_bookmarked: bool = False


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("body")
    @classmethod
    def body_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Comment body cannot be blank.")
        return value.strip()


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    author_id: UUID
    body: str
    created_at: datetime


class CommentFeedOut(CommentOut):
    author_display_name: str


class ReactionCreate(BaseModel):
    kind: Literal["like", "insightful", "support"]
