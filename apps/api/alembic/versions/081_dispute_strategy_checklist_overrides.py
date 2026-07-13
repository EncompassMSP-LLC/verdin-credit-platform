"""Staff overrides for dispute-strategy checklist completion.

Revision ID: 081_dispute_strategy_checklist_overrides
Revises: 080_native_mobile_app_store
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "081_dispute_strategy_checklist_overrides"
down_revision: str | None = "080_native_mobile_app_store"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dispute_strategy_checklist_overrides",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("checklist_kind", sa.String(length=20), nullable=False),
        sa.Column("account_key", sa.String(length=255), nullable=False),
        sa.Column("item_id", sa.String(length=100), nullable=False),
        sa.Column("completion_status", sa.String(length=20), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "case_id",
            "checklist_kind",
            "account_key",
            "item_id",
            name="uq_dispute_strategy_checklist_override_key",
        ),
    )
    op.create_index(
        "ix_dispute_strategy_checklist_overrides_organization_id",
        "dispute_strategy_checklist_overrides",
        ["organization_id"],
    )
    op.create_index(
        "ix_dispute_strategy_checklist_overrides_case_id",
        "dispute_strategy_checklist_overrides",
        ["case_id"],
    )
    op.create_index(
        "ix_dispute_strategy_checklist_overrides_checklist_kind",
        "dispute_strategy_checklist_overrides",
        ["checklist_kind"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dispute_strategy_checklist_overrides_checklist_kind",
        table_name="dispute_strategy_checklist_overrides",
    )
    op.drop_index(
        "ix_dispute_strategy_checklist_overrides_case_id",
        table_name="dispute_strategy_checklist_overrides",
    )
    op.drop_index(
        "ix_dispute_strategy_checklist_overrides_organization_id",
        table_name="dispute_strategy_checklist_overrides",
    )
    op.drop_table("dispute_strategy_checklist_overrides")
