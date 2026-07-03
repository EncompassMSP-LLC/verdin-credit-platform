"""Organization billing tables.

Revision ID: 022_organization_billing
Revises: 021_user_identity_enrollment
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "022_organization_billing"
down_revision: str | None = "021_user_identity_enrollment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE subscription_status AS ENUM "
        "('none', 'active', 'trialing', 'past_due', 'canceled', 'incomplete', 'unpaid')"
    )
    op.execute(
        "CREATE TYPE billing_webhook_event_status AS ENUM ('processed', 'ignored', 'failed')"
    )

    op.create_table(
        "organization_billing_accounts",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column(
            "subscription_status",
            postgresql.ENUM(
                "none",
                "active",
                "trialing",
                "past_due",
                "canceled",
                "incomplete",
                "unpaid",
                name="subscription_status",
                create_type=False,
            ),
            nullable=False,
            server_default="none",
        ),
        sa.Column("price_id", sa.String(length=255), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("organization_id"),
        sa.UniqueConstraint("stripe_customer_id"),
        sa.UniqueConstraint("stripe_subscription_id"),
    )

    op.create_table(
        "billing_webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "processed",
                "ignored",
                "failed",
                name="billing_webhook_event_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_event_id", name="uq_billing_webhook_stripe_event_id"),
    )
    op.create_index(
        "ix_billing_webhook_events_org_created",
        "billing_webhook_events",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_billing_webhook_events_org_created", table_name="billing_webhook_events")
    op.drop_table("billing_webhook_events")
    op.drop_table("organization_billing_accounts")
    op.execute("DROP TYPE billing_webhook_event_status")
    op.execute("DROP TYPE subscription_status")
