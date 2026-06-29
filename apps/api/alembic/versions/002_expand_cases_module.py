"""Expand cases module for Sprint 2 case management.

Revision ID: 002_expand_cases
Revises: 001_initial
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "002_expand_cases"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE case_stage AS ENUM ("
        "'intake', 'review', 'evidence_gathering', 'dispute_preparation', "
        "'awaiting_response', 'monitoring', 'complete'"
        ")"
    )
    op.execute("CREATE TYPE case_priority AS ENUM ('low', 'medium', 'high', 'critical')")

    op.execute("ALTER TYPE case_status RENAME TO case_status_old")
    op.execute(
        "CREATE TYPE case_status AS ENUM (" "'open', 'active', 'on_hold', 'resolved', 'closed'" ")"
    )
    op.execute("ALTER TABLE cases ALTER COLUMN status DROP DEFAULT")
    op.execute(
        """
        ALTER TABLE cases
        ALTER COLUMN status TYPE case_status
        USING (
            CASE status::text
                WHEN 'open' THEN 'open'::case_status
                WHEN 'in_review' THEN 'active'::case_status
                WHEN 'closed' THEN 'closed'::case_status
                WHEN 'archived' THEN 'closed'::case_status
                ELSE 'open'::case_status
            END
        )
        """
    )
    op.execute("DROP TYPE case_status_old")
    op.execute("ALTER TABLE cases ALTER COLUMN status SET DEFAULT 'open'")

    op.add_column("cases", sa.Column("summary", sa.Text(), nullable=True))
    op.execute("UPDATE cases SET summary = description")
    op.drop_column("cases", "description")

    op.add_column(
        "cases",
        sa.Column("client_name", sa.String(255), nullable=False, server_default=""),
    )
    op.alter_column("cases", "client_name", server_default=None)

    op.add_column("cases", sa.Column("client_email", sa.String(255), nullable=True))
    op.add_column(
        "cases",
        sa.Column(
            "stage",
            postgresql.ENUM(
                "intake",
                "review",
                "evidence_gathering",
                "dispute_preparation",
                "awaiting_response",
                "monitoring",
                "complete",
                name="case_stage",
                create_type=False,
            ),
            nullable=False,
            server_default="intake",
        ),
    )
    op.alter_column("cases", "stage", server_default=None)

    op.add_column(
        "cases",
        sa.Column(
            "priority",
            postgresql.ENUM(
                "low",
                "medium",
                "high",
                "critical",
                name="case_priority",
                create_type=False,
            ),
            nullable=False,
            server_default="medium",
        ),
    )
    op.alter_column("cases", "priority", server_default=None)

    op.add_column("cases", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column(
        "cases",
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column("cases", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))

    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_stage", "cases", ["stage"])
    op.create_index("ix_cases_priority", "cases", ["priority"])
    op.create_index("ix_cases_assigned_to_id", "cases", ["assigned_to_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_assigned_to_id", table_name="cases")
    op.drop_index("ix_cases_priority", table_name="cases")
    op.drop_index("ix_cases_stage", table_name="cases")
    op.drop_index("ix_cases_status", table_name="cases")

    op.drop_column("cases", "closed_at")
    op.drop_column("cases", "opened_at")
    op.drop_column("cases", "notes")
    op.drop_column("cases", "priority")
    op.drop_column("cases", "stage")
    op.drop_column("cases", "client_email")
    op.drop_column("cases", "client_name")

    op.add_column("cases", sa.Column("description", sa.Text(), nullable=True))
    op.execute("UPDATE cases SET description = summary")
    op.drop_column("cases", "summary")

    op.execute("ALTER TYPE case_status RENAME TO case_status_new")
    op.execute("CREATE TYPE case_status AS ENUM ('open', 'in_review', 'closed', 'archived')")
    op.execute("ALTER TABLE cases ALTER COLUMN status DROP DEFAULT")
    op.execute(
        """
        ALTER TABLE cases
        ALTER COLUMN status TYPE case_status
        USING (
            CASE status::text
                WHEN 'open' THEN 'open'::case_status
                WHEN 'active' THEN 'in_review'::case_status
                WHEN 'on_hold' THEN 'in_review'::case_status
                WHEN 'resolved' THEN 'closed'::case_status
                WHEN 'closed' THEN 'closed'::case_status
                ELSE 'open'::case_status
            END
        )
        """
    )
    op.execute("DROP TYPE case_status_new")
    op.execute("ALTER TABLE cases ALTER COLUMN status SET DEFAULT 'open'")

    op.execute("DROP TYPE case_priority")
    op.execute("DROP TYPE case_stage")
