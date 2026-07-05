"""HRIS bidirectional sync run audit table.

Revision ID: 040_hris_bidirectional_sync
Revises: 039_agent_execution
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "040_hris_bidirectional_sync"
down_revision: str | None = "039_agent_execution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE hris_bidirectional_sync_run_kind AS ENUM "
        "('employees_inbound', 'employees_outbound')"
    )
    op.execute("CREATE TYPE hris_bidirectional_sync_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute(
        "CREATE TYPE hris_bidirectional_sync_run_status AS ENUM "
        "('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "hris_bidirectional_sync_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "run_kind",
            postgresql.ENUM(
                "employees_inbound",
                "employees_outbound",
                name="hris_bidirectional_sync_run_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="hris_bidirectional_sync_trigger_source",
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
                name="hris_bidirectional_sync_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("records_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_skipped", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_hris_bidirectional_sync_runs_org_started",
        "hris_bidirectional_sync_runs",
        ["organization_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_hris_bidirectional_sync_runs_org_started",
        table_name="hris_bidirectional_sync_runs",
    )
    op.drop_table("hris_bidirectional_sync_runs")
    op.execute("DROP TYPE hris_bidirectional_sync_run_status")
    op.execute("DROP TYPE hris_bidirectional_sync_trigger_source")
    op.execute("DROP TYPE hris_bidirectional_sync_run_kind")
