"""Platform-level models added on top of the Round 2 MVP schema.

These tables extend (never alter) the existing MVP tables so existing data and
API contracts stay compatible (Architecture v1.2 section 1.2 and 7.1).
Grouped by domain: organizations, research workspace, professional identity,
badges, health, messaging, events, notifications, entitlements and AI.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamped, UUIDPrimaryKey, utc_now


# --------------------------------------------------------------------------- organizations
class Organization(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "organizations"

    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    website: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(16), default="unverified", nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class OrganizationMember(UUIDPrimaryKey, Base):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_organization_member"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(24), default="member", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class OrganizationInvitation(UUIDPrimaryKey, Base):
    __tablename__ = "organization_invitations"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    invited_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    invited_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(24), default="member", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProjectOrganization(UUIDPrimaryKey, Base):
    """Attaches an existing research project to an organization workspace."""

    __tablename__ = "project_organizations"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("research_projects.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    attached_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# --------------------------------------------------------------------------- research workspace
class ResearchMembership(UUIDPrimaryKey, Timestamped, Base):
    """Researcher access state (Blueprint section 5): pending -> approved/rejected/revoked."""

    __tablename__ = "research_memberships"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    statement: Mapped[str] = mapped_column(Text, default="", nullable=False)
    reviewed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(String(500))


class ResearchTask(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "research_tasks"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="todo", nullable=False, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkHistoryEntry(UUIDPrimaryKey, Base):
    """Append-only contribution record. Corrections are amendments, never edits."""

    __tablename__ = "work_history_entries"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("research_projects.id", ondelete="SET NULL"), index=True)
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("research_tasks.id", ondelete="SET NULL"))
    kind: Mapped[str] = mapped_column(String(24), default="contribution", nullable=False)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(16), default="unverified", nullable=False)
    verified_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    supersedes_id: Mapped[UUID | None] = mapped_column(ForeignKey("work_history_entries.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# --------------------------------------------------------------------------- professional identity and badges
class ProfessionalRecord(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "professional_records"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    institution: Mapped[str | None] = mapped_column(String(300))
    start_year: Mapped[int | None] = mapped_column(Integer)
    end_year: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(16), default="unverified", nullable=False)
    verified_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    verified_by_organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Badge(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "badges"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    kind: Mapped[str] = mapped_column(String(32), default="platform", nullable=False, index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserBadge(UUIDPrimaryKey, Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge_id: Mapped[UUID] = mapped_column(ForeignKey("badges.id", ondelete="CASCADE"), index=True)
    awarded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# --------------------------------------------------------------------------- health and consent
class HealthRecord(UUIDPrimaryKey, Timestamped, Base):
    """Personal health data: private by default, never used by research or AI features."""

    __tablename__ = "health_records"
    __table_args__ = (Index("ix_health_user_category", "user_id", "category"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    metric: Mapped[str | None] = mapped_column(String(120), index=True)
    value_number: Mapped[float | None] = mapped_column(Float)
    value_text: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(16), default="manual", nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class HealthShare(UUIDPrimaryKey, Base):
    __tablename__ = "health_shares"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    grantee_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    grantee_organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ConsentRecord(UUIDPrimaryKey, Timestamped, Base):
    """Explicit, purpose-limited consent. Absence of a record means 'not granted'."""

    __tablename__ = "consent_records"
    __table_args__ = (UniqueConstraint("user_id", "purpose", name="uq_consent_user_purpose"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(40), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# --------------------------------------------------------------------------- messaging
class Conversation(UUIDPrimaryKey, Base):
    __tablename__ = "conversations"

    kind: Mapped[str] = mapped_column(String(16), default="direct", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class ConversationParticipant(UUIDPrimaryKey, Base):
    __tablename__ = "conversation_participants"
    __table_args__ = (UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),)

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Message(UUIDPrimaryKey, Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(16), default="text", nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    media_url: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# --------------------------------------------------------------------------- events
class Event(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "events"

    organizer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    community_id: Mapped[UUID | None] = mapped_column(ForeignKey("communities.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    discussion_post_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    kind: Mapped[str] = mapped_column(String(24), default="meetup", nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column(String(300))
    online_url: Mapped[str | None] = mapped_column(String(2000))
    capacity: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="scheduled", nullable=False, index=True)


class EventRegistration(UUIDPrimaryKey, Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_registration"),)

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="registered", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class EventInvitation(UUIDPrimaryKey, Base):
    __tablename__ = "event_invitations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_invitation"),)

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    invited_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# --------------------------------------------------------------------------- notifications
class Notification(UUIDPrimaryKey, Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_created", "user_id", "created_at"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(String(500))
    resource_type: Mapped[str | None] = mapped_column(String(40))
    resource_id: Mapped[str | None] = mapped_column(String(36))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# --------------------------------------------------------------------------- subscriptions and entitlements
class SubscriptionPlan(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "subscription_plans"

    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    features: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    interval: Mapped[str] = mapped_column(String(16), default="month", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Subscription(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("subscription_plans.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False, index=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Purchase(UUIDPrimaryKey, Timestamped, Base):
    """Purchase record. No payment processor is integrated; status is set by an administrator."""

    __tablename__ = "purchases"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    feature: Mapped[str] = mapped_column(String(60), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(24), default="manual", nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(120))


class Entitlement(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "entitlements"
    __table_args__ = (Index("ix_entitlements_subject_feature", "subject_type", "subject_id", "feature"),)

    subject_type: Mapped[str] = mapped_column(String(16), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    feature: Mapped[str] = mapped_column(String(60), nullable=False)
    quantity_total: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quantity_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[str] = mapped_column(String(24), default="admin_grant", nullable=False)
    purchase_id: Mapped[UUID | None] = mapped_column(ForeignKey("purchases.id", ondelete="SET NULL"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# --------------------------------------------------------------------------- AI
class AIConversation(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "ai_conversations"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    system: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)


class AIMessage(UUIDPrimaryKey, Base):
    __tablename__ = "ai_messages"

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(12), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AIRun(UUIDPrimaryKey, Base):
    __tablename__ = "ai_runs"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    system: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    conversation_id: Mapped[UUID | None] = mapped_column(ForeignKey("ai_conversations.id", ondelete="SET NULL"))
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    source_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    external_provider_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class AIFeedback(UUIDPrimaryKey, Base):
    """Shared-learning foundation: feedback is stored with an explicit permitted use."""

    __tablename__ = "ai_feedback"
    __table_args__ = (UniqueConstraint("run_id", "user_id", name="uq_ai_feedback_run_user"),)

    run_id: Mapped[UUID] = mapped_column(ForeignKey("ai_runs.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    rating: Mapped[str] = mapped_column(String(8), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000))
    permitted_use: Mapped[str] = mapped_column(String(24), default="product_improvement", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class OrgAIInstance(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "org_ai_instances"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))


class OrgKnowledgeDocument(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "org_knowledge_documents"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    added_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_label: Mapped[str | None] = mapped_column(String(300))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


PLATFORM_TABLE_NAMES = (
    "organizations",
    "organization_members",
    "organization_invitations",
    "project_organizations",
    "research_memberships",
    "research_tasks",
    "work_history_entries",
    "professional_records",
    "badges",
    "user_badges",
    "health_records",
    "health_shares",
    "consent_records",
    "conversations",
    "conversation_participants",
    "messages",
    "events",
    "event_registrations",
    "event_invitations",
    "notifications",
    "subscription_plans",
    "subscriptions",
    "purchases",
    "entitlements",
    "ai_conversations",
    "ai_messages",
    "ai_runs",
    "ai_feedback",
    "org_ai_instances",
    "org_knowledge_documents",
)
