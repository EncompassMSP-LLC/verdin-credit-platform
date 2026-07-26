"""Partner CRM contacts + contact access audit actions (LRP-101).

Revision ID: 099_partner_contacts
Revises: 098_partner_readiness_actions
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "099_partner_contacts"
down_revision: str | None = "098_partner_readiness_actions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

partner_contact_role = postgresql.ENUM(
    "loan_officer",
    "realtor",
    "branch_manager",
    "executive",
    "operations",
    "other",
    name="partner_contact_role",
    create_type=False,
)


def upgrade() -> None:
    partner_contact_role.create(op.get_bind(), checkfirst=True)
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'contact_list'")
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'contact_create'")
    op.execute("ALTER TYPE partner_access_action ADD VALUE IF NOT EXISTS 'contact_update'")

    op.create_table(
        "partner_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("partnership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cro_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("job_title", sa.String(120), nullable=True),
        sa.Column("contact_role", partner_contact_role, nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["partnership_id"], ["org_partnerships.id"]),
        sa.ForeignKeyConstraint(["cro_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
    )
    op.create_index("ix_partner_contacts_partnership_id", "partner_contacts", ["partnership_id"])
    op.create_index(
        "ix_partner_contacts_cro_organization_id", "partner_contacts", ["cro_organization_id"]
    )
    op.create_index("ix_partner_contacts_user_id", "partner_contacts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_partner_contacts_user_id", table_name="partner_contacts")
    op.drop_index("ix_partner_contacts_cro_organization_id", table_name="partner_contacts")
    op.drop_index("ix_partner_contacts_partnership_id", table_name="partner_contacts")
    op.drop_table("partner_contacts")
    partner_contact_role.drop(op.get_bind(), checkfirst=True)
