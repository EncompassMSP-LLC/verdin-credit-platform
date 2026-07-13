"""Add optional note to checklist staff overrides.

Revision ID: 082_override_notes
Revises: 081_checklist_overrides
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "082_override_notes"
down_revision: str | None = "081_checklist_overrides"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "dispute_strategy_checklist_overrides",
        sa.Column("note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dispute_strategy_checklist_overrides", "note")
