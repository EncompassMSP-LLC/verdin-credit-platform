"""Human-gated agent supervised loop audit table.

Revision ID: 047_agent_supervised_loops
Revises: 046_stripe_invoice_pdf
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "047_agent_supervised_loops"
down_revision: str | None = "046_stripe_invoice_pdf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE agent_supervised_loop_status AS ENUM "
        "('pending_approval', 'completed', 'rejected', 'failed')"
    )

    op.create_table(
        "agent_supervised_loop_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_invocation_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tool_kind", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "completed",
                "rejected",
                "failed",
                name="agent_supervised_loop_status",
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
            ["tool_invocation_request_id"],
            ["agent_tool_invocation_requests.id"],
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_supervised_loop_runs_org_requested",
        "agent_supervised_loop_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_agent_supervised_loop_runs_tool_request",
        "agent_supervised_loop_runs",
        ["tool_invocation_request_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_supervised_loop_runs_tool_request",
        table_name="agent_supervised_loop_runs",
    )
    op.drop_index(
        "ix_agent_supervised_loop_runs_org_requested",
        table_name="agent_supervised_loop_runs",
    )
    op.drop_table("agent_supervised_loop_runs")
    op.execute("DROP TYPE agent_supervised_loop_status")
