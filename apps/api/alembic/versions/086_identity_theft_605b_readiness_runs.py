"""Add identity_theft_605b_readiness_runs audit table.

Revision ID: 086_it_readiness_runs
Revises: 085_identity_theft
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "086_it_readiness_runs"
down_revision: str | None = "085_identity_theft"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "identity_theft_605b_readiness_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("generated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_ready", sa.Boolean(), nullable=False),
        sa.Column("packet_readiness", sa.Integer(), nullable=True),
        sa.Column("confirmed_count", sa.Integer(), nullable=False),
        sa.Column("attestation_recorded", sa.Boolean(), nullable=False),
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
        "ix_it_605b_readiness_runs_organization_id",
        "identity_theft_605b_readiness_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_it_605b_readiness_runs_case_id",
        "identity_theft_605b_readiness_runs",
        ["case_id"],
    )
    op.create_index(
        "ix_it_605b_readiness_runs_generated_by_id",
        "identity_theft_605b_readiness_runs",
        ["generated_by_id"],
    )
    op.create_index(
        "ix_it_605b_readiness_runs_case_generated_at",
        "identity_theft_605b_readiness_runs",
        ["case_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_it_605b_readiness_runs_case_generated_at",
        table_name="identity_theft_605b_readiness_runs",
    )
    op.drop_index(
        "ix_it_605b_readiness_runs_generated_by_id",
        table_name="identity_theft_605b_readiness_runs",
    )
    op.drop_index(
        "ix_it_605b_readiness_runs_case_id",
        table_name="identity_theft_605b_readiness_runs",
    )
    op.drop_index(
        "ix_it_605b_readiness_runs_organization_id",
        table_name="identity_theft_605b_readiness_runs",
    )
    op.drop_table("identity_theft_605b_readiness_runs")
