"""Administrative researcher, organization, entitlement, event, and audit schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.researcher import EntitlementResponse


class PlatformUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    email_verified: bool
    researcher_approved: bool
    organization_creation_entitled: bool
    created_at: datetime


class UserVerificationUpdate(BaseModel):
    verified: bool


class ResearcherApplicationDecision(BaseModel):
    decision: Literal["approve", "reject"]


class ResearcherApplicationResponse(BaseModel):
    id: str
    user_id: str
    display_name: str
    email: str
    biography: str
    research_interests: str
    affiliation: str | None
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime


class OrganizationRequestResponse(BaseModel):
    id: str
    requester_id: str
    requester_display_name: str
    requester_email: str
    slug: str
    name: str
    description: str
    website: str
    created_at: datetime


class OrganizationRequestDecision(BaseModel):
    decision: Literal["approve", "reject"]


class OrganizationDecisionResponse(BaseModel):
    id: str
    status: Literal["approved", "rejected"]
    organization_id: str | None
    reviewed_at: datetime


class AdminOrganizationResponse(BaseModel):
    id: str
    slug: str
    name: str
    website: str
    verification_status: str
    created_by_id: str
    verified_by_id: str
    created_at: datetime


class EntitlementGrant(BaseModel):
    key: Literal["organization_create"]
    expires_at: datetime | None = None


class AdminEntitlementResponse(EntitlementResponse):
    user_id: str
    granted_by_id: str


class AdminResearchEventResponse(BaseModel):
    id: str
    organization_id: str | None
    organization_name: str | None
    created_by_id: str
    title: str
    starts_at: datetime
    ends_at: datetime
    status: str
    registration_count: int


class AdminAIUsageGroup(BaseModel):
    environment: str
    provider: str
    model: str | None
    total_interactions: int
    succeeded: int
    failed: int
    input_characters: int
    output_characters: int
    average_latency_ms: float


class AdminAIUsageResponse(BaseModel):
    days: int
    total_interactions: int
    succeeded: int
    failed: int
    input_characters: int
    output_characters: int
    groups: list[AdminAIUsageGroup]


class AdminAuditEventResponse(BaseModel):
    id: str
    actor_id: str
    actor_email: str
    action: str
    target_type: str
    target_id: str
    summary: str
    created_at: datetime


class ResearchEventDecision(BaseModel):
    decision: Literal["cancel"]
