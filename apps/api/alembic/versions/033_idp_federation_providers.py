"""IdP federation provider registry table.

Revision ID: 033_idp_federation_providers
Revises: 032_billing_invoicing_runs
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "033_idp_federation_providers"
down_revision: str | None = "032_billing_invoicing_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE idp_federation_provider_type AS ENUM ('oidc', 'saml')")

    op.create_table(
        "idp_federation_providers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=False),
        sa.Column(
            "provider_type",
            postgresql.ENUM(
                "oidc",
                "saml",
                name="idp_federation_provider_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("issuer_url", sa.String(length=500), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("registered_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["registered_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "provider_key",
            name="uq_idp_federation_org_provider_key",
        ),
    )
    op.create_index(
        "ix_idp_federation_providers_org",
        "idp_federation_providers",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_idp_federation_providers_org", table_name="idp_federation_providers")
    op.drop_table("idp_federation_providers")
    op.execute("DROP TYPE idp_federation_provider_type")
