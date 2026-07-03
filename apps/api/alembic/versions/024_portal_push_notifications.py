"""Portal push notification tables.

Revision ID: 024_portal_push_notifications
Revises: 023_retention_enforcement_runs
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "024_portal_push_notifications"
down_revision: str | None = "023_retention_enforcement_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE portal_push_delivery_status AS ENUM ('sent', 'failed', 'skipped')")

    op.create_table(
        "portal_push_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portal_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh_key", sa.Text(), nullable=False),
        sa.Column("auth_key", sa.Text(), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.ForeignKeyConstraint(["portal_user_id"], ["client_portal_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portal_user_id", "endpoint", name="uq_portal_push_subscription"),
    )
    op.create_index(
        "ix_portal_push_subscriptions_organization_id",
        "portal_push_subscriptions",
        ["organization_id"],
    )
    op.create_index(
        "ix_portal_push_subscriptions_portal_user_id",
        "portal_push_subscriptions",
        ["portal_user_id"],
    )

    op.create_table(
        "portal_push_delivery_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portal_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("thread_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "sent",
                "failed",
                "skipped",
                name="portal_push_delivery_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
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
        sa.ForeignKeyConstraint(["portal_user_id"], ["client_portal_users.id"]),
        sa.ForeignKeyConstraint(["subscription_id"], ["portal_push_subscriptions.id"]),
        sa.ForeignKeyConstraint(["thread_message_id"], ["thread_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_portal_push_delivery_logs_organization_id",
        "portal_push_delivery_logs",
        ["organization_id"],
    )
    op.create_index(
        "ix_portal_push_delivery_logs_portal_user_id",
        "portal_push_delivery_logs",
        ["portal_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_portal_push_delivery_logs_portal_user_id", table_name="portal_push_delivery_logs"
    )
    op.drop_index(
        "ix_portal_push_delivery_logs_organization_id",
        table_name="portal_push_delivery_logs",
    )
    op.drop_table("portal_push_delivery_logs")
    op.drop_index(
        "ix_portal_push_subscriptions_portal_user_id",
        table_name="portal_push_subscriptions",
    )
    op.drop_index(
        "ix_portal_push_subscriptions_organization_id",
        table_name="portal_push_subscriptions",
    )
    op.drop_table("portal_push_subscriptions")
    op.execute("DROP TYPE portal_push_delivery_status")
