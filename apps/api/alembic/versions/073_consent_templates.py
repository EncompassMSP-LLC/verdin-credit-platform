"""Consent document templates and template key on consent records.

Revision ID: 073_consent_templates
Revises: 072_consent_signatures
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "073_consent_templates"
down_revision: str | None = "072_consent_signatures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consent_document_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_key", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column(
            "merge_field_defaults",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "legal_review_status",
            sa.String(length=20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "template_key",
            name="uq_consent_document_templates_org_key",
        ),
    )
    op.create_index(
        "ix_consent_document_templates_organization_id",
        "consent_document_templates",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_consent_document_templates_template_key",
        "consent_document_templates",
        ["template_key"],
        unique=False,
    )

    op.add_column(
        "consent_records",
        sa.Column("document_template_key", sa.String(length=50), nullable=True),
    )
    op.create_index(
        "ix_consent_records_document_template_key",
        "consent_records",
        ["document_template_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_consent_records_document_template_key", table_name="consent_records")
    op.drop_column("consent_records", "document_template_key")
    op.drop_index(
        "ix_consent_document_templates_template_key",
        table_name="consent_document_templates",
    )
    op.drop_index(
        "ix_consent_document_templates_organization_id",
        table_name="consent_document_templates",
    )
    op.drop_table("consent_document_templates")
