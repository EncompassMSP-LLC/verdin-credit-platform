"""Human-gated agent execution step audit table.

Revision ID: 039_agent_execution
Revises: 038_sms_marketing_delivery
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "039_agent_execution"
down_revision: str | None = "038_sms_marketing_delivery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE agent_execution_step_status AS ENUM "
        "('pending_approval', 'executed', 'rejected', 'failed')"
    )

    op.create_table(
        "agent_execution_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "agent_kind",
            postgresql.ENUM(
                "case_review",
                "document_triage",
                "dispute_prep",
                name="agent_observability_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "executed",
                "rejected",
                "failed",
                name="agent_execution_step_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("step_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_execution_steps_org_requested",
        "agent_execution_steps",
        ["organization_id", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_agent_execution_steps_org_requested", table_name="agent_execution_steps")
    op.drop_table("agent_execution_steps")
    op.execute("DROP TYPE agent_execution_step_status")
