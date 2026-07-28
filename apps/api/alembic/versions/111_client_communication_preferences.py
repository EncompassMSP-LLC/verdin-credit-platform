"""Alembic migration: client communication preferences (LRP-209).

Revision ID: 111_client_comm_prefs
Revises: 110_realtor_partner_role
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "111_client_comm_prefs"
down_revision: str | None = "110_realtor_partner_role"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE preferred_communication_channel AS ENUM ("
        "'mail', 'phone', 'email', 'text'"
        ")"
    )
    op.execute(
        "CREATE TYPE attorney_representation_status AS ENUM ("
        "'none', 'represented', 'unknown'"
        ")"
    )
    op.execute(
        "CREATE TYPE dnc_assistance_status AS ENUM ("
        "'not_started', 'consent_recorded', 'registry_link_opened', "
        "'awaiting_email_confirmation', 'completed', 'abandoned'"
        ")"
    )

    op.create_table(
        "client_communication_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "preferred_channel",
            postgresql.ENUM(
                "mail",
                "phone",
                "email",
                "text",
                name="preferred_communication_channel",
                create_type=False,
            ),
            nullable=False,
            server_default="mail",
        ),
        sa.Column("do_not_text", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("do_not_email", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("best_calling_hours", sa.String(length=255), nullable=True),
        sa.Column(
            "workplace_calls_prohibited",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "attorney_representation_status",
            postgresql.ENUM(
                "none",
                "represented",
                "unknown",
                name="attorney_representation_status",
                create_type=False,
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "collector_opt_out_recorded",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("collector_opt_out_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "dnc_assistance_requested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "dnc_consent_attested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "dnc_phone_ownership_confirmed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "dnc_disclosure_acknowledged",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("dnc_phone_number", sa.String(length=50), nullable=True),
        sa.Column(
            "dnc_status",
            postgresql.ENUM(
                "not_started",
                "consent_recorded",
                "registry_link_opened",
                "awaiting_email_confirmation",
                "completed",
                "abandoned",
                name="dnc_assistance_status",
                create_type=False,
            ),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("dnc_registry_opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dnc_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dnc_followup_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "preference_events",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
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
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id", name="uq_client_communication_preferences_client"),
    )
    op.create_index(
        "ix_client_communication_preferences_organization_id",
        "client_communication_preferences",
        ["organization_id"],
    )
    op.create_index(
        "ix_client_communication_preferences_client_id",
        "client_communication_preferences",
        ["client_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_client_communication_preferences_client_id",
        table_name="client_communication_preferences",
    )
    op.drop_index(
        "ix_client_communication_preferences_organization_id",
        table_name="client_communication_preferences",
    )
    op.drop_table("client_communication_preferences")
    op.execute("DROP TYPE IF EXISTS dnc_assistance_status")
    op.execute("DROP TYPE IF EXISTS attorney_representation_status")
    op.execute("DROP TYPE IF EXISTS preferred_communication_channel")
