"""Admin-gated Stripe charge retry audit table.

Revision ID: 057_stripe_charge_retry
Revises: 056_bureau_refiling
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "057_stripe_charge_retry"
down_revision: str | None = "056_bureau_refiling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE stripe_charge_retry_run_status AS ENUM "
        "('pending_approval', 'retried', 'rejected', 'failed')"
    )
    op.create_table(
        "stripe_charge_retry_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_live_tax_api_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "retried",
                "rejected",
                "failed",
                name="stripe_charge_retry_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("retry_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retried_at", sa.DateTime(timezone=True), nullable=True),
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
            ["stripe_live_tax_api_run_id"],
            ["stripe_live_tax_api_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stripe_charge_retry_runs_org_requested",
        "stripe_charge_retry_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_stripe_charge_retry_runs_live_tax_run",
        "stripe_charge_retry_runs",
        ["stripe_live_tax_api_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stripe_charge_retry_runs_live_tax_run",
        table_name="stripe_charge_retry_runs",
    )
    op.drop_index(
        "ix_stripe_charge_retry_runs_org_requested",
        table_name="stripe_charge_retry_runs",
    )
    op.drop_table("stripe_charge_retry_runs")
    op.execute("DROP TYPE stripe_charge_retry_run_status")
