"""Alembic migration: CRM automation rules (LRP-203).

Revision ID: 106_crm_automation_rules
Revises: 105_notification_matrix
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "106_crm_automation_rules"
down_revision: str | None = "105_notification_matrix"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

trigger_enum = postgresql.ENUM(
    "stage_enter",
    "referral_created",
    "task_overdue",
    "score_band_change",
    "document_uploaded",
    "manual",
    name="crm_automation_trigger",
    create_type=False,
)
channel_enum = postgresql.ENUM(
    "task",
    "email",
    "sms",
    "notification",
    "stage",
    name="crm_automation_channel",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "stage_enter",
        "referral_created",
        "task_overdue",
        "score_band_change",
        "document_uploaded",
        "manual",
        name="crm_automation_trigger",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "task",
        "email",
        "sms",
        "notification",
        "stage",
        name="crm_automation_channel",
    ).create(bind, checkfirst=True)

    op.create_table(
        "crm_automation_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("trigger", trigger_enum, nullable=False),
        sa.Column("action", sa.String(length=500), nullable=False),
        sa.Column("channel", channel_enum, nullable=False),
        sa.Column("last_fired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fire_count", sa.Integer(), nullable=False, server_default="0"),
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
    )
    op.create_index(
        "ix_crm_automation_rules_organization_id",
        "crm_automation_rules",
        ["organization_id"],
    )
    op.create_index(
        "ix_crm_automation_rules_trigger",
        "crm_automation_rules",
        ["trigger"],
    )
    op.create_index(
        "ix_crm_automation_rules_enabled",
        "crm_automation_rules",
        ["enabled"],
    )


def downgrade() -> None:
    op.drop_index("ix_crm_automation_rules_enabled", table_name="crm_automation_rules")
    op.drop_index("ix_crm_automation_rules_trigger", table_name="crm_automation_rules")
    op.drop_index("ix_crm_automation_rules_organization_id", table_name="crm_automation_rules")
    op.drop_table("crm_automation_rules")
    postgresql.ENUM(name="crm_automation_channel").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="crm_automation_trigger").drop(op.get_bind(), checkfirst=True)
