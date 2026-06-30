"""Document OCR pipeline — processing status and extracted text.

Revision ID: 005_document_ocr
Revises: 004_document_foundation
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "005_document_ocr"
down_revision: str | None = "004_document_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "processing_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column("documents", sa.Column("ocr_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("ocr_error", sa.Text(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("ocr_processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("documents", sa.Column("ocr_job_id", sa.String(36), nullable=True))
    op.add_column("documents", sa.Column("ocr_version_number", sa.Integer(), nullable=True))

    op.alter_column("documents", "processing_status", server_default=None)
    op.create_index("ix_documents_processing_status", "documents", ["processing_status"])


def downgrade() -> None:
    op.drop_index("ix_documents_processing_status", table_name="documents")
    op.drop_column("documents", "ocr_version_number")
    op.drop_column("documents", "ocr_job_id")
    op.drop_column("documents", "ocr_processed_at")
    op.drop_column("documents", "ocr_error")
    op.drop_column("documents", "ocr_text")
    op.drop_column("documents", "processing_status")
