"""Add community membership, comments, reactions and moderation.

Revision ID: 0003_social_communities
Revises: 0002_social_feed
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_social_communities"
down_revision = "0002_social_feed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "communities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("rules", sa.Text(), nullable=False),
        sa.Column("access_type", sa.String(length=16), nullable=False),
        sa.Column("created_by_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_communities_created_by_id", "communities", ["created_by_id"])

    op.create_table(
        "community_creation_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("requester_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("access_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug", name="uq_community_creation_requests_slug"),
    )
    op.create_index("ix_community_creation_requests_requester_id", "community_creation_requests", ["requester_id"])

    op.create_table(
        "community_memberships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("community_id", sa.String(length=36), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("application_message", sa.String(length=500), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("community_id", "user_id", name="uq_community_memberships_community_user"),
    )
    op.create_index("ix_community_memberships_community_id", "community_memberships", ["community_id"])
    op.create_index("ix_community_memberships_user_id", "community_memberships", ["user_id"])

    with op.batch_alter_table("social_posts") as batch:
        batch.add_column(sa.Column("community_id", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("moderation_status", sa.String(length=16), nullable=False, server_default="published"))
        batch.create_foreign_key(
            "fk_social_posts_community_id_communities",
            "communities",
            ["community_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.create_index("ix_social_posts_community_id", "social_posts", ["community_id"])
    op.create_index("ix_social_posts_moderation_status", "social_posts", ["moderation_status"])

    op.create_table(
        "social_post_comments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("post_id", sa.String(length=36), sa.ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("moderation_status", sa.String(length=16), nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_social_post_comments_post_id", "social_post_comments", ["post_id"])
    op.create_index("ix_social_post_comments_author_id", "social_post_comments", ["author_id"])
    op.create_index("ix_social_post_comments_moderation_status", "social_post_comments", ["moderation_status"])
    op.create_index("ix_social_post_comments_created_at", "social_post_comments", ["created_at"])

    op.create_table(
        "social_post_reactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("post_id", sa.String(length=36), sa.ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("post_id", "user_id", name="uq_social_post_reactions_post_user"),
    )
    op.create_index("ix_social_post_reactions_post_id", "social_post_reactions", ["post_id"])
    op.create_index("ix_social_post_reactions_user_id", "social_post_reactions", ["user_id"])

    with op.batch_alter_table("social_post_reports", recreate="always") as batch:
        batch.alter_column(
            "post_id",
            existing_type=sa.String(length=36),
            nullable=True,
        )
        batch.add_column(sa.Column("comment_id", sa.String(length=36), nullable=True))
        batch.create_foreign_key(
            "fk_social_post_reports_comment_id_comments",
            "social_post_comments",
            ["comment_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch.create_unique_constraint(
            "uq_social_post_reports_reporter_comment",
            ["reporter_id", "comment_id"],
        )
        batch.create_check_constraint(
            "ck_social_post_reports_one_target",
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
        )
    op.create_index("ix_social_post_reports_comment_id", "social_post_reports", ["comment_id"])

    op.create_table(
        "moderation_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("community_id", sa.String(length=36), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_id", sa.String(length=36), sa.ForeignKey("social_post_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("moderator_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("appeal_status", sa.String(length=16), nullable=True),
    )
    op.create_index("ix_moderation_actions_community_id", "moderation_actions", ["community_id"])
    op.create_index("ix_moderation_actions_report_id", "moderation_actions", ["report_id"])
    op.create_index("ix_moderation_actions_target_user_id", "moderation_actions", ["target_user_id"])

    op.create_table(
        "community_posting_suspensions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("community_id", sa.String(length=36), sa.ForeignKey("communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issued_by_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("moderation_action_id", sa.String(length=36), sa.ForeignKey("moderation_actions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_community_posting_suspensions_community_id", "community_posting_suspensions", ["community_id"])
    op.create_index("ix_community_posting_suspensions_user_id", "community_posting_suspensions", ["user_id"])
    op.create_index("ix_community_posting_suspensions_expires_at", "community_posting_suspensions", ["expires_at"])

    op.create_table(
        "moderation_appeals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("action_id", sa.String(length=36), sa.ForeignKey("moderation_actions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appellant_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_by_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("action_id", name="uq_moderation_appeals_action"),
    )
    op.create_index("ix_moderation_appeals_action_id", "moderation_appeals", ["action_id"])
    op.create_index("ix_moderation_appeals_appellant_id", "moderation_appeals", ["appellant_id"])


def downgrade() -> None:
    op.drop_table("moderation_appeals")
    op.drop_table("community_posting_suspensions")
    op.drop_table("moderation_actions")
    op.drop_index("ix_social_post_reports_comment_id", table_name="social_post_reports")
    op.execute("DELETE FROM social_post_reports WHERE comment_id IS NOT NULL")
    with op.batch_alter_table("social_post_reports", recreate="always") as batch:
        batch.drop_constraint("ck_social_post_reports_one_target", type_="check")
        batch.drop_constraint("uq_social_post_reports_reporter_comment", type_="unique")
        batch.drop_constraint("fk_social_post_reports_comment_id_comments", type_="foreignkey")
        batch.drop_column("comment_id")
        batch.alter_column(
            "post_id",
            existing_type=sa.String(length=36),
            nullable=False,
        )
    op.drop_table("social_post_reactions")
    op.drop_table("social_post_comments")
    op.drop_index("ix_social_posts_moderation_status", table_name="social_posts")
    op.drop_index("ix_social_posts_community_id", table_name="social_posts")
    with op.batch_alter_table("social_posts") as batch:
        batch.drop_constraint("fk_social_posts_community_id_communities", type_="foreignkey")
        batch.drop_column("moderation_status")
        batch.drop_column("community_id")
    op.drop_table("community_memberships")
    op.drop_table("community_creation_requests")
    op.drop_table("communities")
