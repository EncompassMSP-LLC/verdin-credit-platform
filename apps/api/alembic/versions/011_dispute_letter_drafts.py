"""Persist dispute letter drafts.

Revision ID: 011_dispute_letter_drafts
Revises: 010_parsed_credit_reports
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "011_dispute_letter_drafts"
down_revision: str | None = "010_parsed_credit_reports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE dispute_letter_status AS ENUM ("
        "'draft', 'review', 'approved', 'sent', 'void'"
        ")"
    )

    op.create_table(
        "dispute_letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_type", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "review",
                "approved",
                "sent",
                "void",
                name="dispute_letter_status",
                create_type=False,
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("template_id", sa.String(length=100), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("disputed_items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("requested_action", sa.Text(), nullable=False),
        sa.Column("evidence_checklist", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("compliance_notes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generated_by", sa.String(length=50), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dispute_letters_account_id", "dispute_letters", ["account_id"])
    op.create_index("ix_dispute_letters_case_id", "dispute_letters", ["case_id"])
    op.create_index("ix_dispute_letters_organization_id", "dispute_letters", ["organization_id"])
    op.create_index("ix_dispute_letters_status", "dispute_letters", ["status"])


def downgrade() -> None:
    op.drop_index("ix_dispute_letters_status", table_name="dispute_letters")
    op.drop_index("ix_dispute_letters_organization_id", table_name="dispute_letters")
    op.drop_index("ix_dispute_letters_case_id", table_name="dispute_letters")
    op.drop_index("ix_dispute_letters_account_id", table_name="dispute_letters")
    op.drop_table("dispute_letters")
    op.execute("DROP TYPE IF EXISTS dispute_letter_status")
