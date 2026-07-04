"""Predictive outcome snapshot and refresh audit tables.

Revision ID: 029_predictive_outcome_snapshots
Revises: 028_scim_provision_logs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "029_predictive_outcome_snapshots"
down_revision: str | None = "028_scim_provision_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE predictive_outcome_refresh_status AS ENUM ('completed', 'failed')")
    op.execute("CREATE TYPE predictive_outcome_trigger_source AS ENUM ('manual', 'scheduled')")

    op.create_table(
        "predictive_outcome_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", name="uq_predictive_outcome_snapshots_org"),
    )
    op.create_index(
        "ix_predictive_outcome_snapshots_org",
        "predictive_outcome_snapshots",
        ["organization_id"],
    )

    op.create_table(
        "predictive_outcome_refresh_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="predictive_outcome_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "failed",
                name="predictive_outcome_refresh_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_predictive_outcome_refresh_runs_org",
        "predictive_outcome_refresh_runs",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_predictive_outcome_refresh_runs_org",
        table_name="predictive_outcome_refresh_runs",
    )
    op.drop_table("predictive_outcome_refresh_runs")
    op.drop_index(
        "ix_predictive_outcome_snapshots_org",
        table_name="predictive_outcome_snapshots",
    )
    op.drop_table("predictive_outcome_snapshots")
    op.execute("DROP TYPE predictive_outcome_refresh_status")
    op.execute("DROP TYPE predictive_outcome_trigger_source")
