"""Clients and client contacts tables.

Revision ID: 013_clients_and_contacts
Revises: 012_in_app_notifications
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "013_clients_and_contacts"
down_revision: str | None = "012_in_app_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE client_status AS ENUM ('active', 'inactive')")
    op.execute(
        "CREATE TYPE contact_relationship AS ENUM ("
        "'primary', 'spouse', 'attorney', 'authorized', 'other'"
        ")"
    )

    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM("active", "inactive", name="client_status", create_type=False),
            nullable=False,
            server_default="active",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
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
    op.create_index("ix_clients_organization_id", "clients", ["organization_id"])
    op.create_index("ix_clients_status", "clients", ["status"])

    op.create_table(
        "client_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column(
            "relationship",
            postgresql.ENUM(
                "primary",
                "spouse",
                "attorney",
                "authorized",
                "other",
                name="contact_relationship",
                create_type=False,
            ),
            nullable=False,
            server_default="other",
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
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
    )
    op.create_index("ix_client_contacts_organization_id", "client_contacts", ["organization_id"])
    op.create_index("ix_client_contacts_client_id", "client_contacts", ["client_id"])


def downgrade() -> None:
    op.drop_index("ix_client_contacts_client_id", table_name="client_contacts")
    op.drop_index("ix_client_contacts_organization_id", table_name="client_contacts")
    op.drop_table("client_contacts")
    op.drop_index("ix_clients_status", table_name="clients")
    op.drop_index("ix_clients_organization_id", table_name="clients")
    op.drop_table("clients")
    op.execute("DROP TYPE contact_relationship")
    op.execute("DROP TYPE client_status")
