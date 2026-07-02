"""User phone numbers and SMS delivery audit log table.

Revision ID: 026_user_phone_sms_delivery_logs
Revises: 025_reporting_materialized_views
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "026_user_phone_sms_delivery_logs"
down_revision: str | None = "025_reporting_materialized_views"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(length=50), nullable=True))

    op.execute("CREATE TYPE sms_delivery_status AS ENUM ('sent', 'failed')")

    op.create_table(
        "sms_delivery_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recipient_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recipient_phone", sa.String(length=50), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("sent", "failed", name="sms_delivery_status", create_type=False),
            nullable=False,
        ),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["recipient_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sent_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sms_delivery_logs_org_created",
        "sms_delivery_logs",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_sms_delivery_logs_org_created", table_name="sms_delivery_logs")
    op.drop_table("sms_delivery_logs")
    op.execute("DROP TYPE sms_delivery_status")
    op.drop_column("users", "phone_number")
