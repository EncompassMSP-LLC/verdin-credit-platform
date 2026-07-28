"""Alembic migration: partner nurture drip (LRP-206).

Revision ID: 108_partner_nurture_drip
Revises: 107_appointment_reminders
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "108_partner_nurture_drip"
down_revision: str | None = "107_appointment_reminders"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "lender",
        "realtor",
        "partner_lead",
        name="partner_nurture_audience",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "lead",
        "discovery",
        "active",
        "nurture",
        "inactive",
        name="partner_nurture_lifecycle_stage",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "email",
        "sms",
        "in_app",
        name="partner_nurture_channel",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "active",
        "paused",
        "completed",
        "exited",
        name="partner_nurture_enrollment_status",
    ).create(bind, checkfirst=True)

    audience = postgresql.ENUM(name="partner_nurture_audience", create_type=False)
    lifecycle = postgresql.ENUM(name="partner_nurture_lifecycle_stage", create_type=False)
    channel = postgresql.ENUM(name="partner_nurture_channel", create_type=False)
    enrollment_status = postgresql.ENUM(name="partner_nurture_enrollment_status", create_type=False)

    op.create_table(
        "partner_nurture_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("audience", audience, nullable=False),
        sa.Column("enrollment_lifecycle_stage", lifecycle, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
    op.create_index(
        "ix_partner_nurture_programs_organization_id",
        "partner_nurture_programs",
        ["organization_id"],
    )

    op.create_table(
        "partner_nurture_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_nurture_programs.id"),
            nullable=False,
        ),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("delay_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("channel", channel, nullable=False),
        sa.Column("template_key", sa.String(length=100), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False),
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
            "program_id",
            "step_order",
            name="uq_partner_nurture_steps_program_order",
        ),
    )
    op.create_index(
        "ix_partner_nurture_steps_organization_id",
        "partner_nurture_steps",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_nurture_steps_program_id",
        "partner_nurture_steps",
        ["program_id"],
    )

    op.create_table(
        "partner_nurture_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_nurture_programs.id"),
            nullable=False,
        ),
        sa.Column(
            "partnership_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_partnerships.id"),
            nullable=True,
        ),
        sa.Column("contact_name", sa.String(length=255), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("status", enrollment_status, nullable=False),
        sa.Column("current_step_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exit_reason", sa.String(length=100), nullable=True),
        sa.Column(
            "marketing_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "tcpa_consent",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
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
    op.create_index(
        "ix_partner_nurture_enrollments_organization_id",
        "partner_nurture_enrollments",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_nurture_enrollments_program_id",
        "partner_nurture_enrollments",
        ["program_id"],
    )
    op.create_index(
        "ix_partner_nurture_enrollments_partnership_id",
        "partner_nurture_enrollments",
        ["partnership_id"],
    )
    op.create_index(
        "ix_partner_nurture_enrollments_status",
        "partner_nurture_enrollments",
        ["status"],
    )

    op.create_table(
        "partner_nurture_delivery_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "enrollment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_nurture_enrollments.id"),
            nullable=False,
        ),
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_nurture_programs.id"),
            nullable=False,
        ),
        sa.Column(
            "step_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partner_nurture_steps.id"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
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
            "enrollment_id",
            "step_id",
            name="uq_partner_nurture_delivery_enrollment_step",
        ),
    )
    op.create_index(
        "ix_partner_nurture_delivery_runs_organization_id",
        "partner_nurture_delivery_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_nurture_delivery_runs_enrollment_id",
        "partner_nurture_delivery_runs",
        ["enrollment_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_index(
        "ix_partner_nurture_delivery_runs_enrollment_id",
        table_name="partner_nurture_delivery_runs",
    )
    op.drop_index(
        "ix_partner_nurture_delivery_runs_organization_id",
        table_name="partner_nurture_delivery_runs",
    )
    op.drop_table("partner_nurture_delivery_runs")
    op.drop_index(
        "ix_partner_nurture_enrollments_status",
        table_name="partner_nurture_enrollments",
    )
    op.drop_index(
        "ix_partner_nurture_enrollments_partnership_id",
        table_name="partner_nurture_enrollments",
    )
    op.drop_index(
        "ix_partner_nurture_enrollments_program_id",
        table_name="partner_nurture_enrollments",
    )
    op.drop_index(
        "ix_partner_nurture_enrollments_organization_id",
        table_name="partner_nurture_enrollments",
    )
    op.drop_table("partner_nurture_enrollments")
    op.drop_index("ix_partner_nurture_steps_program_id", table_name="partner_nurture_steps")
    op.drop_index(
        "ix_partner_nurture_steps_organization_id",
        table_name="partner_nurture_steps",
    )
    op.drop_table("partner_nurture_steps")
    op.drop_index(
        "ix_partner_nurture_programs_organization_id",
        table_name="partner_nurture_programs",
    )
    op.drop_table("partner_nurture_programs")
    postgresql.ENUM(name="partner_nurture_enrollment_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="partner_nurture_channel").drop(bind, checkfirst=True)
    postgresql.ENUM(name="partner_nurture_lifecycle_stage").drop(bind, checkfirst=True)
    postgresql.ENUM(name="partner_nurture_audience").drop(bind, checkfirst=True)
