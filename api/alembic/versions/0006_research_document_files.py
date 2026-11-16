"""Add private file metadata to research documents.

Revision ID: 0006_research_document_files
Revises: 0005_researcher_organizations
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_research_document_files"
down_revision = "0005_researcher_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "research_documents",
        sa.Column("file_storage_key", sa.String(32), nullable=True),
    )
    op.add_column(
        "research_documents",
        sa.Column("media_type", sa.String(100), nullable=True),
    )
    op.add_column(
        "research_documents",
        sa.Column("file_size", sa.Integer(), nullable=True),
    )
    op.add_column(
        "research_documents",
        sa.Column("sha256", sa.String(64), nullable=True),
    )
    op.create_index(
        "uq_research_documents_file_storage_key",
        "research_documents",
        ["file_storage_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_research_documents_file_storage_key",
        "research_documents",
    )
    op.drop_column("research_documents", "sha256")
    op.drop_column("research_documents", "file_size")
    op.drop_column("research_documents", "media_type")
    op.drop_column("research_documents", "file_storage_key")
