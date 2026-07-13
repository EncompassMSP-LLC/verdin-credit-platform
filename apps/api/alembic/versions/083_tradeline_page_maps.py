"""Add tradeline page map cache on parsed credit reports.

Revision ID: 083_tradeline_page_maps
Revises: 082_override_notes
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "083_tradeline_page_maps"
down_revision: str | None = "082_override_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "document_parsed_credit_reports",
        sa.Column("tradeline_page_map", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("document_parsed_credit_reports", "tradeline_page_map")
