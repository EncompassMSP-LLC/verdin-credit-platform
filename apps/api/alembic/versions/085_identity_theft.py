"""Add identity theft incident, account review, and protection tables.

Revision ID: 085_identity_theft
Revises: 084_strategy_runs
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "085_identity_theft"
down_revision: str | None = "084_strategy_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    identity_theft_incident_status = sa.Enum(
        "open",
        "in_recovery",
        "closed",
        name="identity_theft_incident_status",
    )
    identity_theft_issue_type = sa.Enum(
        "IDENTITY_THEFT_INDICATOR",
        "CONFIRMED_IDENTITY_THEFT_CLAIM",
        name="identity_theft_issue_type",
    )
    identity_theft_confirmation = sa.Enum(
        "recognize",
        "need_more_info",
        "inaccurate_reporting",
        "identity_theft",
        "mixed_file",
        "authorized_user",
        "unsure",
        name="identity_theft_confirmation",
    )
    identity_theft_protection_type = sa.Enum(
        "initial_fraud_alert",
        "extended_fraud_alert",
        "active_duty_alert",
        "equifax_freeze",
        "experian_freeze",
        "transunion_freeze",
        name="identity_theft_protection_type",
    )
    identity_theft_protection_status = sa.Enum(
        "active",
        "inactive",
        "frozen",
        "unfrozen",
        "unknown",
        name="identity_theft_protection_status",
    )

    identity_theft_incident_status.create(op.get_bind(), checkfirst=True)
    identity_theft_issue_type.create(op.get_bind(), checkfirst=True)
    identity_theft_confirmation.create(op.get_bind(), checkfirst=True)
    identity_theft_protection_type.create(op.get_bind(), checkfirst=True)
    identity_theft_protection_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "identity_theft_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", identity_theft_incident_status, nullable=False),
        sa.Column("discovered_at", sa.Date(), nullable=True),
        sa.Column("suspected_theft_period_start", sa.Date(), nullable=True),
        sa.Column("suspected_theft_period_end", sa.Date(), nullable=True),
        sa.Column(
            "unrecognized_addresses",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "unrecognized_aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "companies_contacted",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("police_report_number", sa.String(length=128), nullable=True),
        sa.Column("police_report_agency", sa.String(length=255), nullable=True),
        sa.Column("police_report_filed_at", sa.Date(), nullable=True),
        sa.Column("ftc_report_status", sa.String(length=64), nullable=False),
        sa.Column("ftc_report_reference", sa.String(length=255), nullable=True),
        sa.Column(
            "evidence_checklist",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("recovery_step", sa.Integer(), nullable=False),
        sa.Column("consumer_attestation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumer_attestation_text", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_identity_theft_incidents_organization_id",
        "identity_theft_incidents",
        ["organization_id"],
    )
    op.create_index(
        "ix_identity_theft_incidents_case_id",
        "identity_theft_incidents",
        ["case_id"],
    )

    op.create_table(
        "identity_theft_account_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bureau", sa.String(length=32), nullable=True),
        sa.Column("tradeline_index", sa.Integer(), nullable=True),
        sa.Column("match_key", sa.String(length=255), nullable=True),
        sa.Column("creditor_name", sa.String(length=255), nullable=True),
        sa.Column("account_number_masked", sa.String(length=64), nullable=True),
        sa.Column("detection_source", sa.String(length=64), nullable=False),
        sa.Column("rule_id", sa.String(length=128), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("issue_type", identity_theft_issue_type, nullable=False),
        sa.Column("consumer_confirmation", identity_theft_confirmation, nullable=True),
        sa.Column("consumer_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ordinary_dispute_locked", sa.Boolean(), nullable=False),
        sa.Column("legal_path", sa.String(length=64), nullable=True),
        sa.Column("packet_readiness", sa.Integer(), nullable=True),
        sa.Column(
            "missing_evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("attestation_accepted", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["identity_theft_incidents.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_identity_theft_account_reviews_organization_id",
        "identity_theft_account_reviews",
        ["organization_id"],
    )
    op.create_index(
        "ix_identity_theft_account_reviews_case_id",
        "identity_theft_account_reviews",
        ["case_id"],
    )
    op.create_index(
        "ix_identity_theft_account_reviews_incident_id",
        "identity_theft_account_reviews",
        ["incident_id"],
    )
    op.create_index(
        "ix_identity_theft_account_reviews_account_id",
        "identity_theft_account_reviews",
        ["account_id"],
    )
    op.create_index(
        "ix_identity_theft_account_reviews_document_id",
        "identity_theft_account_reviews",
        ["document_id"],
    )
    op.create_index(
        "ix_identity_theft_account_reviews_match_key",
        "identity_theft_account_reviews",
        ["match_key"],
    )

    op.create_table(
        "identity_theft_protections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("protection_type", identity_theft_protection_type, nullable=False),
        sa.Column("status", identity_theft_protection_status, nullable=False),
        sa.Column("placed_at", sa.Date(), nullable=True),
        sa.Column("expires_at", sa.Date(), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_identity_theft_protections_organization_id",
        "identity_theft_protections",
        ["organization_id"],
    )
    op.create_index(
        "ix_identity_theft_protections_case_id",
        "identity_theft_protections",
        ["case_id"],
    )
    op.create_index(
        "ix_identity_theft_protections_case_type",
        "identity_theft_protections",
        ["case_id", "protection_type"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_identity_theft_protections_case_type",
        table_name="identity_theft_protections",
    )
    op.drop_index(
        "ix_identity_theft_protections_case_id",
        table_name="identity_theft_protections",
    )
    op.drop_index(
        "ix_identity_theft_protections_organization_id",
        table_name="identity_theft_protections",
    )
    op.drop_table("identity_theft_protections")

    op.drop_index(
        "ix_identity_theft_account_reviews_match_key",
        table_name="identity_theft_account_reviews",
    )
    op.drop_index(
        "ix_identity_theft_account_reviews_document_id",
        table_name="identity_theft_account_reviews",
    )
    op.drop_index(
        "ix_identity_theft_account_reviews_account_id",
        table_name="identity_theft_account_reviews",
    )
    op.drop_index(
        "ix_identity_theft_account_reviews_incident_id",
        table_name="identity_theft_account_reviews",
    )
    op.drop_index(
        "ix_identity_theft_account_reviews_case_id",
        table_name="identity_theft_account_reviews",
    )
    op.drop_index(
        "ix_identity_theft_account_reviews_organization_id",
        table_name="identity_theft_account_reviews",
    )
    op.drop_table("identity_theft_account_reviews")

    op.drop_index(
        "ix_identity_theft_incidents_case_id",
        table_name="identity_theft_incidents",
    )
    op.drop_index(
        "ix_identity_theft_incidents_organization_id",
        table_name="identity_theft_incidents",
    )
    op.drop_table("identity_theft_incidents")

    sa.Enum(name="identity_theft_protection_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="identity_theft_protection_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="identity_theft_confirmation").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="identity_theft_issue_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="identity_theft_incident_status").drop(op.get_bind(), checkfirst=True)
