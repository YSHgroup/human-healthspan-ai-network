"""Social feed request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SocialPostCreate(BaseModel):
    kind: Literal["discussion", "question"] = "discussion"
    body: str = Field(min_length=1, max_length=5000)


class SocialPostResponse(BaseModel):
    id: str
    author_id: str
    author_display_name: str
    kind: Literal["discussion", "question"]
    body: str
    created_at: datetime


class SocialPostReportCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class SocialPostReportResponse(BaseModel):
    id: str
    post_id: str
    status: Literal["pending"]
    created_at: datetime
