"""Alembic migration: CRM appointments + reminder runs (LRP-205).

Revision ID: 107_appointment_reminders
Revises: 106_crm_automation_rules
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "107_appointment_reminders"
down_revision: str | None = "106_crm_automation_rules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

type_enum = postgresql.ENUM(
    "consultation",
    "call",
    "meeting",
    "follow_up",
    "review",
    name="crm_appointment_type",
    create_type=False,
)
status_enum = postgresql.ENUM(
    "scheduled",
    "completed",
    "cancelled",
    "no_show",
    name="crm_appointment_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "consultation",
        "call",
        "meeting",
        "follow_up",
        "review",
        name="crm_appointment_type",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "scheduled",
        "completed",
        "cancelled",
        "no_show",
        name="crm_appointment_status",
    ).create(bind, checkfirst=True)

    op.create_table(
        "crm_appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("appointment_type", type_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("meeting_url", sa.String(length=500), nullable=True),
        sa.Column("related_name", sa.String(length=255), nullable=True),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("borrower_name", sa.String(length=255), nullable=True),
        sa.Column("borrower_email", sa.String(length=255), nullable=True),
        sa.Column("borrower_phone", sa.String(length=50), nullable=True),
        sa.Column("referring_lo_email", sa.String(length=255), nullable=True),
        sa.Column("referring_lo_name", sa.String(length=255), nullable=True),
        sa.Column("tcpa_consent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
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
    )
    op.create_index("ix_crm_appointments_organization_id", "crm_appointments", ["organization_id"])
    op.create_index("ix_crm_appointments_case_id", "crm_appointments", ["case_id"])
    op.create_index("ix_crm_appointments_status", "crm_appointments", ["status"])
    op.create_index("ix_crm_appointments_starts_at", "crm_appointments", ["starts_at"])

    op.create_table(
        "appointment_reminder_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "appointment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crm_appointments.id"),
            nullable=False,
        ),
        sa.Column("offset_key", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column(
            "matrix_dispatch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_matrix_dispatches.id"),
            nullable=True,
        ),
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
        sa.UniqueConstraint(
            "appointment_id",
            "offset_key",
            name="uq_appointment_reminder_runs_appointment_offset",
        ),
    )
    op.create_index(
        "ix_appointment_reminder_runs_organization_id",
        "appointment_reminder_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_appointment_reminder_runs_appointment_id",
        "appointment_reminder_runs",
        ["appointment_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_appointment_reminder_runs_appointment_id",
        table_name="appointment_reminder_runs",
    )
    op.drop_index(
        "ix_appointment_reminder_runs_organization_id",
        table_name="appointment_reminder_runs",
    )
    op.drop_table("appointment_reminder_runs")
    op.drop_index("ix_crm_appointments_starts_at", table_name="crm_appointments")
    op.drop_index("ix_crm_appointments_status", table_name="crm_appointments")
    op.drop_index("ix_crm_appointments_case_id", table_name="crm_appointments")
    op.drop_index("ix_crm_appointments_organization_id", table_name="crm_appointments")
    op.drop_table("crm_appointments")
    postgresql.ENUM(name="crm_appointment_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="crm_appointment_type").drop(op.get_bind(), checkfirst=True)
