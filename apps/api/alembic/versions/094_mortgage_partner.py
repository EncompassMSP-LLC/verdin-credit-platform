"""Mortgage partner partnerships, members, referrals, access audits.

Revision ID: 094_mortgage_partner
Revises: 093_widen_meta_pay_status
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "094_mortgage_partner"
down_revision: str | None = "093_widen_meta_pay_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

partner_org_type = postgresql.ENUM(
    "lender",
    "realtor",
    "broker",
    "operator",
    "other",
    name="partner_org_type",
    create_type=False,
)
partnership_status = postgresql.ENUM(
    "pending",
    "active",
    "paused",
    "ended",
    name="partnership_status",
    create_type=False,
)
partner_role = postgresql.ENUM(
    "lender_admin",
    "loan_officer",
    "credit_ops",
    "underwriter_view",
    "read_only",
    name="partner_role",
    create_type=False,
)
partner_referral_status = postgresql.ENUM(
    "new",
    "accepted",
    "in_progress",
    "completed",
    "declined",
    name="partner_referral_status",
    create_type=False,
)
partner_access_action = postgresql.ENUM(
    "partnership_view",
    "referral_list",
    "referral_view",
    "member_list",
    "member_create",
    "partnership_create",
    "referral_create",
    name="partner_access_action",
    create_type=False,
)


def upgrade() -> None:
    partner_org_type.create(op.get_bind(), checkfirst=True)
    partnership_status.create(op.get_bind(), checkfirst=True)
    partner_role.create(op.get_bind(), checkfirst=True)
    partner_referral_status.create(op.get_bind(), checkfirst=True)
    partner_access_action.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "org_partnerships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cro_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_type", partner_org_type, nullable=False),
        sa.Column("status", partnership_status, nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
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
        sa.ForeignKeyConstraint(["cro_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["partner_organization_id"], ["organizations.id"]),
        sa.UniqueConstraint(
            "cro_organization_id",
            "partner_organization_id",
            name="uq_org_partnerships_cro_partner",
        ),
    )
    op.create_index(
        "ix_org_partnerships_cro_organization_id", "org_partnerships", ["cro_organization_id"]
    )
    op.create_index(
        "ix_org_partnerships_partner_organization_id",
        "org_partnerships",
        ["partner_organization_id"],
    )
    op.create_index("ix_org_partnerships_status", "org_partnerships", ["status"])

    op.create_table(
        "org_partnership_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("partnership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_role", partner_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.ForeignKeyConstraint(["partnership_id"], ["org_partnerships.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint(
            "partnership_id",
            "user_id",
            name="uq_org_partnership_members_partnership_user",
        ),
    )
    op.create_index(
        "ix_org_partnership_members_partnership_id",
        "org_partnership_members",
        ["partnership_id"],
    )
    op.create_index(
        "ix_org_partnership_members_organization_id",
        "org_partnership_members",
        ["organization_id"],
    )
    op.create_index("ix_org_partnership_members_user_id", "org_partnership_members", ["user_id"])

    op.create_table(
        "partner_referrals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("partnership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cro_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", partner_referral_status, nullable=False),
        sa.Column("source_label", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("referred_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["partnership_id"], ["org_partnerships.id"]),
        sa.ForeignKeyConstraint(["cro_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["referred_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_partner_referrals_partnership_id", "partner_referrals", ["partnership_id"])
    op.create_index(
        "ix_partner_referrals_cro_organization_id",
        "partner_referrals",
        ["cro_organization_id"],
    )
    op.create_index("ix_partner_referrals_client_id", "partner_referrals", ["client_id"])
    op.create_index("ix_partner_referrals_case_id", "partner_referrals", ["case_id"])
    op.create_index("ix_partner_referrals_status", "partner_referrals", ["status"])

    op.create_table(
        "partner_access_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cro_organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partnership_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", partner_access_action, nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["cro_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["partnership_id"], ["org_partnerships.id"]),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_partner_access_audits_cro_organization_id",
        "partner_access_audits",
        ["cro_organization_id"],
    )
    op.create_index(
        "ix_partner_access_audits_partnership_id",
        "partner_access_audits",
        ["partnership_id"],
    )
    op.create_index(
        "ix_partner_access_audits_actor_user_id", "partner_access_audits", ["actor_user_id"]
    )
    op.create_index("ix_partner_access_audits_action", "partner_access_audits", ["action"])


def downgrade() -> None:
    op.drop_index("ix_partner_access_audits_action", table_name="partner_access_audits")
    op.drop_index("ix_partner_access_audits_actor_user_id", table_name="partner_access_audits")
    op.drop_index("ix_partner_access_audits_partnership_id", table_name="partner_access_audits")
    op.drop_index(
        "ix_partner_access_audits_cro_organization_id", table_name="partner_access_audits"
    )
    op.drop_table("partner_access_audits")

    op.drop_index("ix_partner_referrals_status", table_name="partner_referrals")
    op.drop_index("ix_partner_referrals_case_id", table_name="partner_referrals")
    op.drop_index("ix_partner_referrals_client_id", table_name="partner_referrals")
    op.drop_index("ix_partner_referrals_cro_organization_id", table_name="partner_referrals")
    op.drop_index("ix_partner_referrals_partnership_id", table_name="partner_referrals")
    op.drop_table("partner_referrals")

    op.drop_index("ix_org_partnership_members_user_id", table_name="org_partnership_members")
    op.drop_index(
        "ix_org_partnership_members_organization_id", table_name="org_partnership_members"
    )
    op.drop_index("ix_org_partnership_members_partnership_id", table_name="org_partnership_members")
    op.drop_table("org_partnership_members")

    op.drop_index("ix_org_partnerships_status", table_name="org_partnerships")
    op.drop_index("ix_org_partnerships_partner_organization_id", table_name="org_partnerships")
    op.drop_index("ix_org_partnerships_cro_organization_id", table_name="org_partnerships")
    op.drop_table("org_partnerships")

    partner_access_action.drop(op.get_bind(), checkfirst=True)
    partner_referral_status.drop(op.get_bind(), checkfirst=True)
    partner_role.drop(op.get_bind(), checkfirst=True)
    partnership_status.drop(op.get_bind(), checkfirst=True)
    partner_org_type.drop(op.get_bind(), checkfirst=True)
