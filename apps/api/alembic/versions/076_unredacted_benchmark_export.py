"""Admin-gated unredacted cross-org benchmark export audit table.

Revision ID: 076_unredacted_benchmark_export
Revises: 075_client_enrollments
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "076_unredacted_benchmark_export"
down_revision: str | None = "075_client_enrollments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE unredacted_cross_org_benchmark_export_run_status AS ENUM "
        "('pending_approval', 'approved', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "unredacted_cross_org_benchmark_export_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cross_org_benchmark_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "approved",
                "rejected",
                "failed",
                name="unredacted_cross_org_benchmark_export_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("export_summary", sa.Text(), nullable=False),
        sa.Column("export_reference_id", sa.String(length=255), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
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
            ["cross_org_benchmark_run_id"],
            ["cross_org_benchmark_runs.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_unredacted_cross_org_benchmark_export_runs_org_requested",
        "unredacted_cross_org_benchmark_export_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_unredacted_cross_org_benchmark_export_runs_benchmark_run",
        "unredacted_cross_org_benchmark_export_runs",
        ["cross_org_benchmark_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_unredacted_cross_org_benchmark_export_runs_benchmark_run",
        table_name="unredacted_cross_org_benchmark_export_runs",
    )
    op.drop_index(
        "ix_unredacted_cross_org_benchmark_export_runs_org_requested",
        table_name="unredacted_cross_org_benchmark_export_runs",
    )
    op.drop_table("unredacted_cross_org_benchmark_export_runs")
    op.execute("DROP TYPE unredacted_cross_org_benchmark_export_run_status")
