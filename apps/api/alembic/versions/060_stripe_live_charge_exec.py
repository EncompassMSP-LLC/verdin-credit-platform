"""Admin-gated Stripe live charge retry execution audit table.

Revision ID: 060_stripe_live_charge_exec
Revises: 059_bureau_unsupervised_refiling
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "060_stripe_live_charge_exec"
down_revision: str | None = "059_bureau_unsupervised_refiling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE stripe_live_charge_retry_execution_run_status AS ENUM "
        "('pending_approval', 'executed', 'rejected', 'failed')"
    )
    op.create_table(
        "stripe_live_charge_retry_execution_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_charge_retry_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "executed",
                "rejected",
                "failed",
                name="stripe_live_charge_retry_execution_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("execution_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["stripe_charge_retry_run_id"],
            ["stripe_charge_retry_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stripe_live_charge_retry_execution_runs_org_requested",
        "stripe_live_charge_retry_execution_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_stripe_live_charge_retry_execution_runs_charge_retry_run",
        "stripe_live_charge_retry_execution_runs",
        ["stripe_charge_retry_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stripe_live_charge_retry_execution_runs_charge_retry_run",
        table_name="stripe_live_charge_retry_execution_runs",
    )
    op.drop_index(
        "ix_stripe_live_charge_retry_execution_runs_org_requested",
        table_name="stripe_live_charge_retry_execution_runs",
    )
    op.drop_table("stripe_live_charge_retry_execution_runs")
    op.execute("DROP TYPE stripe_live_charge_retry_execution_run_status")
