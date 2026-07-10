"""Admin-gated live unredacted benchmark blob export audit table.

Revision ID: 077_live_benchmark_blob_export
Revises: 076_unredacted_benchmark_export
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "077_live_benchmark_blob_export"
down_revision: str | None = "076_unredacted_benchmark_export"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE live_unredacted_benchmark_blob_export_run_status AS ENUM "
        "('pending_approval', 'exported', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "live_unredacted_benchmark_blob_export_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unredacted_export_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "exported",
                "rejected",
                "failed",
                name="live_unredacted_benchmark_blob_export_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("export_summary", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["unredacted_export_run_id"],
            ["unredacted_cross_org_benchmark_export_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_live_unredacted_benchmark_blob_export_runs_org_requested",
        "live_unredacted_benchmark_blob_export_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_live_unredacted_benchmark_blob_export_runs_parent",
        "live_unredacted_benchmark_blob_export_runs",
        ["unredacted_export_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_live_unredacted_benchmark_blob_export_runs_parent",
        table_name="live_unredacted_benchmark_blob_export_runs",
    )
    op.drop_index(
        "ix_live_unredacted_benchmark_blob_export_runs_org_requested",
        table_name="live_unredacted_benchmark_blob_export_runs",
    )
    op.drop_table("live_unredacted_benchmark_blob_export_runs")
    op.execute("DROP TYPE live_unredacted_benchmark_blob_export_run_status")
