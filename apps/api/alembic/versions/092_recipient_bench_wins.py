"""Add per-recipient reinvestigation benchmark window overrides.

Revision ID: 092_recipient_bench_wins
Revises: 091_bureau_benchmark_wins
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "092_recipient_bench_wins"
down_revision: str | None = "091_bureau_benchmark_wins"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organization_dispute_settings",
        sa.Column(
            "reinvestigation_benchmark_recipient_windows",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "organization_dispute_settings",
        "reinvestigation_benchmark_recipient_windows",
    )
