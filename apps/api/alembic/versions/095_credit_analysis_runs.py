"""Credit analysis / Lending Readiness Score runs.

Revision ID: 095_credit_analysis_runs
Revises: 094_mortgage_partner
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "095_credit_analysis_runs"
down_revision: str | None = "094_mortgage_partner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credit_analysis_runs",
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
        sa.Column("status", sa.String(length=32), nullable=False, server_default="published"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "published_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("score_version", sa.String(length=32), nullable=False),
        sa.Column("formula_version", sa.String(length=32), nullable=False),
        sa.Column("inputs_hash", sa.String(length=64), nullable=False),
        sa.Column("reports_evaluated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tradelines_evaluated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("borrower_readiness_score", sa.Integer(), nullable=False),
        sa.Column("mortgage_readiness_score", sa.Integer(), nullable=False),
        sa.Column("band", sa.String(length=32), nullable=False),
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
        "ix_credit_analysis_runs_organization_id",
        "credit_analysis_runs",
        ["organization_id"],
    )
    op.create_index("ix_credit_analysis_runs_case_id", "credit_analysis_runs", ["case_id"])
    op.create_index(
        "ix_credit_analysis_runs_generated_by_id",
        "credit_analysis_runs",
        ["generated_by_id"],
    )
    op.create_index("ix_credit_analysis_runs_status", "credit_analysis_runs", ["status"])
    op.create_index("ix_credit_analysis_runs_band", "credit_analysis_runs", ["band"])
    op.create_index(
        "ix_credit_analysis_runs_case_generated",
        "credit_analysis_runs",
        ["case_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_credit_analysis_runs_case_generated", table_name="credit_analysis_runs")
    op.drop_index("ix_credit_analysis_runs_band", table_name="credit_analysis_runs")
    op.drop_index("ix_credit_analysis_runs_status", table_name="credit_analysis_runs")
    op.drop_index("ix_credit_analysis_runs_generated_by_id", table_name="credit_analysis_runs")
    op.drop_index("ix_credit_analysis_runs_case_id", table_name="credit_analysis_runs")
    op.drop_index("ix_credit_analysis_runs_organization_id", table_name="credit_analysis_runs")
    op.drop_table("credit_analysis_runs")
