"""Alembic migration: weekly partner status digests (LRP-207).

Revision ID: 109_weekly_partner_digest
Revises: 108_partner_nurture_drip
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "109_weekly_partner_digest"
down_revision: str | None = "108_partner_nurture_drip"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "partner_weekly_digest_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "partnership_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_partnerships.id"),
            nullable=False,
        ),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "marketing_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("send_weekday", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "updated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "partnership_id",
            "recipient_email",
            name="uq_partner_weekly_digest_sub_email",
        ),
    )
    op.create_index(
        "ix_partner_weekly_digest_subscriptions_organization_id",
        "partner_weekly_digest_subscriptions",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_weekly_digest_subscriptions_partnership_id",
        "partner_weekly_digest_subscriptions",
        ["partnership_id"],
    )

    op.create_table(
        "partner_weekly_digest_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "partnership_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_partnerships.id"),
            nullable=False,
        ),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_weekly_digest_subscriptions.id"),
            nullable=False,
        ),
        sa.Column("week_key", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "subscription_id",
            "week_key",
            name="uq_partner_weekly_digest_run_sub_week",
        ),
    )
    op.create_index(
        "ix_partner_weekly_digest_runs_organization_id",
        "partner_weekly_digest_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_weekly_digest_runs_partnership_id",
        "partner_weekly_digest_runs",
        ["partnership_id"],
    )
    op.create_index(
        "ix_partner_weekly_digest_runs_subscription_id",
        "partner_weekly_digest_runs",
        ["subscription_id"],
    )
    op.create_index(
        "ix_partner_weekly_digest_runs_week_key",
        "partner_weekly_digest_runs",
        ["week_key"],
    )


def downgrade() -> None:
    op.drop_index("ix_partner_weekly_digest_runs_week_key", table_name="partner_weekly_digest_runs")
    op.drop_index(
        "ix_partner_weekly_digest_runs_subscription_id",
        table_name="partner_weekly_digest_runs",
    )
    op.drop_index(
        "ix_partner_weekly_digest_runs_partnership_id",
        table_name="partner_weekly_digest_runs",
    )
    op.drop_index(
        "ix_partner_weekly_digest_runs_organization_id",
        table_name="partner_weekly_digest_runs",
    )
    op.drop_table("partner_weekly_digest_runs")
    op.drop_index(
        "ix_partner_weekly_digest_subscriptions_partnership_id",
        table_name="partner_weekly_digest_subscriptions",
    )
    op.drop_index(
        "ix_partner_weekly_digest_subscriptions_organization_id",
        table_name="partner_weekly_digest_subscriptions",
    )
    op.drop_table("partner_weekly_digest_subscriptions")
