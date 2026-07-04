"""SAML federation metadata upload audit table.

Revision ID: 037_saml_federation_metadata
Revises: 036_billing_invoice_collection
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "037_saml_federation_metadata"
down_revision: str | None = "036_billing_invoice_collection"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE saml_metadata_validation_status AS ENUM ('valid', 'invalid')")

    op.create_table(
        "saml_federation_metadata_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=True),
        sa.Column("metadata_xml", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=True),
        sa.Column(
            "validation_status",
            postgresql.ENUM(
                "valid",
                "invalid",
                name="saml_metadata_validation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("validation_message", sa.Text(), nullable=True),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_saml_federation_metadata_uploads_org_uploaded",
        "saml_federation_metadata_uploads",
        ["organization_id", "uploaded_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_saml_federation_metadata_uploads_org_uploaded",
        table_name="saml_federation_metadata_uploads",
    )
    op.drop_table("saml_federation_metadata_uploads")
    op.execute("DROP TYPE saml_metadata_validation_status")
