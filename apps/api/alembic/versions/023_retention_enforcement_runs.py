"""Retention enforcement run audit log.

Revision ID: 023_retention_enforcement_runs
Revises: 022_organization_billing
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "023_retention_enforcement_runs"
down_revision: str | None = "022_organization_billing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE enforcement_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute("CREATE TYPE enforcement_run_status AS ENUM ('completed', 'failed', 'skipped')")

    op.create_table(
        "retention_enforcement_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "scope",
            postgresql.ENUM(
                "documents",
                "communications",
                "audit_logs",
                "client_profiles",
                name="retention_scope",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="enforcement_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "failed",
                "skipped",
                name="enforcement_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("items_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_enforced", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["policy_id"], ["retention_policies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_retention_enforcement_runs_organization_id",
        "retention_enforcement_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_retention_enforcement_runs_policy_id",
        "retention_enforcement_runs",
        ["policy_id"],
    )
    op.create_index(
        "ix_retention_enforcement_runs_started_at",
        "retention_enforcement_runs",
        ["started_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_retention_enforcement_runs_started_at", table_name="retention_enforcement_runs"
    )
    op.drop_index(
        "ix_retention_enforcement_runs_policy_id", table_name="retention_enforcement_runs"
    )
    op.drop_index(
        "ix_retention_enforcement_runs_organization_id",
        table_name="retention_enforcement_runs",
    )
    op.drop_table("retention_enforcement_runs")
    op.execute("DROP TYPE enforcement_run_status")
    op.execute("DROP TYPE enforcement_trigger_source")
