"""Admin-gated Stripe tax calculation audit table.

Revision ID: 049_stripe_tax_calculation
Revises: 048_bureau_live_api
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "049_stripe_tax_calculation"
down_revision: str | None = "048_bureau_live_api"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE stripe_tax_calculation_status AS ENUM "
        "('pending_approval', 'calculated', 'rejected', 'failed')"
    )
    op.create_table(
        "stripe_tax_calculation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "invoice_pdf_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stripe_invoice_pdf_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "calculated",
                "rejected",
                "failed",
                name="stripe_tax_calculation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("calculation_summary", sa.Text(), nullable=False),
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
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_stripe_tax_calculation_runs_org_requested",
        "stripe_tax_calculation_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_stripe_tax_calculation_runs_pdf_run",
        "stripe_tax_calculation_runs",
        ["invoice_pdf_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stripe_tax_calculation_runs_pdf_run",
        table_name="stripe_tax_calculation_runs",
    )
    op.drop_index(
        "ix_stripe_tax_calculation_runs_org_requested",
        table_name="stripe_tax_calculation_runs",
    )
    op.drop_table("stripe_tax_calculation_runs")
    op.execute("DROP TYPE stripe_tax_calculation_status")
