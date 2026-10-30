from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CommunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    description: str
    topic: str


class CommunitySummaryOut(CommunityOut):
    member_count: int
    is_member: bool = False


class AdminCommunityOut(CommunityOut):
    is_active: bool
    created_at: datetime


class AdminCommunityUpdate(BaseModel):
    is_active: bool
    reason: str = Field(min_length=3, max_length=500)


class ReportCreate(BaseModel):
    target_type: str = Field(pattern="^(post|comment|user|evidence)$")
    target_id: UUID
    reason: str = Field(min_length=3, max_length=80)
    details: str | None = Field(default=None, max_length=2000)


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    target_type: str
    target_id: str
    reason: str
    details: str | None
    status: str
    created_at: datetime


class ModerationDecision(BaseModel):
    action: str = Field(pattern="^(dismiss|remove|restrict)$")
    reason: str = Field(min_length=3, max_length=2000)


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    role: str | None = Field(
        default=None,
        pattern="^(user|moderator|scientific_reviewer|support_operator|read_only_auditor|admin)$",
    )
    reason: str = Field(min_length=3, max_length=500)

    @model_validator(mode="after")
    def require_change(self) -> "AdminUserUpdate":
        if self.is_active is None and self.role is None:
            raise ValueError("Provide at least one account change.")
        return self
