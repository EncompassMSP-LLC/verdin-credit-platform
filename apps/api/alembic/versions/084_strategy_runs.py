"""Add dispute_strategy_runs audit table.

Revision ID: 084_strategy_runs
Revises: 083_tradeline_page_maps
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "084_strategy_runs"
down_revision: str | None = "083_tradeline_page_maps"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dispute_strategy_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("generated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accounts_planned", sa.Integer(), nullable=False),
        sa.Column("issues_covered", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["generated_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dispute_strategy_runs_organization_id",
        "dispute_strategy_runs",
        ["organization_id"],
    )
    op.create_index("ix_dispute_strategy_runs_case_id", "dispute_strategy_runs", ["case_id"])
    op.create_index(
        "ix_dispute_strategy_runs_generated_by_id",
        "dispute_strategy_runs",
        ["generated_by_id"],
    )
    op.create_index(
        "ix_dispute_strategy_runs_case_generated_at",
        "dispute_strategy_runs",
        ["case_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dispute_strategy_runs_case_generated_at",
        table_name="dispute_strategy_runs",
    )
    op.drop_index(
        "ix_dispute_strategy_runs_generated_by_id",
        table_name="dispute_strategy_runs",
    )
    op.drop_index("ix_dispute_strategy_runs_case_id", table_name="dispute_strategy_runs")
    op.drop_index(
        "ix_dispute_strategy_runs_organization_id",
        table_name="dispute_strategy_runs",
    )
    op.drop_table("dispute_strategy_runs")
