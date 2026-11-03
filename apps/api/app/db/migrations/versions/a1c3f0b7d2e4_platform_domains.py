"""platform domains: organizations, health, messaging, events, entitlements, AI records

Revision ID: a1c3f0b7d2e4
Revises: 9ac2a7348f16
Create Date: 2026-11-02 00:00:00.000000

All tables are additive; no existing MVP table is altered. The tables are created
from the models listed in ``PLATFORM_TABLE_NAMES`` so the migration cannot drift from
the model definitions during the first rollout. Later schema changes must use
explicit, hand-reviewed operations (``alembic revision --autogenerate``).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1c3f0b7d2e4"
down_revision: Union[str, None] = "9ac2a7348f16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _platform_tables():
    from app.db.base import Base
    from app.models import domain, platform  # noqa: F401

    return [Base.metadata.tables[name] for name in platform.PLATFORM_TABLE_NAMES]


def upgrade() -> None:
    Base_metadata_bind = op.get_bind()
    from app.db.base import Base

    Base.metadata.create_all(bind=Base_metadata_bind, tables=_platform_tables(), checkfirst=True)


def downgrade() -> None:
    from app.db.base import Base

    Base.metadata.drop_all(bind=op.get_bind(), tables=_platform_tables(), checkfirst=True)
