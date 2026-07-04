"""Agent observability run audit table.

Revision ID: 035_agent_observability_runs
Revises: 034_sms_marketing_campaign_runs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "035_agent_observability_runs"
down_revision: str | None = "034_sms_marketing_campaign_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE agent_observability_kind AS ENUM ('case_review', 'document_triage', 'dispute_prep')"
    )
    op.execute("CREATE TYPE agent_observability_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute(
        "CREATE TYPE agent_observability_run_status AS ENUM ('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "agent_observability_runs",
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
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="agent_observability_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "running",
                "completed",
                "failed",
                name="agent_observability_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("steps_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steps_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_observability_runs_org_started",
        "agent_observability_runs",
        ["organization_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_observability_runs_org_started",
        table_name="agent_observability_runs",
    )
    op.drop_table("agent_observability_runs")
    op.execute("DROP TYPE agent_observability_run_status")
    op.execute("DROP TYPE agent_observability_trigger_source")
    op.execute("DROP TYPE agent_observability_kind")
