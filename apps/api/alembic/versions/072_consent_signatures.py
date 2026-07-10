"""Consent signature metadata and signed document linkage.

Revision ID: 072_consent_signatures
Revises: 071_case_proof_address
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "072_consent_signatures"
down_revision: str | None = "071_case_proof_address"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "consent_records",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "consent_records",
        sa.Column("signature_method", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "consent_records",
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "consent_records",
        sa.Column("signer_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "consent_records",
        sa.Column("signature_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_foreign_key(
        "fk_consent_records_document_id_documents",
        "consent_records",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_consent_records_document_id",
        "consent_records",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_consent_records_document_id", table_name="consent_records")
    op.drop_constraint(
        "fk_consent_records_document_id_documents", "consent_records", type_="foreignkey"
    )
    op.drop_column("consent_records", "signature_metadata")
    op.drop_column("consent_records", "signer_name")
    op.drop_column("consent_records", "signed_at")
    op.drop_column("consent_records", "signature_method")
    op.drop_column("consent_records", "document_id")
