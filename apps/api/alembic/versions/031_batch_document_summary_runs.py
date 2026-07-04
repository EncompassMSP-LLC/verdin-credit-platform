"""Batch document LLM summary run audit table.

Revision ID: 031_batch_document_summary_runs
Revises: 030_api_key_rotation_logs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "031_batch_document_summary_runs"
down_revision: str | None = "030_api_key_rotation_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE batch_summary_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute(
        "CREATE TYPE batch_summary_run_status AS ENUM ('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "batch_document_summary_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="batch_summary_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "running",
                "completed",
                "failed",
                name="batch_summary_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("document_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("documents_queued", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_succeeded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("documents_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_batch_document_summary_runs_org",
        "batch_document_summary_runs",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_batch_document_summary_runs_org",
        table_name="batch_document_summary_runs",
    )
    op.drop_table("batch_document_summary_runs")
    op.execute("DROP TYPE batch_summary_run_status")
    op.execute("DROP TYPE batch_summary_trigger_source")
