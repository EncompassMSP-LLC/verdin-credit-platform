"""Extend timeline_events for platform-wide audit stream.

Revision ID: 008_timeline_audit_engine
Revises: 007_document_metadata_resolution
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "008_timeline_audit_engine"
down_revision: str | None = "007_document_metadata_resolution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "timeline_events",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("event_category", sa.String(50), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("source_module", sa.String(50), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "timeline_events",
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
    )

    op.execute(
        """
        UPDATE timeline_events te
        SET organization_id = c.organization_id
        FROM cases c
        WHERE te.case_id = c.id
        """
    )

    op.alter_column("timeline_events", "organization_id", nullable=False)
    op.alter_column("timeline_events", "case_id", nullable=True)

    op.create_foreign_key(
        "fk_timeline_events_organization_id",
        "timeline_events",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_timeline_events_account_id",
        "timeline_events",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_timeline_events_document_id",
        "timeline_events",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_timeline_events_performed_by",
        "timeline_events",
        "users",
        ["performed_by"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        UPDATE timeline_events
        SET event_category = 'legacy',
            source_module = 'timeline'
        WHERE event_category IS NULL
        """
    )
    op.alter_column("timeline_events", "event_category", nullable=False, server_default="legacy")
    op.alter_column("timeline_events", "source_module", nullable=False, server_default="timeline")
    op.create_index("ix_timeline_events_case_id", "timeline_events", ["case_id"])
    op.create_index("ix_timeline_events_account_id", "timeline_events", ["account_id"])
    op.create_index("ix_timeline_events_document_id", "timeline_events", ["document_id"])
    op.create_index("ix_timeline_events_performed_by", "timeline_events", ["performed_by"])
    op.create_index("ix_timeline_events_occurred_at", "timeline_events", ["occurred_at"])
    op.create_index("ix_timeline_events_event_category", "timeline_events", ["event_category"])


def downgrade() -> None:
    op.drop_index("ix_timeline_events_event_category", table_name="timeline_events")
    op.drop_index("ix_timeline_events_occurred_at", table_name="timeline_events")
    op.drop_index("ix_timeline_events_performed_by", table_name="timeline_events")
    op.drop_index("ix_timeline_events_document_id", table_name="timeline_events")
    op.drop_index("ix_timeline_events_account_id", table_name="timeline_events")
    op.drop_index("ix_timeline_events_case_id", table_name="timeline_events")
    op.drop_index("ix_timeline_events_organization_id", table_name="timeline_events")

    op.drop_constraint("fk_timeline_events_performed_by", "timeline_events", type_="foreignkey")
    op.drop_constraint("fk_timeline_events_document_id", "timeline_events", type_="foreignkey")
    op.drop_constraint("fk_timeline_events_account_id", "timeline_events", type_="foreignkey")
    op.drop_constraint("fk_timeline_events_organization_id", "timeline_events", type_="foreignkey")

    op.alter_column("timeline_events", "case_id", nullable=False)
    op.drop_column("timeline_events", "metadata")
    op.drop_column("timeline_events", "performed_by")
    op.drop_column("timeline_events", "source_module")
    op.drop_column("timeline_events", "event_category")
    op.drop_column("timeline_events", "document_id")
    op.drop_column("timeline_events", "account_id")
    op.drop_column("timeline_events", "organization_id")
