"""Add organization_dispute_settings for cross-bureau tolerance (Phase 15).

Revision ID: 088_org_dispute_settings
Revises: 087_dispute_responses
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "088_org_dispute_settings"
down_revision: str | None = "087_dispute_responses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_dispute_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "cross_bureau_balance_tolerance",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="1.00",
        ),
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
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", name="uq_organization_dispute_settings_org"),
    )
    op.create_index(
        op.f("ix_organization_dispute_settings_organization_id"),
        "organization_dispute_settings",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_dispute_settings_organization_id"),
        table_name="organization_dispute_settings",
    )
    op.drop_table("organization_dispute_settings")
