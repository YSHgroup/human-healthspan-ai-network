"""Add public social feed posts and reports.

Revision ID: 0002_social_feed
Revises: 0001_core
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_social_feed"
down_revision = "0001_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "social_posts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("author_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_social_posts_author_id", "social_posts", ["author_id"])
    op.create_index("ix_social_posts_created_at", "social_posts", ["created_at"])

    op.create_table(
        "social_post_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("post_id", sa.String(length=36), sa.ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reporter_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("reporter_id", "post_id", name="uq_social_post_reports_reporter_post"),
    )
    op.create_index("ix_social_post_reports_post_id", "social_post_reports", ["post_id"])
    op.create_index("ix_social_post_reports_reporter_id", "social_post_reports", ["reporter_id"])


def downgrade() -> None:
    op.drop_table("social_post_reports")
    op.drop_table("social_posts")
