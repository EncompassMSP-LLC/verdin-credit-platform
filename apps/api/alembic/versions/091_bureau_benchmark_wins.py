"""Add per-bureau reinvestigation benchmark window overrides.

Revision ID: 091_bureau_benchmark_wins
Revises: 090_org_benchmark_windows
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "091_bureau_benchmark_wins"
down_revision: str | None = "090_org_benchmark_windows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organization_dispute_settings",
        sa.Column(
            "reinvestigation_benchmark_bureau_windows",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "organization_dispute_settings",
        "reinvestigation_benchmark_bureau_windows",
    )
