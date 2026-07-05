"""Admin-gated autonomous bureau filing audit table.

Revision ID: 052_autonomous_bureau_filing
Revises: 051_agent_unsupervised_loops
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "052_autonomous_bureau_filing"
down_revision: str | None = "051_agent_unsupervised_loops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE autonomous_bureau_filing_run_status AS ENUM "
        "('pending_approval', 'filed', 'rejected', 'failed')"
    )
    op.create_table(
        "autonomous_bureau_filing_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_live_api_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "filed",
                "rejected",
                "failed",
                name="autonomous_bureau_filing_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("filing_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("filed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["bureau_live_api_run_id"],
            ["bureau_live_api_runs.id"],
        ),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_autonomous_bureau_filing_runs_org_requested",
        "autonomous_bureau_filing_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_autonomous_bureau_filing_runs_live_api_run",
        "autonomous_bureau_filing_runs",
        ["bureau_live_api_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_autonomous_bureau_filing_runs_live_api_run",
        table_name="autonomous_bureau_filing_runs",
    )
    op.drop_index(
        "ix_autonomous_bureau_filing_runs_org_requested",
        table_name="autonomous_bureau_filing_runs",
    )
    op.drop_table("autonomous_bureau_filing_runs")
    op.execute("DROP TYPE autonomous_bureau_filing_run_status")
