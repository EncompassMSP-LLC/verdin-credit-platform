"""Optional client_id FK on cases.

Revision ID: 015_cases_client_id
Revises: 014_client_portal_users
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "015_cases_client_id"
down_revision: str | None = "014_client_portal_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cases_client_id", "cases", ["client_id"])
    op.create_foreign_key(
        "fk_cases_client_id_clients",
        "cases",
        "clients",
        ["client_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_cases_client_id_clients", "cases", type_="foreignkey")
    op.drop_index("ix_cases_client_id", table_name="cases")
    op.drop_column("cases", "client_id")
