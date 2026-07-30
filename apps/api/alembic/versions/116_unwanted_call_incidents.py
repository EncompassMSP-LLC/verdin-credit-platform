"""Alembic migration: unwanted-call complaint incidents (LRP-209A).

Revision ID: 116_unwanted_call_incidents
Revises: 115_issue_evidence_links
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "116_unwanted_call_incidents"
down_revision: str | None = "115_issue_evidence_links"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE unwanted_call_party_type AS ENUM ("
        "'creditor', 'collector', 'telemarketer', 'unknown')"
    )
    op.execute("CREATE TYPE unwanted_call_channel AS ENUM (" "'phone', 'voip', 'sms', 'unknown')")
    op.execute(
        "CREATE TYPE unwanted_call_incident_status AS ENUM ("
        "'open', 'documenting', 'draft_ready', 'submitted_externally', "
        "'follow_up_due', 'closed', 'abandoned')"
    )
    op.execute(
        "CREATE TYPE unwanted_call_complaint_target AS ENUM ("
        "'none', 'ftc', 'cfpb', 'state_ag', 'carrier', 'other')"
    )
    op.execute(
        "CREATE TYPE unwanted_call_external_submission_status AS ENUM ("
        "'not_started', 'draft_prepared', 'client_submitted', 'staff_recorded')"
    )

    op.create_table(
        "unwanted_call_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("creditor_or_collector_name", sa.String(length=255), nullable=True),
        sa.Column(
            "party_type",
            postgresql.ENUM(
                "creditor",
                "collector",
                "telemarketer",
                "unknown",
                name="unwanted_call_party_type",
                create_type=False,
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("called_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("caller_number", sa.String(length=50), nullable=True),
        sa.Column("called_number", sa.String(length=50), nullable=True),
        sa.Column(
            "channel",
            postgresql.ENUM(
                "phone",
                "voip",
                "sms",
                "unknown",
                name="unwanted_call_channel",
                create_type=False,
            ),
            nullable=False,
            server_default="phone",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "preference_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "eligibility_guidance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "open",
                "documenting",
                "draft_ready",
                "submitted_externally",
                "follow_up_due",
                "closed",
                "abandoned",
                name="unwanted_call_incident_status",
                create_type=False,
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column("follow_up_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("follow_up_notes", sa.Text(), nullable=True),
        sa.Column(
            "complaint_target",
            postgresql.ENUM(
                "none",
                "ftc",
                "cfpb",
                "state_ag",
                "carrier",
                "other",
                name="unwanted_call_complaint_target",
                create_type=False,
            ),
            nullable=False,
            server_default="none",
        ),
        sa.Column(
            "external_submission_status",
            postgresql.ENUM(
                "not_started",
                "draft_prepared",
                "client_submitted",
                "staff_recorded",
                name="unwanted_call_external_submission_status",
                create_type=False,
            ),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("evidence_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("draft_text", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["evidence_document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_unwanted_call_incidents_organization_id",
        "unwanted_call_incidents",
        ["organization_id"],
    )
    op.create_index(
        "ix_unwanted_call_incidents_client_id",
        "unwanted_call_incidents",
        ["client_id"],
    )
    op.create_index(
        "ix_unwanted_call_incidents_case_id",
        "unwanted_call_incidents",
        ["case_id"],
    )
    op.create_index(
        "ix_unwanted_call_incidents_status",
        "unwanted_call_incidents",
        ["status"],
    )
    op.create_index(
        "ix_unwanted_call_incidents_org_client",
        "unwanted_call_incidents",
        ["organization_id", "client_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_unwanted_call_incidents_org_client", table_name="unwanted_call_incidents")
    op.drop_index("ix_unwanted_call_incidents_status", table_name="unwanted_call_incidents")
    op.drop_index("ix_unwanted_call_incidents_case_id", table_name="unwanted_call_incidents")
    op.drop_index("ix_unwanted_call_incidents_client_id", table_name="unwanted_call_incidents")
    op.drop_index(
        "ix_unwanted_call_incidents_organization_id",
        table_name="unwanted_call_incidents",
    )
    op.drop_table("unwanted_call_incidents")
    op.execute("DROP TYPE IF EXISTS unwanted_call_external_submission_status")
    op.execute("DROP TYPE IF EXISTS unwanted_call_complaint_target")
    op.execute("DROP TYPE IF EXISTS unwanted_call_incident_status")
    op.execute("DROP TYPE IF EXISTS unwanted_call_channel")
    op.execute("DROP TYPE IF EXISTS unwanted_call_party_type")
