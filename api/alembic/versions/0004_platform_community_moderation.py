"""Add platform approval and moderation workflow metadata.

Revision ID: 0004_platform_community_moderation
Revises: 0003_social_communities
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_platform_community_moderation"
down_revision = "0003_social_communities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("community_creation_requests") as batch:
        batch.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("reviewed_by_id", sa.String(length=36), nullable=True))
        batch.create_foreign_key(
            "fk_community_creation_requests_reviewed_by_id_users",
            "users",
            ["reviewed_by_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("moderation_actions") as batch:
        batch.alter_column(
            "community_id",
            existing_type=sa.String(length=36),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("moderation_actions") as batch:
        batch.alter_column(
            "community_id",
            existing_type=sa.String(length=36),
            nullable=False,
        )
    with op.batch_alter_table("community_creation_requests") as batch:
        batch.drop_constraint(
            "fk_community_creation_requests_reviewed_by_id_users",
            type_="foreignkey",
        )
        batch.drop_column("reviewed_by_id")
        batch.drop_column("reviewed_at")
