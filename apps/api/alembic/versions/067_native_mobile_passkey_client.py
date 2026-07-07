"""Admin-gated native mobile passkey client audit table.

Revision ID: 067_native_mobile_passkey_client
Revises: 066_mobile_passkey_readiness
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "067_native_mobile_passkey_client"
down_revision: str | None = "066_mobile_passkey_readiness"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE native_mobile_passkey_client_run_status AS ENUM "
        "('pending_approval', 'approved', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "native_mobile_passkey_client_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mobile_passkey_readiness_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "approved",
                "rejected",
                "failed",
                name="native_mobile_passkey_client_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("client_summary", sa.Text(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
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
            ["mobile_passkey_readiness_run_id"],
            ["mobile_passkey_readiness_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_native_mobile_passkey_client_runs_org_requested",
        "native_mobile_passkey_client_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_native_mobile_passkey_client_runs_readiness_run",
        "native_mobile_passkey_client_runs",
        ["mobile_passkey_readiness_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_native_mobile_passkey_client_runs_readiness_run",
        table_name="native_mobile_passkey_client_runs",
    )
    op.drop_index(
        "ix_native_mobile_passkey_client_runs_org_requested",
        table_name="native_mobile_passkey_client_runs",
    )
    op.drop_table("native_mobile_passkey_client_runs")
    op.execute("DROP TYPE native_mobile_passkey_client_run_status")
