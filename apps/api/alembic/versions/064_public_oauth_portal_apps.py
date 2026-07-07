"""Public OAuth developer portal app audit table.

Revision ID: 064_public_oauth_portal_apps
Revises: 063_bureau_live_api_audit
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "064_public_oauth_portal_apps"
down_revision: str | None = "063_bureau_live_api_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE oauth_developer_app_status AS ENUM "
        "('pending_approval', 'approved', 'revoked', 'failed')"
    )
    op.create_table(
        "oauth_developer_apps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("redirect_uri", sa.String(length=1024), nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "approved",
                "revoked",
                "failed",
                name="oauth_developer_app_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_oauth_developer_apps_org_requested",
        "oauth_developer_apps",
        ["organization_id", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_oauth_developer_apps_org_requested", table_name="oauth_developer_apps")
    op.drop_table("oauth_developer_apps")
    op.execute("DROP TYPE oauth_developer_app_status")
