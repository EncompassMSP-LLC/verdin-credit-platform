"""Admin-gated SAML passwordless enrollment audit table.

Revision ID: 058_saml_passwordless_enrollment
Revises: 057_stripe_charge_retry
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "058_saml_passwordless_enrollment"
down_revision: str | None = "057_stripe_charge_retry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE saml_passwordless_enrollment_run_status AS ENUM "
        "('pending_approval', 'enrolled', 'rejected', 'failed')"
    )
    op.create_table(
        "saml_passwordless_enrollment_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("saml_automated_rotation_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "enrolled",
                "rejected",
                "failed",
                name="saml_passwordless_enrollment_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("enrollment_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=True),
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
            ["saml_automated_rotation_run_id"],
            ["saml_automated_rotation_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_saml_passwordless_enrollment_runs_org_requested",
        "saml_passwordless_enrollment_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_saml_passwordless_enrollment_runs_automated_rotation_run",
        "saml_passwordless_enrollment_runs",
        ["saml_automated_rotation_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_saml_passwordless_enrollment_runs_automated_rotation_run",
        table_name="saml_passwordless_enrollment_runs",
    )
    op.drop_index(
        "ix_saml_passwordless_enrollment_runs_org_requested",
        table_name="saml_passwordless_enrollment_runs",
    )
    op.drop_table("saml_passwordless_enrollment_runs")
    op.execute("DROP TYPE saml_passwordless_enrollment_run_status")
