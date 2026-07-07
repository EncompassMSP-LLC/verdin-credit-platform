"""Admin-gated OAuth marketplace publishing audit table.

Revision ID: 068_oauth_marketplace_publishing
Revises: 067_native_mobile_passkey_client
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "068_oauth_marketplace_publishing"
down_revision: str | None = "067_native_mobile_passkey_client"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE oauth_marketplace_publishing_run_status AS ENUM "
        "('pending_approval', 'approved', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "oauth_marketplace_publishing_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("oauth_developer_app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "approved",
                "rejected",
                "failed",
                name="oauth_marketplace_publishing_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("publishing_summary", sa.Text(), nullable=False),
        sa.Column("marketplace_listing_slug", sa.String(length=255), nullable=False),
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
            ["oauth_developer_app_id"],
            ["oauth_developer_apps.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_oauth_marketplace_publishing_runs_org_requested",
        "oauth_marketplace_publishing_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_oauth_marketplace_publishing_runs_oauth_app",
        "oauth_marketplace_publishing_runs",
        ["oauth_developer_app_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_oauth_marketplace_publishing_runs_oauth_app",
        table_name="oauth_marketplace_publishing_runs",
    )
    op.drop_index(
        "ix_oauth_marketplace_publishing_runs_org_requested",
        table_name="oauth_marketplace_publishing_runs",
    )
    op.drop_table("oauth_marketplace_publishing_runs")
    op.execute("DROP TYPE oauth_marketplace_publishing_run_status")
