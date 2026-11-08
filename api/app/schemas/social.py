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
    post_id: str | None
    comment_id: str | None = None
    status: Literal["pending"]
    created_at: datetime


class CommunityCreateRequest(BaseModel):
    slug: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    access_type: Literal["open", "restricted"]


class CommunityCreationRequestResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    access_type: Literal["open", "restricted"]
    status: Literal["pending"]
    created_at: datetime


class CommunityResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    rules: str
    access_type: Literal["open", "restricted"]
    membership_status: Literal["none", "pending", "active", "rejected"]
    membership_role: Literal["owner", "moderator", "member"] | None


class CommunityJoinRequest(BaseModel):
    message: str | None = Field(default=None, max_length=500)


class CommunityMembershipResponse(BaseModel):
    id: str
    community_id: str
    user_id: str
    display_name: str
    role: Literal["owner", "moderator", "member"]
    status: Literal["pending", "active", "rejected"]
    application_message: str | None
    joined_at: datetime


class MembershipDecision(BaseModel):
    decision: Literal["approve", "reject"]


class CommunityPostCreate(BaseModel):
    kind: Literal["discussion", "question"] = "discussion"
    body: str = Field(min_length=1, max_length=5000)


class SocialPostCommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class SocialPostCommentResponse(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_display_name: str
    body: str
    created_at: datetime


class SocialPostReactionRequest(BaseModel):
    kind: Literal["like", "agree", "curious"]


class SocialPostReactionResponse(BaseModel):
    post_id: str
    count: int
    current_user_reaction: Literal["like", "agree", "curious"] | None


class ModerationReportResponse(BaseModel):
    id: str
    post_id: str | None
    comment_id: str | None
    reporter_id: str
    reporter_display_name: str
    reason: str
    status: Literal["pending"]
    created_at: datetime


class ModerationActionCreate(BaseModel):
    action: Literal["hide", "remove", "warn", "suspend", "escalate", "dismiss"]
    reason: str = Field(min_length=3, max_length=500)
    duration_hours: int | None = Field(default=None, ge=1, le=720)


class ModerationActionResponse(BaseModel):
    id: str
    community_id: str
    report_id: str
    moderator_id: str
    target_user_id: str
    action: Literal["hide", "remove", "warn", "suspend", "escalate", "dismiss"]
    reason: str
    created_at: datetime
    expires_at: datetime | None
    appeal_status: Literal["pending", "upheld", "overturned"] | None


class ModerationAppealCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class ModerationAppealResponse(BaseModel):
    id: str
    action_id: str
    appellant_id: str
    reason: str
    status: Literal["pending", "upheld", "overturned"]
    created_at: datetime


class ModerationAppealDecision(BaseModel):
    decision: Literal["upheld", "overturned"]
