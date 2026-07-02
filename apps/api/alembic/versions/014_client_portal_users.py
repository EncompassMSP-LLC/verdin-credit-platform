"""Client portal users table.

Revision ID: 014_client_portal_users
Revises: 013_clients_and_contacts
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "014_client_portal_users"
down_revision: str | None = "013_clients_and_contacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client_portal_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        "ix_client_portal_users_organization_id", "client_portal_users", ["organization_id"]
    )
    op.create_index("ix_client_portal_users_client_id", "client_portal_users", ["client_id"])
    op.create_index("ix_client_portal_users_email", "client_portal_users", ["email"])


def downgrade() -> None:
    op.drop_index("ix_client_portal_users_email", table_name="client_portal_users")
    op.drop_index("ix_client_portal_users_client_id", table_name="client_portal_users")
    op.drop_index("ix_client_portal_users_organization_id", table_name="client_portal_users")
    op.drop_table("client_portal_users")
