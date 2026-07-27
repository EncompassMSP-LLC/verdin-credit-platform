"""Alembic migration: referral intake orchestrator runs (LRP-201).

Revision ID: 104_referral_intake_orchestrator
Revises: 103_consultation_pack
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "104_referral_intake_orchestrator"
down_revision: str | None = "103_consultation_pack"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "partner_referral_intake_orchestrator_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "intake_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_referral_intake_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id"),
            nullable=True,
        ),
        sa.Column(
            "referral_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_referrals.id"),
            nullable=True,
        ),
        sa.Column(
            "assigned_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
    )
    op.create_index(
        "ix_partner_referral_intake_orchestrator_runs_organization_id",
        "partner_referral_intake_orchestrator_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_referral_intake_orchestrator_runs_intake_run_id",
        "partner_referral_intake_orchestrator_runs",
        ["intake_run_id"],
        unique=True,
    )
    op.create_index(
        "ix_partner_referral_intake_orchestrator_runs_status",
        "partner_referral_intake_orchestrator_runs",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_partner_referral_intake_orchestrator_runs_status",
        table_name="partner_referral_intake_orchestrator_runs",
    )
    op.drop_index(
        "ix_partner_referral_intake_orchestrator_runs_intake_run_id",
        table_name="partner_referral_intake_orchestrator_runs",
    )
    op.drop_index(
        "ix_partner_referral_intake_orchestrator_runs_organization_id",
        table_name="partner_referral_intake_orchestrator_runs",
    )
    op.drop_table("partner_referral_intake_orchestrator_runs")
