"""Alembic migration: FAQ/KB retrieval conversation audit (LRP-405).

Revision ID: 112_faq_kb_retrieval
Revises: 111_client_comm_prefs
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "112_faq_kb_retrieval"
down_revision: str | None = "111_client_comm_prefs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE faq_kb_audience AS ENUM ('borrower', 'lender', 'realtor', 'staff')")
    op.execute(
        "CREATE TYPE faq_kb_feedback_rating AS ENUM ('accurate', 'inaccurate', 'incomplete')"
    )
    op.create_table(
        "faq_kb_conversation_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "audience",
            postgresql.ENUM(
                "borrower",
                "lender",
                "realtor",
                "staff",
                name="faq_kb_audience",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("grounded", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("refused", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("refusal_reason", sa.String(length=64), nullable=True),
        sa.Column(
            "citations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "matched_article_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column(
            "feedback_rating",
            postgresql.ENUM(
                "accurate",
                "inaccurate",
                "incomplete",
                name="faq_kb_feedback_rating",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("feedback_note", sa.Text(), nullable=True),
        sa.Column("feedback_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["feedback_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_faq_kb_conversation_turns_organization_id",
        "faq_kb_conversation_turns",
        ["organization_id"],
    )
    op.create_index(
        "ix_faq_kb_conversation_turns_org_created",
        "faq_kb_conversation_turns",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_faq_kb_conversation_turns_org_created",
        table_name="faq_kb_conversation_turns",
    )
    op.drop_index(
        "ix_faq_kb_conversation_turns_organization_id",
        table_name="faq_kb_conversation_turns",
    )
    op.drop_table("faq_kb_conversation_turns")
    op.execute("DROP TYPE IF EXISTS faq_kb_feedback_rating")
    op.execute("DROP TYPE IF EXISTS faq_kb_audience")
