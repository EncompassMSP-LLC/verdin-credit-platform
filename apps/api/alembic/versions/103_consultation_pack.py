"""Alembic migration: consultation_pack_runs (LRP-204).

Revision ID: 103_consultation_pack
Revises: 102_portal_checklist
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "103_consultation_pack"
down_revision: str | None = "102_portal_checklist"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consultation_pack_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id"),
            nullable=False,
        ),
        sa.Column(
            "generated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column(
            "credit_analysis_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("credit_analysis_runs.id"),
            nullable=True,
        ),
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
    )
    op.create_index(
        "ix_consultation_pack_runs_organization_id",
        "consultation_pack_runs",
        ["organization_id"],
    )
    op.create_index("ix_consultation_pack_runs_case_id", "consultation_pack_runs", ["case_id"])
    op.create_index("ix_consultation_pack_runs_status", "consultation_pack_runs", ["status"])
    op.create_index(
        "ix_consultation_pack_runs_generated_by_id",
        "consultation_pack_runs",
        ["generated_by_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_consultation_pack_runs_generated_by_id", table_name="consultation_pack_runs")
    op.drop_index("ix_consultation_pack_runs_status", table_name="consultation_pack_runs")
    op.drop_index("ix_consultation_pack_runs_case_id", table_name="consultation_pack_runs")
    op.drop_index("ix_consultation_pack_runs_organization_id", table_name="consultation_pack_runs")
    op.drop_table("consultation_pack_runs")
