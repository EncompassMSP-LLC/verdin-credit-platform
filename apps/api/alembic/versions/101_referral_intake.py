"""Partner referral web-form intake audit (LRP-103).

Revision ID: 101_referral_intake
Revises: 100_organization_type_flags
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "101_referral_intake"
down_revision: str | None = "100_organization_type_flags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

referral_intake_status = postgresql.ENUM(
    "accepted",
    "quarantined",
    "duplicate_review",
    name="referral_intake_status",
    create_type=False,
)


def upgrade() -> None:
    referral_intake_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "partner_referral_intake_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cro_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partnership_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("referral_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            referral_intake_status,
            nullable=False,
            server_default="accepted",
        ),
        sa.Column("partner_org_name", sa.String(length=255), nullable=False),
        sa.Column("lo_name", sa.String(length=255), nullable=False),
        sa.Column("lo_email", sa.String(length=255), nullable=False),
        sa.Column("lo_phone", sa.String(length=50), nullable=True),
        sa.Column("borrower_name", sa.String(length=255), nullable=False),
        sa.Column("borrower_email", sa.String(length=255), nullable=True),
        sa.Column("borrower_phone", sa.String(length=50), nullable=True),
        sa.Column("product_intent", sa.String(length=255), nullable=True),
        sa.Column("known_gaps", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "consent_attested", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "source_channel",
            sa.String(length=64),
            nullable=False,
            server_default="web_form",
        ),
        sa.Column("quarantine_reason", sa.String(length=255), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["cro_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["partnership_id"], ["org_partnerships.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["referral_id"], ["partner_referrals.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
    )
    op.create_index(
        "ix_partner_referral_intake_runs_cro_organization_id",
        "partner_referral_intake_runs",
        ["cro_organization_id"],
    )
    op.create_index(
        "ix_partner_referral_intake_runs_partnership_id",
        "partner_referral_intake_runs",
        ["partnership_id"],
    )
    op.create_index(
        "ix_partner_referral_intake_runs_status",
        "partner_referral_intake_runs",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_partner_referral_intake_runs_status",
        table_name="partner_referral_intake_runs",
    )
    op.drop_index(
        "ix_partner_referral_intake_runs_partnership_id",
        table_name="partner_referral_intake_runs",
    )
    op.drop_index(
        "ix_partner_referral_intake_runs_cro_organization_id",
        table_name="partner_referral_intake_runs",
    )
    op.drop_table("partner_referral_intake_runs")
    referral_intake_status.drop(op.get_bind(), checkfirst=True)
