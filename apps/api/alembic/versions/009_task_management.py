"""Expand tasks for operational task management.

Revision ID: 009_task_management
Revises: 008_timeline_audit_engine
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "009_task_management"
down_revision: str | None = "008_timeline_audit_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'open'")
        op.execute("ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'blocked'")
        op.execute("ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'canceled'")
        op.execute("ALTER TYPE task_priority ADD VALUE IF NOT EXISTS 'critical'")

    op.execute("UPDATE tasks SET status = 'open' WHERE status::text = 'pending'")
    op.execute("UPDATE tasks SET status = 'canceled' WHERE status::text = 'cancelled'")
    op.execute("UPDATE tasks SET priority = 'critical' WHERE priority::text = 'urgent'")

    op.add_column(
        "tasks",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE tasks t
        SET organization_id = c.organization_id
        FROM cases c
        WHERE t.case_id = c.id
        """
    )
    op.alter_column("tasks", "organization_id", nullable=False)

    op.alter_column("tasks", "case_id", nullable=True)

    op.add_column(
        "tasks",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("completed_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("source_module", sa.String(50), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("source_event_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.alter_column("tasks", "assigned_to_id", new_column_name="assigned_user_id")

    op.alter_column("tasks", "status", server_default="open")
    op.alter_column("tasks", "priority", server_default="medium")

    op.create_foreign_key(
        "fk_tasks_organization_id",
        "tasks",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_account_id",
        "tasks",
        "accounts",
        ["account_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_document_id",
        "tasks",
        "documents",
        ["document_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_completed_by_id",
        "tasks",
        "users",
        ["completed_by_id"],
        ["id"],
    )

    op.create_index("ix_tasks_organization_id", "tasks", ["organization_id"])
    op.create_index("ix_tasks_case_id", "tasks", ["case_id"])
    op.create_index("ix_tasks_account_id", "tasks", ["account_id"])
    op.create_index("ix_tasks_document_id", "tasks", ["document_id"])
    op.create_index("ix_tasks_assigned_user_id", "tasks", ["assigned_user_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])


def downgrade() -> None:
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_assigned_user_id", table_name="tasks")
    op.drop_index("ix_tasks_document_id", table_name="tasks")
    op.drop_index("ix_tasks_account_id", table_name="tasks")
    op.drop_index("ix_tasks_case_id", table_name="tasks")
    op.drop_index("ix_tasks_organization_id", table_name="tasks")

    op.drop_constraint("fk_tasks_completed_by_id", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_document_id", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_account_id", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_organization_id", "tasks", type_="foreignkey")

    op.alter_column("tasks", "assigned_user_id", new_column_name="assigned_to_id")

    op.drop_column("tasks", "source_event_id")
    op.drop_column("tasks", "source_module")
    op.drop_column("tasks", "completed_by_id")
    op.drop_column("tasks", "completed_at")
    op.drop_column("tasks", "document_id")
    op.drop_column("tasks", "account_id")
    op.drop_column("tasks", "organization_id")

    op.alter_column("tasks", "case_id", nullable=False)
    op.alter_column("tasks", "status", server_default="pending")

    op.execute("UPDATE tasks SET status = 'pending' WHERE status::text = 'open'")
    op.execute("UPDATE tasks SET status = 'cancelled' WHERE status::text = 'canceled'")
    op.execute("UPDATE tasks SET priority = 'urgent' WHERE priority::text = 'critical'")
