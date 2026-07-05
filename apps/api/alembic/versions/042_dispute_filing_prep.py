"""Compliance-gated dispute filing prep audit table.

Revision ID: 042_dispute_filing_prep
Revises: 041_llm_dispute_draft_augment
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "042_dispute_filing_prep"
down_revision: str | None = "041_llm_dispute_draft_augment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE dispute_filing_prep_status AS ENUM "
        "('pending_approval', 'prepared', 'rejected', 'failed')"
    )

    op.create_table(
        "dispute_filing_prep_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "prepared",
                "rejected",
                "failed",
                name="dispute_filing_prep_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("prep_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dispute_filing_prep_runs_org_requested",
        "dispute_filing_prep_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_dispute_filing_prep_runs_account",
        "dispute_filing_prep_runs",
        ["account_id", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_dispute_filing_prep_runs_account", table_name="dispute_filing_prep_runs")
    op.drop_index(
        "ix_dispute_filing_prep_runs_org_requested", table_name="dispute_filing_prep_runs"
    )
    op.drop_table("dispute_filing_prep_runs")
    op.execute("DROP TYPE dispute_filing_prep_status")
