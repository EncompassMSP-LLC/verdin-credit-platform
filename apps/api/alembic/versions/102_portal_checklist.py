"""Portal borrower checklist completion state (LRP-104).

Revision ID: 102_portal_checklist
Revises: 101_referral_intake
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "102_portal_checklist"
down_revision: str | None = "101_referral_intake"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "portal_checklist_completions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portal_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_key", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["portal_user_id"], ["client_portal_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "case_id",
            "portal_user_id",
            "item_key",
            name="uq_portal_checklist_completion_key",
        ),
    )
    op.create_index(
        "ix_portal_checklist_completions_organization_id",
        "portal_checklist_completions",
        ["organization_id"],
    )
    op.create_index(
        "ix_portal_checklist_completions_case_id",
        "portal_checklist_completions",
        ["case_id"],
    )
    op.create_index(
        "ix_portal_checklist_completions_portal_user_id",
        "portal_checklist_completions",
        ["portal_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_portal_checklist_completions_portal_user_id",
        table_name="portal_checklist_completions",
    )
    op.drop_index(
        "ix_portal_checklist_completions_case_id",
        table_name="portal_checklist_completions",
    )
    op.drop_index(
        "ix_portal_checklist_completions_organization_id",
        table_name="portal_checklist_completions",
    )
    op.drop_table("portal_checklist_completions")
