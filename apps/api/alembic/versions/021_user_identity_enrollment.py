"""User identity enrollment tables.

Revision ID: 021_user_identity_enrollment
Revises: 019_organization_api_keys
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "021_user_identity_enrollment"
down_revision: str | None = "019_organization_api_keys"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_totp_enrollments",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encrypted_secret", sa.Text(), nullable=True),
        sa.Column("pending_encrypted_secret", sa.Text(), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "user_sso_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("issuer_url", sa.String(length=500), nullable=False),
        sa.Column("idp_subject", sa.String(length=255), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "issuer_url", "idp_subject", name="uq_user_sso_idp_subject"
        ),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_sso_per_provider"),
    )
    op.create_index("ix_user_sso_enrollments_user_id", "user_sso_enrollments", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_sso_enrollments_user_id", table_name="user_sso_enrollments")
    op.drop_table("user_sso_enrollments")
    op.drop_table("user_totp_enrollments")
