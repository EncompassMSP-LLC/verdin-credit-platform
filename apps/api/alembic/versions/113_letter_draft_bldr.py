"""Alembic migration: Intelligent Letter Draft Builder (LRP-406).

Revision ID: 113_letter_draft_bldr
Revises: 112_faq_kb_retrieval
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "113_letter_draft_bldr"
down_revision: str | None = "112_faq_kb_retrieval"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE letter_draft_workflow_status AS ENUM ("
        "'ai_draft_created', 'staff_review', 'client_review', 'approved', "
        "'ready_to_send', 'sent_recorded', 'delivery_confirmed', 'response_received')"
    )
    op.create_table(
        "intelligent_letter_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_kind", sa.String(length=64), nullable=False),
        sa.Column(
            "workflow_status",
            postgresql.ENUM(
                "ai_draft_created",
                "staff_review",
                "client_review",
                "approved",
                "ready_to_send",
                "sent_recorded",
                "delivery_confirmed",
                "response_received",
                name="letter_draft_workflow_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("issue_source_id", sa.String(length=128), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "sections",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("full_text", sa.Text(), nullable=False),
        sa.Column(
            "validation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "claim_warnings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "send_guardrails",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "versions_history",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("disclaimer", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_intelligent_letter_drafts_organization_id",
        "intelligent_letter_drafts",
        ["organization_id"],
    )
    op.create_index(
        "ix_intelligent_letter_drafts_case_id",
        "intelligent_letter_drafts",
        ["case_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_intelligent_letter_drafts_case_id", table_name="intelligent_letter_drafts")
    op.drop_index(
        "ix_intelligent_letter_drafts_organization_id",
        table_name="intelligent_letter_drafts",
    )
    op.drop_table("intelligent_letter_drafts")
    op.execute("DROP TYPE letter_draft_workflow_status")
