"""Add partner_access_action.referral_update for referral status PATCH.

Revision ID: 096_referral_update_action
Revises: 095_credit_analysis_runs
Create Date: 2026-07-23
"""

from collections.abc import Sequence

from alembic import op

revision: str = "096_referral_update_action"
down_revision: str | None = "095_credit_analysis_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'referral_update'")


def downgrade() -> None:
    # PostgreSQL cannot remove enum values safely; leave value in place.
    pass
