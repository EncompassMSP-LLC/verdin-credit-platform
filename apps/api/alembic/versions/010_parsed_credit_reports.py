"""Persist structured parsed credit reports.

Revision ID: 010_parsed_credit_reports
Revises: 009_task_management
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "010_parsed_credit_reports"
down_revision: str | None = "009_task_management"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_parsed_credit_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("bureau", sa.String(length=50), nullable=False),
        sa.Column("parser_name", sa.String(length=50), nullable=False),
        sa.Column("parser_confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("parsed_report", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_partial", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", name="uq_document_parsed_credit_reports_document_id"),
    )
    op.create_index(
        "ix_document_parsed_credit_reports_organization_id",
        "document_parsed_credit_reports",
        ["organization_id"],
    )
    op.create_index(
        "ix_document_parsed_credit_reports_parser_name",
        "document_parsed_credit_reports",
        ["parser_name"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_parsed_credit_reports_parser_name",
        table_name="document_parsed_credit_reports",
    )
    op.drop_index(
        "ix_document_parsed_credit_reports_organization_id",
        table_name="document_parsed_credit_reports",
    )
    op.drop_table("document_parsed_credit_reports")
