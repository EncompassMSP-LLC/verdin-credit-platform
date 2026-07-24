"""Add loan pipeline stage + milestones to mortgage partner edition.

Revision ID: 097_partner_loan_pipeline
Revises: 096_referral_update_action
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "097_partner_loan_pipeline"
down_revision: str | None = "096_referral_update_action"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LOAN_PIPELINE_STAGE_ENUM = postgresql.ENUM(
    "referred",
    "intake",
    "in_repair",
    "near_ready",
    "mortgage_ready",
    "in_underwriting",
    "funded",
    "declined",
    "withdrawn",
    name="loan_pipeline_stage",
    create_type=False,
)


def upgrade() -> None:
    # 1. New loan_pipeline_stage enum type
    op.execute(
        "CREATE TYPE loan_pipeline_stage AS ENUM ("
        "'referred', 'intake', 'in_repair', 'near_ready', 'mortgage_ready', "
        "'in_underwriting', 'funded', 'declined', 'withdrawn')"
    )

    # 2. Extend partner_access_action with pipeline / milestone values
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'pipeline_view'")
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'pipeline_update'")
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'milestone_update'")

    # 3. Add pipeline columns to partner_referrals
    op.add_column(
        "partner_referrals",
        sa.Column(
            "pipeline_stage",
            LOAN_PIPELINE_STAGE_ENUM,
            nullable=False,
            server_default="referred",
        ),
    )
    op.add_column(
        "partner_referrals",
        sa.Column(
            "pipeline_stage_changed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # 4. Create partner_loan_milestones table
    op.create_table(
        "partner_loan_milestones",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "referral_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_referrals.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("complete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # TimestampMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # SoftDeleteMixin
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # AuditMixin
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "updated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )
    # Indexes for referral_id and organization_id are created automatically by
    # the index=True flags on the Column definitions in create_table above.


def downgrade() -> None:
    op.drop_table("partner_loan_milestones")
    op.drop_column("partner_referrals", "pipeline_stage_changed_at")
    op.drop_column("partner_referrals", "pipeline_stage")
    op.execute("DROP TYPE IF EXISTS loan_pipeline_stage")
    # NOTE: enum values added to partner_access_action cannot be removed in PG safely.
