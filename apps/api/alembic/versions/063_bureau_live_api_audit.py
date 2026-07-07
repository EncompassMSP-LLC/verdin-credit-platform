"""Bureau live API invocation audit enrichment.

Revision ID: 063_bureau_live_api_audit
Revises: 062_bulk_idp_provisioning
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "063_bureau_live_api_audit"
down_revision: str | None = "062_bulk_idp_provisioning"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "bureau_live_api_runs",
        sa.Column("invocation_reference_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "bureau_live_api_runs",
        sa.Column("invocation_channel", sa.String(length=32), nullable=True),
    )
    op.execute(
        "UPDATE bureau_live_api_runs SET invocation_channel = 'operator_approved' "
        "WHERE status = 'invoked' AND invocation_channel IS NULL"
    )
    op.create_index(
        "ix_bureau_live_api_runs_invocation_reference_id",
        "bureau_live_api_runs",
        ["invocation_reference_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_bureau_live_api_runs_invocation_reference_id",
        table_name="bureau_live_api_runs",
    )
    op.drop_column("bureau_live_api_runs", "invocation_channel")
    op.drop_column("bureau_live_api_runs", "invocation_reference_id")
