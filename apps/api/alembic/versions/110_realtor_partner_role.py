"""Alembic migration: realtor partner role + invite/credential tokens (LRP-301).

Revision ID: 110_realtor_partner_role
Revises: 109_weekly_partner_digest
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "110_realtor_partner_role"
down_revision: str | None = "109_weekly_partner_digest"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE partner_role ADD VALUE IF NOT EXISTS 'realtor'")

    op.create_table(
        "partner_realtor_invites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "partnership_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_partnerships.id"),
            nullable=False,
        ),
        sa.Column(
            "partner_organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "invited_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.UniqueConstraint("token_hash", name="uq_partner_realtor_invites_token_hash"),
    )
    op.create_index(
        "ix_partner_realtor_invites_organization_id",
        "partner_realtor_invites",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_realtor_invites_partnership_id",
        "partner_realtor_invites",
        ["partnership_id"],
    )
    op.create_index(
        "ix_partner_realtor_invites_partner_organization_id",
        "partner_realtor_invites",
        ["partner_organization_id"],
    )
    op.create_index("ix_partner_realtor_invites_email", "partner_realtor_invites", ["email"])

    op.create_table(
        "partner_realtor_credential_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.UniqueConstraint("token_hash", name="uq_partner_realtor_cred_token_hash"),
    )
    op.create_index(
        "ix_partner_realtor_credential_tokens_organization_id",
        "partner_realtor_credential_tokens",
        ["organization_id"],
    )
    op.create_index(
        "ix_partner_realtor_credential_tokens_user_id",
        "partner_realtor_credential_tokens",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_partner_realtor_credential_tokens_user_id",
        table_name="partner_realtor_credential_tokens",
    )
    op.drop_index(
        "ix_partner_realtor_credential_tokens_organization_id",
        table_name="partner_realtor_credential_tokens",
    )
    op.drop_table("partner_realtor_credential_tokens")
    op.drop_index("ix_partner_realtor_invites_email", table_name="partner_realtor_invites")
    op.drop_index(
        "ix_partner_realtor_invites_partner_organization_id",
        table_name="partner_realtor_invites",
    )
    op.drop_index(
        "ix_partner_realtor_invites_partnership_id",
        table_name="partner_realtor_invites",
    )
    op.drop_index(
        "ix_partner_realtor_invites_organization_id",
        table_name="partner_realtor_invites",
    )
    op.drop_table("partner_realtor_invites")
    # PostgreSQL cannot easily drop enum values; leave partner_role.realtor in place.
