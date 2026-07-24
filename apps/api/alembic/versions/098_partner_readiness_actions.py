"""Add readiness_view and readiness_export to partner_access_action enum.

Revision ID: 098_partner_readiness_actions
Revises: 097_partner_loan_pipeline
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op

revision: str = "098_partner_readiness_actions"
down_revision: str | None = "097_partner_loan_pipeline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Extend partner_access_action enum with readiness surfaces.
    # ADD VALUE IF NOT EXISTS is idempotent in PostgreSQL 9.6+.
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'readiness_view'")
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'readiness_export'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values. No-op on downgrade.
    pass
