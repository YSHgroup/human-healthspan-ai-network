from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.research import validate_http_url


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("This value cannot be blank.")
    return value.strip()


# ---------------------------------------------------------------- research access, tasks, work history
class ResearchMembershipApply(Strict):
    statement: str = Field(min_length=10, max_length=2000)

    _clean = field_validator("statement")(_not_blank)


class ResearchMembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    status: str
    statement: str
    reviewed_at: datetime | None = None
    review_note: str | None = None
    created_at: datetime


class ResearchMembershipDecision(Strict):
    decision: Literal["approve", "reject", "revoke"]
    note: str = Field(min_length=3, max_length=500)


class TaskCreate(Strict):
    title: str = Field(min_length=3, max_length=300)
    description: str = Field(default="", max_length=5000)
    assignee_id: UUID | None = None
    due_date: datetime | None = None

    _clean = field_validator("title")(_not_blank)


class TaskUpdate(Strict):
    title: str | None = Field(default=None, min_length=3, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    assignee_id: UUID | None = None
    status: Literal["todo", "in_progress", "done"] | None = None
    due_date: datetime | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    created_by: UUID
    assignee_id: UUID | None
    title: str
    description: str
    status: str
    due_date: datetime | None
    completed_at: datetime | None
    created_at: datetime


class WorkHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    organization_id: UUID | None
    project_id: UUID | None
    task_id: UUID | None
    kind: str
    summary: str
    verification_status: str
    verified_at: datetime | None
    supersedes_id: UUID | None
    created_at: datetime


class WorkHistoryAmend(Strict):
    summary: str = Field(min_length=3, max_length=1000)

    _clean = field_validator("summary")(_not_blank)


# ---------------------------------------------------------------- organizations
OrgRole = Literal["founder", "owner", "administrator", "research_leader", "researcher", "contributor", "member"]


class OrganizationCreate(Strict):
    name: str = Field(min_length=3, max_length=160)
    description: str = Field(default="", max_length=5000)
    website: str | None = Field(default=None, max_length=500)

    _clean = field_validator("name")(_not_blank)

    @field_validator("website")
    @classmethod
    def website_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class OrganizationUpdate(Strict):
    description: str | None = Field(default=None, max_length=5000)
    website: str | None = Field(default=None, max_length=500)
    policy: dict[str, Any] | None = None

    @field_validator("website")
    @classmethod
    def website_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    description: str
    website: str | None
    verification_status: str
    created_at: datetime


class OrganizationDetailOut(OrganizationOut):
    my_role: str | None = None
    member_count: int = 0


class OrganizationMemberOut(BaseModel):
    user_id: UUID
    display_name: str
    role: str


class OrganizationInviteCreate(Strict):
    user_id: UUID
    role: OrgRole = "member"


class OrganizationRoleUpdate(Strict):
    role: OrgRole


class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    role: str
    status: str
    created_at: datetime
    organization_name: str | None = None


class ProjectAttach(Strict):
    project_id: UUID


# ---------------------------------------------------------------- professional identity and badges
class ProfessionalRecordCreate(Strict):
    kind: Literal[
        "education", "certification", "employment", "experience", "research", "project", "contribution", "reference"
    ]
    title: str = Field(min_length=2, max_length=300)
    institution: str | None = Field(default=None, max_length=300)
    start_year: int | None = Field(default=None, ge=1900, le=2200)
    end_year: int | None = Field(default=None, ge=1900, le=2200)
    description: str | None = Field(default=None, max_length=5000)
    is_public: bool = True

    _clean = field_validator("title")(_not_blank)

    @model_validator(mode="after")
    def years_in_order(self) -> "ProfessionalRecordCreate":
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValueError("end_year cannot be before start_year.")
        return self


class ProfessionalRecordUpdate(Strict):
    title: str | None = Field(default=None, min_length=2, max_length=300)
    institution: str | None = Field(default=None, max_length=300)
    start_year: int | None = Field(default=None, ge=1900, le=2200)
    end_year: int | None = Field(default=None, ge=1900, le=2200)
    description: str | None = Field(default=None, max_length=5000)
    is_public: bool | None = None


class ProfessionalRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    kind: str
    title: str
    institution: str | None
    start_year: int | None
    end_year: int | None
    description: str | None
    is_public: bool
    verification_status: str
    verified_by_organization_id: UUID | None
    verified_at: datetime | None
    # "green" = verified, "yellow" = unverified (Architecture 3.3.2)
    verification_color: str = "yellow"


class BadgeCreate(Strict):
    slug: str = Field(min_length=3, max_length=120, pattern="^[a-z0-9][a-z0-9-]*$")
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)
    kind: Literal["platform", "certification"] = "platform"


class OrgBadgeCreate(Strict):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)


class BadgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    description: str
    kind: str
    organization_id: UUID | None
    is_active: bool


class BadgeAward(Strict):
    user_id: UUID


class PublicProfileOut(BaseModel):
    id: UUID
    role: str
    display_name: str
    bio: str | None
    expertise: list[str]
    badges: list[BadgeOut]
    professional_records: list[ProfessionalRecordOut]


# ---------------------------------------------------------------- health and consent
HealthCategory = Literal[
    "medical_record",
    "measurement",
    "laboratory",
    "observation",
    "nutrition",
    "fitness",
    "performance",
    "sleep_activity",
    "other",
]
HEALTH_CATEGORIES = (
    "medical_record",
    "measurement",
    "laboratory",
    "observation",
    "nutrition",
    "fitness",
    "performance",
    "sleep_activity",
    "other",
)


class HealthRecordCreate(Strict):
    category: HealthCategory
    title: str = Field(min_length=1, max_length=200)
    metric: str | None = Field(default=None, max_length=120)
    value_number: float | None = None
    value_text: str | None = Field(default=None, max_length=5000)
    unit: str | None = Field(default=None, max_length=40)
    source: Literal["manual", "device", "wearable", "document", "integration"] = "manual"
    recorded_at: datetime | None = None

    _clean = field_validator("title")(_not_blank)


class HealthRecordUpdate(Strict):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    metric: str | None = Field(default=None, max_length=120)
    value_number: float | None = None
    value_text: str | None = Field(default=None, max_length=5000)
    unit: str | None = Field(default=None, max_length=40)
    recorded_at: datetime | None = None


class HealthRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category: str
    title: str
    metric: str | None
    value_number: float | None
    value_text: str | None
    unit: str | None
    source: str
    recorded_at: datetime
    created_at: datetime


class HealthShareCreate(Strict):
    categories: list[HealthCategory] = Field(min_length=1, max_length=len(HEALTH_CATEGORIES))
    grantee_user_id: UUID | None = None
    grantee_organization_id: UUID | None = None
    create_link: bool = False
    expires_in_hours: int | None = Field(default=None, ge=1, le=24 * 90)
    label: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def exactly_one_grantee(self) -> "HealthShareCreate":
        targets = [self.grantee_user_id is not None, self.grantee_organization_id is not None, self.create_link]
        if sum(targets) != 1:
            raise ValueError("Choose exactly one of grantee_user_id, grantee_organization_id or create_link.")
        if self.create_link and self.expires_in_hours is None:
            raise ValueError("Share links must expire; provide expires_in_hours.")
        return self


class HealthShareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    grantee_user_id: UUID | None
    grantee_organization_id: UUID | None
    is_link: bool = False
    categories: list[str]
    label: str | None
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class HealthShareCreated(HealthShareOut):
    # Returned exactly once; only a hash is stored.
    link_token: str | None = None


class ConsentUpdate(Strict):
    granted: bool


class ConsentOut(BaseModel):
    purpose: str
    granted: bool
    updated_at: datetime | None = None


# ---------------------------------------------------------------- messaging
class MessageCreate(Strict):
    recipient_id: UUID | None = None
    conversation_id: UUID | None = None
    kind: Literal["text", "audio", "video", "media", "resource"] = "text"
    body: str = Field(default="", max_length=5000)
    media_url: str | None = Field(default=None, max_length=2000)

    @field_validator("media_url")
    @classmethod
    def media_url_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @model_validator(mode="after")
    def target_and_content(self) -> "MessageCreate":
        if (self.recipient_id is None) == (self.conversation_id is None):
            raise ValueError("Provide exactly one of recipient_id or conversation_id.")
        if self.kind == "text" and not self.body.strip():
            raise ValueError("Text messages cannot be blank.")
        if self.kind != "text" and not self.media_url:
            raise ValueError("Non-text messages require media_url.")
        return self


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    kind: str
    body: str
    media_url: str | None
    created_at: datetime


class ConversationOut(BaseModel):
    id: UUID
    participant_ids: list[UUID]
    participant_names: list[str]
    last_message_at: datetime | None
    unread_count: int


# ---------------------------------------------------------------- events
class EventCreate(Strict):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=10000)
    kind: Literal["meetup", "webinar", "conference", "seminar", "challenge", "festival", "scientific_meeting", "other"] = "meetup"
    visibility: Literal["public", "community", "invited"] = "public"
    starts_at: datetime
    ends_at: datetime | None = None
    location: str | None = Field(default=None, max_length=300)
    online_url: str | None = Field(default=None, max_length=2000)
    capacity: int | None = Field(default=None, ge=1, le=100000)
    community_id: UUID | None = None
    organization_id: UUID | None = None

    _clean = field_validator("title")(_not_blank)

    @field_validator("online_url")
    @classmethod
    def online_url_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @model_validator(mode="after")
    def valid_window(self) -> "EventCreate":
        if self.ends_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at.")
        if self.visibility == "community" and self.community_id is None:
            raise ValueError("Community events require community_id.")
        return self


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organizer_id: UUID
    community_id: UUID | None
    organization_id: UUID | None
    discussion_post_id: UUID | None
    title: str
    description: str
    kind: str
    visibility: str
    starts_at: datetime
    ends_at: datetime | None
    location: str | None
    online_url: str | None
    capacity: int | None
    status: str
    registered_count: int = 0
    is_registered: bool = False


class EventInvite(Strict):
    user_id: UUID


# ---------------------------------------------------------------- notifications
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: str
    title: str
    body: str | None
    resource_type: str | None
    resource_id: str | None
    read_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------------- entitlements and payments
class PurchaseCreate(Strict):
    feature: Literal["organization.create", "event.create", "organization.badge", "organization.ai"]
    quantity: int = Field(default=1, ge=1, le=100)
    organization_id: UUID | None = None


class PurchaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    organization_id: UUID | None
    feature: str
    quantity: int
    amount_cents: int
    currency: str
    status: str
    provider: str
    created_at: datetime


class EntitlementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_type: str
    subject_id: UUID
    feature: str
    quantity_total: int
    quantity_used: int
    source: str
    expires_at: datetime | None
    revoked_at: datetime | None


class EntitlementGrant(Strict):
    feature: Literal["organization.create", "event.create", "organization.badge", "organization.ai"]
    user_id: UUID | None = None
    organization_id: UUID | None = None
    quantity: int = Field(default=1, ge=1, le=1000)
    expires_at: datetime | None = None
    reason: str = Field(min_length=3, max_length=500)


class PaymentDecision(Strict):
    status: Literal["paid", "cancelled", "refunded"]
    external_reference: str | None = Field(default=None, max_length=120)
    reason: str = Field(min_length=3, max_length=500)


class PlanCreate(Strict):
    slug: str = Field(min_length=3, max_length=80, pattern="^[a-z0-9][a-z0-9-]*$")
    name: str = Field(min_length=2, max_length=120)
    features: list[Literal["organization.create", "event.create", "organization.badge", "organization.ai"]] = Field(
        min_length=1
    )
    price_cents: int = Field(default=0, ge=0)
    interval: Literal["month", "year", "one_time"] = "month"


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    features: list[str]
    price_cents: int
    currency: str
    interval: str
    is_active: bool


class SubscriptionGrant(Strict):
    user_id: UUID
    plan_slug: str
    period_days: int | None = Field(default=None, ge=1, le=3650)
    reason: str = Field(min_length=3, max_length=500)


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    plan_id: UUID
    status: str
    current_period_end: datetime | None


# ---------------------------------------------------------------- AI
class AIChatRequest(Strict):
    prompt: str = Field(min_length=2, max_length=4000)
    conversation_id: UUID | None = None

    _clean = field_validator("prompt")(_not_blank)


class LegacyAIChatRequest(BaseModel):
    """Tolerant body for the legacy /ai/chat and /ai/research endpoints."""

    model_config = ConfigDict(extra="ignore")

    prompt: str = Field(min_length=2, max_length=4000)
    conversation_id: UUID | None = None

    _clean = field_validator("prompt")(_not_blank)


class AIAnswerOut(BaseModel):
    system: str
    status: str
    answer: str
    sources: list[dict[str, Any]]
    evidence_summary: dict[str, int]
    uncertainty: str
    disclaimer: str
    run_id: UUID
    conversation_id: UUID
    provider: str
    model_version: str
    ai_generated: bool = True


class AIConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    system: str
    organization_id: UUID | None
    title: str
    created_at: datetime


class AIMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    sources: list[dict[str, Any]]
    created_at: datetime


class AIFeedbackCreate(Strict):
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=1000)
    permitted_use: Literal["product_improvement", "evaluation", "training"] = "product_improvement"


class OrgAICreate(Strict):
    name: str = Field(min_length=3, max_length=120)
    instructions: str = Field(default="", max_length=4000)

    _clean = field_validator("name")(_not_blank)


class OrgAIUpdate(Strict):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    instructions: str | None = Field(default=None, max_length=4000)
    status: Literal["active", "disabled"] | None = None


class OrgAIOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    instructions: str
    status: str


class OrgDocumentCreate(Strict):
    title: str = Field(min_length=2, max_length=300)
    content: str = Field(min_length=10, max_length=100000)
    source_label: str | None = Field(default=None, max_length=300)

    _clean = field_validator("title", "content")(_not_blank)


class OrgDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    title: str
    source_label: str | None
    created_at: datetime


# ---------------------------------------------------------------- admin
class OrganizationVerification(Strict):
    verification_status: Literal["verified", "rejected", "unverified"]
    reason: str = Field(min_length=3, max_length=500)


class OrganizationActivation(Strict):
    is_active: bool
    reason: str = Field(min_length=3, max_length=500)


class EventModeration(Strict):
    status: Literal["scheduled", "cancelled", "removed"]
    reason: str = Field(min_length=3, max_length=500)


class AdminBadgeAward(Strict):
    user_id: UUID
    reason: str = Field(min_length=3, max_length=500)


class ProfessionalVerification(Strict):
    verification_status: Literal["verified", "unverified"]
    reason: str = Field(min_length=3, max_length=500)
