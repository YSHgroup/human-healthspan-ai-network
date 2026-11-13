"""Add persistent API rate-limit buckets.

Revision ID: 0008_api_rate_limits
Revises: 0007_ai_usage_costs
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_api_rate_limits"
down_revision = "0007_ai_usage_costs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_buckets",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
    )
    op.create_index(
        "ix_rate_limit_buckets_window_started_at",
        "rate_limit_buckets",
        ["window_started_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_rate_limit_buckets_window_started_at", table_name="rate_limit_buckets")
    op.drop_table("rate_limit_buckets")
