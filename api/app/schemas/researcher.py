"""Researcher, organization, and collaboration request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResearcherApplicationCreate(BaseModel):
    biography: str = Field(min_length=30, max_length=3000)
    research_interests: str = Field(min_length=3, max_length=500)
    affiliation: str | None = Field(default=None, max_length=200)
    profile_public: bool = False


class ResearcherProfileUpdate(ResearcherApplicationCreate):
    pass


class ResearcherStatusResponse(BaseModel):
    email_verified: bool
    approved: bool
    application_status: Literal["none", "pending", "approved", "rejected"]


class ResearcherProfileResponse(BaseModel):
    user_id: str
    display_name: str
    biography: str
    research_interests: str
    affiliation: str | None
    profile_public: bool


class OrganizationRequestCreate(BaseModel):
    slug: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    website: str = Field(
        min_length=10,
        max_length=500,
        pattern=r"^https?://[^\s/$.?#].[^\s]*$",
    )


class OrganizationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    description: str
    website: str
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime


class OrganizationResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    website: str
    verification_status: Literal["verified", "unverified"]
    role: Literal["owner", "admin", "member"] | None = None


class OrganizationInvitationCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: Literal["admin", "member"] = "member"


class OrganizationInvitationResponse(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    email: str
    role: Literal["admin", "member"]
    status: Literal["pending", "accepted", "declined", "expired"]
    expires_at: datetime


class OrganizationMemberResponse(BaseModel):
    user_id: str
    display_name: str
    email: str
    role: Literal["owner", "admin", "member"]
    joined_at: datetime


class ResearchProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    objectives: str = Field(default="", max_length=2000)
    research_questions: str = Field(default="", max_length=2000)
    organization_id: str | None = None
    community_id: str | None = None
    visibility: Literal["private", "team", "invited", "community", "public"] = "private"


class ResearchProjectResponse(BaseModel):
    id: str
    organization_id: str | None
    community_id: str | None
    owner_id: str
    owner_display_name: str
    title: str
    description: str
    objectives: str
    research_questions: str
    visibility: Literal["private", "team", "invited", "community", "public"]
    status: Literal["active", "completed", "archived"]
    created_at: datetime
    updated_at: datetime


class ResearchProjectMemberCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ResearchProjectMemberResponse(BaseModel):
    user_id: str
    display_name: str
    role: Literal["owner", "contributor"]
    joined_at: datetime


class ResearchTaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=2000)
    assignee_email: str | None = Field(default=None, max_length=320)
    due_at: datetime | None = None


class ResearchTaskUpdate(BaseModel):
    status: Literal["open", "in_progress", "completed", "cancelled"]


class ResearchTaskResponse(BaseModel):
    id: str
    project_id: str
    created_by_id: str
    assignee_id: str | None
    assignee_display_name: str | None
    title: str
    description: str
    status: Literal["open", "in_progress", "completed", "cancelled"]
    due_at: datetime | None
    created_at: datetime


class ResearchDocumentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=100_000)
    access_scope: Literal["private", "project"] = "private"


class ResearchDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    uploaded_by_id: str
    title: str
    filename: str
    content: str
    access_scope: Literal["private", "project"]
    media_type: str | None
    file_size: int | None
    created_at: datetime


class ResearchActivityResponse(BaseModel):
    id: str
    actor_id: str
    actor_display_name: str
    action: str
    summary: str
    occurred_at: datetime


class ResearchEventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    location: str = Field(default="Online", min_length=2, max_length=300)
    organization_id: str | None = None
    starts_at: datetime
    ends_at: datetime


class ResearchEventResponse(BaseModel):
    id: str
    organization_id: str | None
    organization_name: str | None
    created_by_id: str
    title: str
    description: str
    location: str
    starts_at: datetime
    ends_at: datetime
    status: Literal["published", "cancelled"]
    registration_count: int
    registered: bool


class EntitlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    granted_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
