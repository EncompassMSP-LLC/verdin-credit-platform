"""Add dispute_responses audit table (Phase 10 dispute response intake).

Revision ID: 087_dispute_responses
Revises: 086_it_readiness_runs
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "087_dispute_responses"
down_revision: str | None = "086_it_readiness_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OUTCOMES = ("deleted", "verified", "updated", "corrected", "no_response", "rejected")
_METHODS = ("mail", "portal", "phone", "email", "other")


def upgrade() -> None:
    outcome_enum = postgresql.ENUM(*_OUTCOMES, name="dispute_response_outcome")
    method_enum = postgresql.ENUM(*_METHODS, name="dispute_response_method")
    bind = op.get_bind()
    outcome_enum.create(bind, checkfirst=True)
    method_enum.create(bind, checkfirst=True)

    op.create_table(
        "dispute_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dispute_letter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "outcome",
            postgresql.ENUM(*_OUTCOMES, name="dispute_response_outcome", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "response_method",
            postgresql.ENUM(*_METHODS, name="dispute_response_method", create_type=False),
            nullable=False,
        ),
        sa.Column("response_date", sa.Date(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["dispute_letter_id"], ["dispute_letters.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dispute_responses_organization_id", "dispute_responses", ["organization_id"]
    )
    op.create_index("ix_dispute_responses_case_id", "dispute_responses", ["case_id"])
    op.create_index("ix_dispute_responses_account_id", "dispute_responses", ["account_id"])
    op.create_index(
        "ix_dispute_responses_dispute_letter_id", "dispute_responses", ["dispute_letter_id"]
    )
    op.create_index("ix_dispute_responses_document_id", "dispute_responses", ["document_id"])
    op.create_index("ix_dispute_responses_outcome", "dispute_responses", ["outcome"])
    op.create_index(
        "ix_dispute_responses_account_recorded_at",
        "dispute_responses",
        ["account_id", "recorded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_dispute_responses_account_recorded_at", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_outcome", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_document_id", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_dispute_letter_id", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_account_id", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_case_id", table_name="dispute_responses")
    op.drop_index("ix_dispute_responses_organization_id", table_name="dispute_responses")
    op.drop_table("dispute_responses")

    bind = op.get_bind()
    postgresql.ENUM(*_METHODS, name="dispute_response_method").drop(bind, checkfirst=True)
    postgresql.ENUM(*_OUTCOMES, name="dispute_response_outcome").drop(bind, checkfirst=True)
