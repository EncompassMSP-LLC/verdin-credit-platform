"""Alembic migration: notification matrix dispatches (LRP-202).

Revision ID: 105_notification_matrix
Revises: 104_referral_intake_orchestrator
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "105_notification_matrix"
down_revision: str | None = "104_referral_intake_orchestrator"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_matrix_dispatches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("event_key", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column(
            "triggered_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
            "organization_id",
            "event_key",
            "entity_type",
            "entity_id",
            name="uq_notification_matrix_dispatches_idempotency",
        ),
    )
    op.create_index(
        "ix_notification_matrix_dispatches_organization_id",
        "notification_matrix_dispatches",
        ["organization_id"],
    )
    op.create_index(
        "ix_notification_matrix_dispatches_event_key",
        "notification_matrix_dispatches",
        ["event_key"],
    )
    op.create_index(
        "ix_notification_matrix_dispatches_entity_id",
        "notification_matrix_dispatches",
        ["entity_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_matrix_dispatches_entity_id",
        table_name="notification_matrix_dispatches",
    )
    op.drop_index(
        "ix_notification_matrix_dispatches_event_key",
        table_name="notification_matrix_dispatches",
    )
    op.drop_index(
        "ix_notification_matrix_dispatches_organization_id",
        table_name="notification_matrix_dispatches",
    )
    op.drop_table("notification_matrix_dispatches")
