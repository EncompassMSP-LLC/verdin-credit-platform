"""Public OAuth marketplace listing audit table.

Revision ID: 079_public_oauth_listings
Revises: 078_unsupervised_filing_loops
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "079_public_oauth_listings"
down_revision: str | None = "078_unsupervised_filing_loops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE public_oauth_marketplace_listing_run_status AS ENUM "
        "('pending_approval', 'listed', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "public_oauth_marketplace_listing_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "oauth_marketplace_publishing_run_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("oauth_developer_app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "listed",
                "rejected",
                "failed",
                name="public_oauth_marketplace_listing_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("listing_summary", sa.Text(), nullable=False),
        sa.Column("marketplace_listing_slug", sa.String(length=255), nullable=False),
        sa.Column("public_listing_url", sa.String(length=500), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("listed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["oauth_marketplace_publishing_run_id"],
            ["oauth_marketplace_publishing_runs.id"],
        ),
        sa.ForeignKeyConstraint(["oauth_developer_app_id"], ["oauth_developer_apps.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_public_oauth_listing_runs_org_requested",
        "public_oauth_marketplace_listing_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_public_oauth_listing_runs_publishing",
        "public_oauth_marketplace_listing_runs",
        ["oauth_marketplace_publishing_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_public_oauth_listing_runs_publishing",
        table_name="public_oauth_marketplace_listing_runs",
    )
    op.drop_index(
        "ix_public_oauth_listing_runs_org_requested",
        table_name="public_oauth_marketplace_listing_runs",
    )
    op.drop_table("public_oauth_marketplace_listing_runs")
    op.execute("DROP TYPE public_oauth_marketplace_listing_run_status")
