"""Operator-gated bureau unsupervised re-filing audit table.

Revision ID: 059_bureau_unsupervised_refiling
Revises: 058_saml_passwordless_enrollment
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "059_bureau_unsupervised_refiling"
down_revision: str | None = "058_saml_passwordless_enrollment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE bureau_unsupervised_refiling_run_status AS ENUM "
        "('pending_approval', 'unsupervised_refiled', 'rejected', 'failed')"
    )
    op.create_table(
        "bureau_unsupervised_refiling_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_refiling_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bureau_target", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "unsupervised_refiled",
                "rejected",
                "failed",
                name="bureau_unsupervised_refiling_run_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("refiling_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsupervised_refiled_at", sa.DateTime(timezone=True), nullable=True),
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
            ["bureau_refiling_run_id"],
            ["bureau_refiling_runs.id"],
        ),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["timeline_event_id"],
            ["timeline_events.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_bureau_unsupervised_refiling_runs_org_requested",
        "bureau_unsupervised_refiling_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_bureau_unsupervised_refiling_runs_refiling_run",
        "bureau_unsupervised_refiling_runs",
        ["bureau_refiling_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_bureau_unsupervised_refiling_runs_refiling_run",
        table_name="bureau_unsupervised_refiling_runs",
    )
    op.drop_index(
        "ix_bureau_unsupervised_refiling_runs_org_requested",
        table_name="bureau_unsupervised_refiling_runs",
    )
    op.drop_table("bureau_unsupervised_refiling_runs")
    op.execute("DROP TYPE bureau_unsupervised_refiling_run_status")
