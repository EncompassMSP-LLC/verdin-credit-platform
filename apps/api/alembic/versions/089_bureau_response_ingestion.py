"""Add bureau_response_ingestion_runs audit table (Phase 15).

Revision ID: 089_bureau_resp_ingest
Revises: 088_org_dispute_settings
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "089_bureau_resp_ingest"
down_revision: str | None = "088_org_dispute_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE bureau_response_ingestion_run_status AS ENUM ('deferred', 'failed')")
    op.create_table(
        "bureau_response_ingestion_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "deferred",
                "failed",
                name="bureau_response_ingestion_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("deferral_reason", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bureau_response_ingestion_runs_organization_id"),
        "bureau_response_ingestion_runs",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_bureau_response_ingestion_runs_case_id"),
        "bureau_response_ingestion_runs",
        ["case_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_bureau_response_ingestion_runs_account_id"),
        "bureau_response_ingestion_runs",
        ["account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_bureau_response_ingestion_runs_account_id"),
        table_name="bureau_response_ingestion_runs",
    )
    op.drop_index(
        op.f("ix_bureau_response_ingestion_runs_case_id"),
        table_name="bureau_response_ingestion_runs",
    )
    op.drop_index(
        op.f("ix_bureau_response_ingestion_runs_organization_id"),
        table_name="bureau_response_ingestion_runs",
    )
    op.drop_table("bureau_response_ingestion_runs")
    op.execute("DROP TYPE bureau_response_ingestion_run_status")
