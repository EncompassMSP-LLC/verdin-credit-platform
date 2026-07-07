"""Admin-gated fully autonomous bureau API filing audit table.

Revision ID: 069_full_auto_bureau_api
Revises: 068_oauth_marketplace_publishing
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "069_full_auto_bureau_api"
down_revision: str | None = "068_oauth_marketplace_publishing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE fully_autonomous_bureau_api_filing_run_status AS ENUM "
        "('pending_approval', 'executed', 'rejected', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.create_table(
        "fully_autonomous_bureau_api_filing_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("autonomous_bureau_filing_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "executed",
                "rejected",
                "failed",
                name="fully_autonomous_bureau_api_filing_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("api_filing_summary", sa.Text(), nullable=False),
        sa.Column("execution_reference_id", sa.String(length=128), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["autonomous_bureau_filing_run_id"],
            ["autonomous_bureau_filing_runs.id"],
        ),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_fully_auto_bureau_api_filing_runs_org_requested",
        "fully_autonomous_bureau_api_filing_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_fully_auto_bureau_api_filing_runs_filing_run",
        "fully_autonomous_bureau_api_filing_runs",
        ["autonomous_bureau_filing_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fully_auto_bureau_api_filing_runs_filing_run",
        table_name="fully_autonomous_bureau_api_filing_runs",
    )
    op.drop_index(
        "ix_fully_auto_bureau_api_filing_runs_org_requested",
        table_name="fully_autonomous_bureau_api_filing_runs",
    )
    op.drop_table("fully_autonomous_bureau_api_filing_runs")
    op.execute("DROP TYPE fully_autonomous_bureau_api_filing_run_status")
