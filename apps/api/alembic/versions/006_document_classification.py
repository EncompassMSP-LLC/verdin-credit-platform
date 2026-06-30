"""Document classification fields.

Revision ID: 006_document_classification
Revises: 005_document_ocr
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "006_document_classification"
down_revision: str | None = "005_document_ocr"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("document_type", sa.String(50), nullable=True))
    op.add_column("documents", sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True))
    op.add_column("documents", sa.Column("classification_method", sa.String(20), nullable=True))
    op.add_column(
        "documents",
        sa.Column("classified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("classified_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "documents_classified_by_id_fkey",
        "documents",
        "users",
        ["classified_by_id"],
        ["id"],
    )
    op.create_index("ix_documents_document_type", "documents", ["document_type"])


def downgrade() -> None:
    op.drop_index("ix_documents_document_type", table_name="documents")
    op.drop_constraint("documents_classified_by_id_fkey", "documents", type_="foreignkey")
    op.drop_column("documents", "classified_by_id")
    op.drop_column("documents", "classified_at")
    op.drop_column("documents", "classification_method")
    op.drop_column("documents", "confidence_score")
    op.drop_column("documents", "document_type")
