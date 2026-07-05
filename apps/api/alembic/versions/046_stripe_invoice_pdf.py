"""Admin-gated Stripe invoice PDF generation audit table.

Revision ID: 046_stripe_invoice_pdf
Revises: 045_saml_certificate_rotation
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "046_stripe_invoice_pdf"
down_revision: str | None = "045_saml_certificate_rotation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE stripe_invoice_pdf_status AS ENUM "
        "('pending_approval', 'generated', 'rejected', 'failed')"
    )

    op.create_table(
        "stripe_invoice_pdf_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "generated",
                "rejected",
                "failed",
                name="stripe_invoice_pdf_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("generation_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
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
            ["collection_run_id"],
            ["billing_invoice_collection_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stripe_invoice_pdf_runs_org_requested",
        "stripe_invoice_pdf_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_stripe_invoice_pdf_runs_collection_run",
        "stripe_invoice_pdf_runs",
        ["collection_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stripe_invoice_pdf_runs_collection_run",
        table_name="stripe_invoice_pdf_runs",
    )
    op.drop_index(
        "ix_stripe_invoice_pdf_runs_org_requested",
        table_name="stripe_invoice_pdf_runs",
    )
    op.drop_table("stripe_invoice_pdf_runs")
    op.execute("DROP TYPE stripe_invoice_pdf_status")
