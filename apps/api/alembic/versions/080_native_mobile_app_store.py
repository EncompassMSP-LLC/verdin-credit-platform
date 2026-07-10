"""Native mobile app store distribution audit table.

Revision ID: 080_native_mobile_app_store
Revises: 079_public_oauth_listings
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "080_native_mobile_app_store"
down_revision: str | None = "079_public_oauth_listings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE native_mobile_app_store_distribution_run_status AS ENUM "
        "('pending_approval', 'ready', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "native_mobile_app_store_distribution_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "native_mobile_passkey_client_run_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "ready",
                "rejected",
                "failed",
                name="native_mobile_app_store_distribution_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("distribution_summary", sa.Text(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("store_target", sa.String(length=50), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True),
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
            ["native_mobile_passkey_client_run_id"],
            ["native_mobile_passkey_client_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_native_mobile_app_store_runs_org_requested",
        "native_mobile_app_store_distribution_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_native_mobile_app_store_runs_passkey_client",
        "native_mobile_app_store_distribution_runs",
        ["native_mobile_passkey_client_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_native_mobile_app_store_runs_passkey_client",
        table_name="native_mobile_app_store_distribution_runs",
    )
    op.drop_index(
        "ix_native_mobile_app_store_runs_org_requested",
        table_name="native_mobile_app_store_distribution_runs",
    )
    op.drop_table("native_mobile_app_store_distribution_runs")
    op.execute("DROP TYPE native_mobile_app_store_distribution_run_status")
