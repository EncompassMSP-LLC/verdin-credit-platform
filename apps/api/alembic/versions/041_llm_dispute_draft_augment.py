"""LLM dispute draft augment audit table.

Revision ID: 041_llm_dispute_draft_augment
Revises: 040_hris_bidirectional_sync
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "041_llm_dispute_draft_augment"
down_revision: str | None = "040_hris_bidirectional_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE llm_dispute_draft_augment_status AS ENUM ('completed', 'failed')")

    op.create_table(
        "llm_dispute_draft_augments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_type", sa.String(length=50), nullable=False),
        sa.Column("base_template_id", sa.String(length=100), nullable=False),
        sa.Column("base_subject", sa.String(length=255), nullable=False),
        sa.Column("base_body", sa.Text(), nullable=False),
        sa.Column("augmented_body", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "failed",
                name="llm_dispute_draft_augment_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=50), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("prompt_hash", sa.String(length=64), nullable=True),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_llm_dispute_draft_augments_org_requested",
        "llm_dispute_draft_augments",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_llm_dispute_draft_augments_account_requested",
        "llm_dispute_draft_augments",
        ["account_id", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_llm_dispute_draft_augments_account_requested",
        table_name="llm_dispute_draft_augments",
    )
    op.drop_index(
        "ix_llm_dispute_draft_augments_org_requested",
        table_name="llm_dispute_draft_augments",
    )
    op.drop_table("llm_dispute_draft_augments")
    op.execute("DROP TYPE llm_dispute_draft_augment_status")
