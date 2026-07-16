"""Add org reinvestigation benchmark window defaults.

Revision ID: 090_org_benchmark_windows
Revises: 089_bureau_resp_ingest
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "090_org_benchmark_windows"
down_revision: str | None = "089_bureau_resp_ingest"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organization_dispute_settings",
        sa.Column(
            "reinvestigation_benchmark_baseline_days",
            sa.Integer(),
            nullable=False,
            server_default="90",
        ),
    )
    op.add_column(
        "organization_dispute_settings",
        sa.Column(
            "reinvestigation_benchmark_recent_days",
            sa.Integer(),
            nullable=False,
            server_default="30",
        ),
    )


def downgrade() -> None:
    op.drop_column("organization_dispute_settings", "reinvestigation_benchmark_recent_days")
    op.drop_column("organization_dispute_settings", "reinvestigation_benchmark_baseline_days")
