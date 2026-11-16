"""Record AI provider token usage and configured cost estimates.

Revision ID: 0007_ai_usage_costs
Revises: 0006_research_document_files
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_ai_usage_costs"
down_revision = "0006_research_document_files"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_interactions", sa.Column("input_tokens", sa.Integer(), nullable=True))
    op.add_column("ai_interactions", sa.Column("output_tokens", sa.Integer(), nullable=True))
    op.add_column(
        "ai_interactions",
        sa.Column("input_usd_per_million_tokens", sa.Numeric(20, 10), nullable=True),
    )
    op.add_column(
        "ai_interactions",
        sa.Column("output_usd_per_million_tokens", sa.Numeric(20, 10), nullable=True),
    )
    op.add_column(
        "ai_interactions",
        sa.Column("estimated_cost_usd", sa.Numeric(20, 10), nullable=True),
    )
    op.add_column(
        "ai_interactions",
        sa.Column("pricing_source", sa.String(length=256), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ai_interactions", "pricing_source")
    op.drop_column("ai_interactions", "estimated_cost_usd")
    op.drop_column("ai_interactions", "output_usd_per_million_tokens")
    op.drop_column("ai_interactions", "input_usd_per_million_tokens")
    op.drop_column("ai_interactions", "output_tokens")
    op.drop_column("ai_interactions", "input_tokens")
