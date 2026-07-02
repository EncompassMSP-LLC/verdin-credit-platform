"""Compliance center — consent records and retention policy placeholders.

Revision ID: 017_compliance_consent_retention
Revises: 016_email_delivery_logs
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "017_compliance_consent_retention"
down_revision: str | None = "016_email_delivery_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE consent_type AS ENUM ("
        "'croa_services', 'fcra_dispute', 'fdcpa_contact', 'marketing', 'data_processing'"
        ")"
    )
    op.execute("CREATE TYPE consent_status AS ENUM ('granted', 'withdrawn')")
    op.execute(
        "CREATE TYPE retention_scope AS ENUM ("
        "'documents', 'communications', 'audit_logs', 'client_profiles'"
        ")"
    )

    op.create_table(
        "consent_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "consent_type",
            postgresql.ENUM(
                "croa_services",
                "fcra_dispute",
                "fdcpa_contact",
                "marketing",
                "data_processing",
                name="consent_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM("granted", "withdrawn", name="consent_status", create_type=False),
            nullable=False,
            server_default="granted",
        ),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="staff"),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consent_records_organization_id", "consent_records", ["organization_id"])
    op.create_index("ix_consent_records_client_id", "consent_records", ["client_id"])
    op.create_index("ix_consent_records_case_id", "consent_records", ["case_id"])
    op.create_index("ix_consent_records_consent_type", "consent_records", ["consent_type"])
    op.create_index("ix_consent_records_status", "consent_records", ["status"])

    op.create_table(
        "retention_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "scope",
            postgresql.ENUM(
                "documents",
                "communications",
                "audit_logs",
                "client_profiles",
                name="retention_scope",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_retention_policies_organization_id", "retention_policies", ["organization_id"]
    )
    op.create_index("ix_retention_policies_scope", "retention_policies", ["scope"])


def downgrade() -> None:
    op.drop_index("ix_retention_policies_scope", table_name="retention_policies")
    op.drop_index("ix_retention_policies_organization_id", table_name="retention_policies")
    op.drop_table("retention_policies")

    op.drop_index("ix_consent_records_status", table_name="consent_records")
    op.drop_index("ix_consent_records_consent_type", table_name="consent_records")
    op.drop_index("ix_consent_records_case_id", table_name="consent_records")
    op.drop_index("ix_consent_records_client_id", table_name="consent_records")
    op.drop_index("ix_consent_records_organization_id", table_name="consent_records")
    op.drop_table("consent_records")

    op.execute("DROP TYPE retention_scope")
    op.execute("DROP TYPE consent_status")
    op.execute("DROP TYPE consent_type")
