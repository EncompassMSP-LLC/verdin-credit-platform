"""Admin-gated agent unsupervised loop audit table.

Revision ID: 051_agent_unsupervised_loops
Revises: 050_hris_lifecycle_sync
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "051_agent_unsupervised_loops"
down_revision: str | None = "050_hris_lifecycle_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE agent_unsupervised_loop_status AS ENUM "
        "('pending_approval', 'completed', 'rejected', 'failed')"
    )
    op.create_table(
        "agent_unsupervised_loop_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_supervised_loop_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tool_kind", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "completed",
                "rejected",
                "failed",
                name="agent_unsupervised_loop_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("loop_summary", sa.Text(), nullable=False),
        sa.Column("steps_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["agent_supervised_loop_run_id"],
            ["agent_supervised_loop_runs.id"],
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_unsupervised_loop_runs_org_requested",
        "agent_unsupervised_loop_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_agent_unsupervised_loop_runs_supervised_run",
        "agent_unsupervised_loop_runs",
        ["agent_supervised_loop_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_unsupervised_loop_runs_supervised_run",
        table_name="agent_unsupervised_loop_runs",
    )
    op.drop_index(
        "ix_agent_unsupervised_loop_runs_org_requested",
        table_name="agent_unsupervised_loop_runs",
    )
    op.drop_table("agent_unsupervised_loop_runs")
    op.execute("DROP TYPE agent_unsupervised_loop_status")
