"""Admin-gated HRIS passwordless UI audit table.

Revision ID: 061_hris_passwordless_ui
Revises: 060_stripe_live_charge_exec
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "061_hris_passwordless_ui"
down_revision: str | None = "060_stripe_live_charge_exec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE hris_passwordless_ui_run_status AS ENUM "
        "('pending_approval', 'approved', 'rejected', 'failed')"
    )
    op.create_table(
        "hris_passwordless_ui_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "saml_passwordless_enrollment_run_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "approved",
                "rejected",
                "failed",
                name="hris_passwordless_ui_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("ui_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
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
            ["saml_passwordless_enrollment_run_id"],
            ["saml_passwordless_enrollment_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_hris_passwordless_ui_runs_org_requested",
        "hris_passwordless_ui_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_hris_passwordless_ui_runs_enrollment_run",
        "hris_passwordless_ui_runs",
        ["saml_passwordless_enrollment_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_hris_passwordless_ui_runs_enrollment_run",
        table_name="hris_passwordless_ui_runs",
    )
    op.drop_index(
        "ix_hris_passwordless_ui_runs_org_requested",
        table_name="hris_passwordless_ui_runs",
    )
    op.drop_table("hris_passwordless_ui_runs")
    op.execute("DROP TYPE hris_passwordless_ui_run_status")
