"""Alembic migration: CRM automation audit events (LRP-502).

Revision ID: 114_crm_automation_audit
Revises: 113_letter_draft_bldr
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "114_crm_automation_audit"
down_revision: str | None = "113_letter_draft_bldr"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE crm_automation_audit_event_kind AS ENUM ("
        "'rule_created', 'rule_updated', 'rule_enabled', 'rule_disabled', "
        "'rule_fired', 'rule_dry_run', 'rule_skipped')"
    )
    op.execute(
        "CREATE TYPE crm_automation_audit_status AS ENUM ("
        "'completed', 'skipped', 'failed', 'dry_run')"
    )
    op.create_table(
        "crm_automation_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "event_kind",
            postgresql.ENUM(
                "rule_created",
                "rule_updated",
                "rule_enabled",
                "rule_disabled",
                "rule_fired",
                "rule_dry_run",
                "rule_skipped",
                name="crm_automation_audit_event_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("trigger", sa.String(length=64), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "skipped",
                "failed",
                "dry_run",
                name="crm_automation_audit_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "schema_version",
            sa.String(length=32),
            nullable=False,
            server_default="crm-automation-audit-v1",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["rule_id"], ["crm_automation_rules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_crm_automation_audit_events_organization_id",
        "crm_automation_audit_events",
        ["organization_id"],
    )
    op.create_index(
        "ix_crm_automation_audit_events_rule_id",
        "crm_automation_audit_events",
        ["rule_id"],
    )
    op.create_index(
        "ix_crm_automation_audit_events_event_kind",
        "crm_automation_audit_events",
        ["event_kind"],
    )
    op.create_index(
        "ix_crm_automation_audit_events_status",
        "crm_automation_audit_events",
        ["status"],
    )
    op.create_index(
        "ix_crm_automation_audit_events_entity_id",
        "crm_automation_audit_events",
        ["entity_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_automation_audit_events_entity_id",
        table_name="crm_automation_audit_events",
    )
    op.drop_index(
        "ix_crm_automation_audit_events_status",
        table_name="crm_automation_audit_events",
    )
    op.drop_index(
        "ix_crm_automation_audit_events_event_kind",
        table_name="crm_automation_audit_events",
    )
    op.drop_index(
        "ix_crm_automation_audit_events_rule_id",
        table_name="crm_automation_audit_events",
    )
    op.drop_index(
        "ix_crm_automation_audit_events_organization_id",
        table_name="crm_automation_audit_events",
    )
    op.drop_table("crm_automation_audit_events")
    op.execute("DROP TYPE crm_automation_audit_status")
    op.execute("DROP TYPE crm_automation_audit_event_kind")
