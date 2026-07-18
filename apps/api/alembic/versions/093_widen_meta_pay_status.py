"""Widen document_metadata.payment_status for bureau status text.

Revision ID: 093_widen_meta_pay_status
Revises: 092_recipient_bench_wins
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "093_widen_meta_pay_status"
down_revision: str | None = "092_recipient_bench_wins"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "document_metadata",
        "payment_status",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "document_metadata",
        "payment_status",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
