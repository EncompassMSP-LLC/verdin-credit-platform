"""Document metadata and entity resolution tables.

Revision ID: 007_document_metadata_resolution
Revises: 006_document_classification
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "007_document_metadata_resolution"
down_revision: str | None = "006_document_classification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consumer_name", sa.String(255), nullable=True),
        sa.Column("bureau", sa.String(50), nullable=True),
        sa.Column("creditor", sa.String(255), nullable=True),
        sa.Column("collection_agency", sa.String(255), nullable=True),
        sa.Column("account_number_masked", sa.String(50), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("open_date", sa.Date(), nullable=True),
        sa.Column("balance", sa.Numeric(12, 2), nullable=True),
        sa.Column("payment_status", sa.String(50), nullable=True),
        sa.Column("addresses", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("phone_numbers", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("ssn_masked", sa.String(20), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("extraction_method", sa.String(20), nullable=False, server_default="rules"),
        sa.Column("metadata_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("extraction_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.UniqueConstraint("document_id", name="uq_document_metadata_document_id"),
    )
    op.create_index("ix_document_metadata_status", "document_metadata", ["metadata_status"])
    op.create_index(
        "ix_document_metadata_organization_id", "document_metadata", ["organization_id"]
    )

    op.create_table(
        "document_entity_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("matched_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("resolution_status", sa.String(20), nullable=False),
        sa.Column("resolution_method", sa.String(20), nullable=False, server_default="rules"),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("candidate_entity_ids", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"]),
        sa.UniqueConstraint(
            "document_id",
            "entity_type",
            name="uq_document_entity_resolution_type",
        ),
    )
    op.create_index(
        "ix_document_entity_resolutions_document_id",
        "document_entity_resolutions",
        ["document_id"],
    )
    op.create_index(
        "ix_document_entity_resolutions_status",
        "document_entity_resolutions",
        ["resolution_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_document_entity_resolutions_status", table_name="document_entity_resolutions")
    op.drop_index(
        "ix_document_entity_resolutions_document_id",
        table_name="document_entity_resolutions",
    )
    op.drop_table("document_entity_resolutions")
    op.drop_index("ix_document_metadata_organization_id", table_name="document_metadata")
    op.drop_index("ix_document_metadata_status", table_name="document_metadata")
    op.drop_table("document_metadata")
