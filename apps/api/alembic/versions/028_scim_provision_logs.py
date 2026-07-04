"""SCIM provision audit log table.

Revision ID: 028_scim_provision_logs
Revises: 027_billing_usage_events
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "028_scim_provision_logs"
down_revision: str | None = "027_billing_usage_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE scim_resource_type AS ENUM ('user', 'group')")
    op.execute("CREATE TYPE scim_provision_operation AS ENUM ('create', 'update', 'deactivate')")

    op.create_table(
        "scim_provision_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "resource_type",
            postgresql.ENUM("user", "group", name="scim_resource_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "operation",
            postgresql.ENUM(
                "create",
                "update",
                "deactivate",
                name="scim_provision_operation",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("auth_mode", sa.String(length=32), nullable=False, server_default="staff"),
        sa.Column("provisioned_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["provisioned_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "resource_type",
            "external_id",
            name="uq_scim_provision_org_resource_external_id",
        ),
    )
    op.create_index(
        "ix_scim_provision_logs_org_resource",
        "scim_provision_logs",
        ["organization_id", "resource_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_scim_provision_logs_org_resource", table_name="scim_provision_logs")
    op.drop_table("scim_provision_logs")
    op.execute("DROP TYPE scim_provision_operation")
    op.execute("DROP TYPE scim_resource_type")
