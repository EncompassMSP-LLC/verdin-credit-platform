"""Alembic migration: borrower portal in-app notifications (LRP-302A).

Revision ID: 118_portal_notifications
Revises: 117_portal_credential_tokens
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "118_portal_notifications"
down_revision: str | None = "117_portal_credential_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "portal_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_portal_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column(
            "category",
            postgresql.ENUM(
                "system",
                "task",
                "dispute",
                "document",
                "workflow",
                name="notification_category",
                create_type=False,
            ),
            nullable=False,
            server_default="system",
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_module", sa.String(length=50), nullable=True),
        sa.Column("action_url", sa.String(length=500), nullable=True),
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
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["recipient_portal_user_id"], ["client_portal_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_portal_notifications_org_recipient_created",
        "portal_notifications",
        ["organization_id", "recipient_portal_user_id", "created_at"],
    )
    op.create_index(
        "ix_portal_notifications_org_recipient_unread",
        "portal_notifications",
        ["organization_id", "recipient_portal_user_id", "read_at"],
    )
    op.create_index(
        "ix_portal_notifications_org_client_created",
        "portal_notifications",
        ["organization_id", "client_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_portal_notifications_org_client_created",
        table_name="portal_notifications",
    )
    op.drop_index(
        "ix_portal_notifications_org_recipient_unread",
        table_name="portal_notifications",
    )
    op.drop_index(
        "ix_portal_notifications_org_recipient_created",
        table_name="portal_notifications",
    )
    op.drop_table("portal_notifications")
