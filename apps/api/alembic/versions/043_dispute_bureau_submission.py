"""Admin-gated dispute bureau submission audit table.

Revision ID: 043_dispute_bureau_submission
Revises: 042_dispute_filing_prep
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "043_dispute_bureau_submission"
down_revision: str | None = "042_dispute_filing_prep"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE dispute_bureau_submission_status AS ENUM "
        "('pending_approval', 'submitted', 'rejected', 'failed')"
    )

    op.create_table(
        "dispute_bureau_submission_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filing_prep_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "submitted",
                "rejected",
                "failed",
                name="dispute_bureau_submission_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("submission_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["filing_prep_run_id"], ["dispute_filing_prep_runs.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dispute_bureau_submission_runs_org_requested",
        "dispute_bureau_submission_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_dispute_bureau_submission_runs_prep_run",
        "dispute_bureau_submission_runs",
        ["filing_prep_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dispute_bureau_submission_runs_prep_run",
        table_name="dispute_bureau_submission_runs",
    )
    op.drop_index(
        "ix_dispute_bureau_submission_runs_org_requested",
        table_name="dispute_bureau_submission_runs",
    )
    op.drop_table("dispute_bureau_submission_runs")
    op.execute("DROP TYPE dispute_bureau_submission_status")
