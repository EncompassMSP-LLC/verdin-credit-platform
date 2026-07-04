"""API key rotation audit log table.

Revision ID: 030_api_key_rotation_logs
Revises: 029_predictive_outcome_snapshots
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "030_api_key_rotation_logs"
down_revision: str | None = "029_predictive_outcome_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_key_rotation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_api_key_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("new_api_key_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rotated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["previous_api_key_id"], ["organization_api_keys.id"]),
        sa.ForeignKeyConstraint(["new_api_key_id"], ["organization_api_keys.id"]),
        sa.ForeignKeyConstraint(["rotated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_api_key_rotation_logs_org",
        "api_key_rotation_logs",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_api_key_rotation_logs_org", table_name="api_key_rotation_logs")
    op.drop_table("api_key_rotation_logs")
