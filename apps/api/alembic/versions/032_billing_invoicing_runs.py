"""Billing invoicing and dunning run audit table.

Revision ID: 032_billing_invoicing_runs
Revises: 031_batch_document_summary_runs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "032_billing_invoicing_runs"
down_revision: str | None = "031_batch_document_summary_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE billing_invoicing_run_kind AS ENUM ('invoice_cycle', 'dunning_reminder')"
    )
    op.execute("CREATE TYPE billing_invoicing_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute(
        "CREATE TYPE billing_invoicing_run_status AS ENUM ('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "billing_invoicing_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "run_kind",
            postgresql.ENUM(
                "invoice_cycle",
                "dunning_reminder",
                name="billing_invoicing_run_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="billing_invoicing_trigger_source",
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
                name="billing_invoicing_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("invoices_prepared", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dunning_reminders_queued", sa.Integer(), nullable=False, server_default="0"),
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
        "ix_billing_invoicing_runs_org_started",
        "billing_invoicing_runs",
        ["organization_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_billing_invoicing_runs_org_started", table_name="billing_invoicing_runs")
    op.drop_table("billing_invoicing_runs")
    op.execute("DROP TYPE billing_invoicing_run_status")
    op.execute("DROP TYPE billing_invoicing_trigger_source")
    op.execute("DROP TYPE billing_invoicing_run_kind")
