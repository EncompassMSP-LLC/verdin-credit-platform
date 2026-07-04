"""Billing invoice collection run audit table.

Revision ID: 036_billing_invoice_collection_runs
Revises: 035_agent_observability_runs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "036_billing_invoice_collection"
down_revision: str | None = "035_agent_observability_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE billing_invoice_collection_run_kind AS ENUM ('invoice_pdf', 'payment_reminder')"
    )
    op.execute(
        "CREATE TYPE billing_invoice_collection_trigger_source AS ENUM ('manual', 'scheduled')"
    )
    op.execute(
        "CREATE TYPE billing_invoice_collection_run_status AS ENUM ('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "billing_invoice_collection_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "run_kind",
            postgresql.ENUM(
                "invoice_pdf",
                "payment_reminder",
                name="billing_invoice_collection_run_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="billing_invoice_collection_trigger_source",
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
                name="billing_invoice_collection_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("invoices_pdf_generated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payment_reminders_queued", sa.Integer(), nullable=False, server_default="0"),
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
        "ix_billing_invoice_collection_runs_org_started",
        "billing_invoice_collection_runs",
        ["organization_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_billing_invoice_collection_runs_org_started",
        table_name="billing_invoice_collection_runs",
    )
    op.drop_table("billing_invoice_collection_runs")
    op.execute("DROP TYPE billing_invoice_collection_run_status")
    op.execute("DROP TYPE billing_invoice_collection_trigger_source")
    op.execute("DROP TYPE billing_invoice_collection_run_kind")
