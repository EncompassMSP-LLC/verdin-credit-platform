"""Operator-gated bureau live API invocation audit table.

Revision ID: 048_bureau_live_api
Revises: 047_agent_supervised_loops
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "048_bureau_live_api"
down_revision: str | None = "047_agent_supervised_loops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE bureau_live_api_run_status AS ENUM "
        "('pending_approval', 'invoked', 'rejected', 'failed')"
    )
    op.create_table(
        "bureau_live_api_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "bureau_submission_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dispute_bureau_submission_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "invoked",
                "rejected",
                "failed",
                name="bureau_live_api_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("invocation_summary", sa.Text(), nullable=False),
        sa.Column(
            "requested_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "approved_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "timeline_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("timeline_events.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_bureau_live_api_runs_org_requested",
        "bureau_live_api_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_bureau_live_api_runs_submission_run",
        "bureau_live_api_runs",
        ["bureau_submission_run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_bureau_live_api_runs_submission_run", table_name="bureau_live_api_runs")
    op.drop_index("ix_bureau_live_api_runs_org_requested", table_name="bureau_live_api_runs")
    op.drop_table("bureau_live_api_runs")
    op.execute("DROP TYPE bureau_live_api_run_status")
