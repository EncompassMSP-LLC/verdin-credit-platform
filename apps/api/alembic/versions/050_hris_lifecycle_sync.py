"""Admin-gated HRIS lifecycle sync audit table.

Revision ID: 050_hris_lifecycle_sync
Revises: 049_stripe_tax_calculation
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "050_hris_lifecycle_sync"
down_revision: str | None = "049_stripe_tax_calculation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE hris_lifecycle_sync_run_status AS ENUM "
        "('pending_approval', 'completed', 'rejected', 'failed')"
    )
    op.create_table(
        "hris_lifecycle_sync_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "hris_bidirectional_sync_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hris_bidirectional_sync_runs.id"),
            nullable=False,
        ),
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
            "status",
            postgresql.ENUM(
                "pending_approval",
                "completed",
                "rejected",
                "failed",
                name="hris_lifecycle_sync_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("lifecycle_summary", sa.Text(), nullable=False),
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
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_hris_lifecycle_sync_runs_org_requested",
        "hris_lifecycle_sync_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_hris_lifecycle_sync_runs_bidirectional_run",
        "hris_lifecycle_sync_runs",
        ["hris_bidirectional_sync_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_hris_lifecycle_sync_runs_bidirectional_run",
        table_name="hris_lifecycle_sync_runs",
    )
    op.drop_index(
        "ix_hris_lifecycle_sync_runs_org_requested",
        table_name="hris_lifecycle_sync_runs",
    )
    op.drop_table("hris_lifecycle_sync_runs")
    op.execute("DROP TYPE hris_lifecycle_sync_run_status")
