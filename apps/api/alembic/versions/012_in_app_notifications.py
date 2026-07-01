"""In-app notifications table.

Revision ID: 012_in_app_notifications
Revises: 011_dispute_letter_drafts
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "012_in_app_notifications"
down_revision: str | None = "011_dispute_letter_drafts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE notification_category AS ENUM ("
        "'system', 'task', 'dispute', 'document', 'workflow'"
        ")"
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_user_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["recipient_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notifications_org_recipient_created",
        "notifications",
        ["organization_id", "recipient_user_id", "created_at"],
    )
    op.create_index(
        "ix_notifications_org_recipient_unread",
        "notifications",
        ["organization_id", "recipient_user_id", "read_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_org_recipient_unread", table_name="notifications")
    op.drop_index("ix_notifications_org_recipient_created", table_name="notifications")
    op.drop_table("notifications")
    op.execute("DROP TYPE notification_category")
