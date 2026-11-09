"""Add researcher, organization, collaboration, event, entitlement, and audit workflows.

Revision ID: 0005_researcher_organizations
Revises: 0004_platform_community_moderation
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_researcher_organizations"
down_revision = "0004_platform_community_moderation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "researcher_applications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("biography", sa.Text(), nullable=False),
        sa.Column("research_interests", sa.String(500), nullable=False),
        sa.Column("affiliation", sa.String(200), nullable=True),
        sa.Column("profile_public", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("user_id", name="uq_researcher_applications_user"),
    )
    op.create_index("ix_researcher_applications_user_id", "researcher_applications", ["user_id"])
    op.create_index("ix_researcher_applications_status", "researcher_applications", ["status"])

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("website", sa.String(500), nullable=False),
        sa.Column("verification_status", sa.String(16), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_organizations_verification_status", "organizations", ["verification_status"])
    op.create_index("ix_organizations_created_by_id", "organizations", ["created_by_id"])

    op.create_table(
        "organization_creation_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("requester_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("website", sa.String(500), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("slug", name="uq_organization_creation_requests_slug"),
    )
    op.create_index("ix_organization_creation_requests_requester_id", "organization_creation_requests", ["requester_id"])
    op.create_index("ix_organization_creation_requests_status", "organization_creation_requests", ["status"])

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_organization_memberships_org_user"),
    )
    op.create_index("ix_organization_memberships_organization_id", "organization_memberships", ["organization_id"])
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"])
    op.create_index("ix_organization_memberships_status", "organization_memberships", ["status"])

    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("inviter_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_organization_invitations_organization_id", "organization_invitations", ["organization_id"])
    op.create_index("ix_organization_invitations_email", "organization_invitations", ["email"])
    op.create_index("ix_organization_invitations_status", "organization_invitations", ["status"])

    op.create_table(
        "entitlements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("granted_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_entitlements_user_id", "entitlements", ["user_id"])
    op.create_index("ix_entitlements_key", "entitlements", ["key"])

    op.create_table(
        "research_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("community_id", sa.String(36), sa.ForeignKey("communities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("objectives", sa.String(2000), nullable=False),
        sa.Column("research_questions", sa.String(2000), nullable=False),
        sa.Column("visibility", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_projects_organization_id", "research_projects", ["organization_id"])
    op.create_index("ix_research_projects_community_id", "research_projects", ["community_id"])
    op.create_index("ix_research_projects_owner_id", "research_projects", ["owner_id"])

    op.create_table(
        "research_project_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("invited_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "user_id", name="uq_research_project_members_project_user"),
    )
    op.create_index("ix_research_project_members_project_id", "research_project_members", ["project_id"])
    op.create_index("ix_research_project_members_user_id", "research_project_members", ["user_id"])
    op.create_index("ix_research_project_members_status", "research_project_members", ["status"])

    op.create_table(
        "research_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assignee_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_tasks_project_id", "research_tasks", ["project_id"])
    op.create_index("ix_research_tasks_assignee_id", "research_tasks", ["assignee_id"])
    op.create_index("ix_research_tasks_status", "research_tasks", ["status"])

    op.create_table(
        "research_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("access_scope", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_documents_project_id", "research_documents", ["project_id"])

    op.create_table(
        "research_activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_activities_project_id", "research_activities", ["project_id"])
    op.create_index("ix_research_activities_actor_id", "research_activities", ["actor_id"])
    op.create_index("ix_research_activities_occurred_at", "research_activities", ["occurred_at"])

    op.create_table(
        "research_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("location", sa.String(300), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_events_organization_id", "research_events", ["organization_id"])
    op.create_index("ix_research_events_created_by_id", "research_events", ["created_by_id"])
    op.create_index("ix_research_events_starts_at", "research_events", ["starts_at"])
    op.create_index("ix_research_events_status", "research_events", ["status"])

    op.create_table(
        "research_event_registrations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("research_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("event_id", "user_id", name="uq_research_event_registrations_event_user"),
    )
    op.create_index("ix_research_event_registrations_event_id", "research_event_registrations", ["event_id"])
    op.create_index("ix_research_event_registrations_user_id", "research_event_registrations", ["user_id"])

    op.create_table(
        "admin_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("target_id", sa.String(36), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_admin_audit_events_actor_id", "admin_audit_events", ["actor_id"])
    op.create_index("ix_admin_audit_events_action", "admin_audit_events", ["action"])
    op.create_index("ix_admin_audit_events_target_id", "admin_audit_events", ["target_id"])
    op.create_index("ix_admin_audit_events_created_at", "admin_audit_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("admin_audit_events")
    op.drop_table("research_event_registrations")
    op.drop_table("research_events")
    op.drop_table("research_activities")
    op.drop_table("research_documents")
    op.drop_table("research_tasks")
    op.drop_table("research_project_members")
    op.drop_table("research_projects")
    op.drop_table("entitlements")
    op.drop_table("organization_invitations")
    op.drop_table("organization_memberships")
    op.drop_table("organization_creation_requests")
    op.drop_table("organizations")
    op.drop_table("researcher_applications")
