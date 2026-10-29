"""extend member profiles

Revision ID: 9ac2a7348f16
Revises: cf5b66bc658f
Create Date: 2026-10-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9ac2a7348f16"
down_revision: Union[str, None] = "cf5b66bc658f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("location", sa.String(length=160), nullable=True))
    op.add_column("profiles", sa.Column("topics", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    op.add_column("profiles", sa.Column("researcher_identifier", sa.String(length=100), nullable=True))
    op.add_column("profiles", sa.Column("organization_affiliation", sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "organization_affiliation")
    op.drop_column("profiles", "researcher_identifier")
    op.drop_column("profiles", "topics")
    op.drop_column("profiles", "location")
