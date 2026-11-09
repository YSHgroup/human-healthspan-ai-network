"""Platform administration request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.social import ModerationAppealResponse


class CommunityRequestReview(BaseModel):
    decision: Literal["approve", "reject"]


class PlatformCommunityRequestResponse(BaseModel):
    id: str
    requester_id: str
    requester_display_name: str
    slug: str
    name: str
    description: str
    access_type: Literal["open", "restricted"]
    created_at: datetime


class CommunityRequestDecisionResponse(BaseModel):
    id: str
    status: Literal["approved", "rejected"]
    community_id: str | None
    reviewed_at: datetime


class PlatformModerationReportResponse(BaseModel):
    id: str
    post_id: str | None
    comment_id: str | None
    reporter_id: str
    reporter_display_name: str
    reason: str
    status: Literal["pending", "escalated"]
    created_at: datetime
    target_kind: Literal["post", "comment"]
    target_body: str
    target_author_id: str
    target_author_display_name: str
    community_id: str | None
    community_name: str | None


class PlatformModerationActionCreate(BaseModel):
    action: Literal["hide", "remove", "warn", "dismiss"]
    reason: str = Field(min_length=3, max_length=500)


class PlatformAppealDecision(BaseModel):
    decision: Literal["upheld", "overturned"]


class PlatformModerationAppealResponse(ModerationAppealResponse):
    action_id: str
    action: Literal["hide", "remove", "warn", "suspend"]
    action_reason: str
    target_user_id: str
