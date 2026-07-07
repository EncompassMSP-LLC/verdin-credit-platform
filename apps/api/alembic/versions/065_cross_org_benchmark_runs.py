"""add cross org benchmark runs table

Revision ID: 065_cross_org_benchmark_runs
Revises: 064_public_oauth_portal_apps
Create Date: 2026-07-07 06:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "065_cross_org_benchmark_runs"
down_revision: str | None = "064_public_oauth_portal_apps"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE cross_org_benchmark_trigger_source AS ENUM ('manual'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE cross_org_benchmark_run_status AS ENUM ('completed', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "cross_org_benchmark_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                name="cross_org_benchmark_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "failed",
                name="cross_org_benchmark_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("organizations_evaluated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
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
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cross_org_benchmark_runs_requested_by_id",
        "cross_org_benchmark_runs",
        ["requested_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cross_org_benchmark_runs_requested_by_id", table_name="cross_org_benchmark_runs"
    )
    op.drop_table("cross_org_benchmark_runs")
    op.execute("DROP TYPE IF EXISTS cross_org_benchmark_run_status")
    op.execute("DROP TYPE IF EXISTS cross_org_benchmark_trigger_source")
