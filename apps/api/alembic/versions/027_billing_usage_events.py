"""Billing usage event audit table for org-scoped metering scaffold.

Revision ID: 027_billing_usage_events
Revises: 026_user_phone_sms_delivery_logs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "027_billing_usage_events"
down_revision: str | None = "026_user_phone_sms_delivery_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "billing_usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="manual"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_billing_usage_events_org_metric",
        "billing_usage_events",
        ["organization_id", "metric_name"],
    )
    op.create_index(
        "ix_billing_usage_events_org_recorded_at",
        "billing_usage_events",
        ["organization_id", "recorded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_billing_usage_events_org_recorded_at", table_name="billing_usage_events")
    op.drop_index("ix_billing_usage_events_org_metric", table_name="billing_usage_events")
    op.drop_table("billing_usage_events")
