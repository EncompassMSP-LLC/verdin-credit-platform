"""Add client mailing address fields for intake and consent documents.

Revision ID: 074_client_mailing_address
Revises: 073_consent_templates
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "074_client_mailing_address"
down_revision: str | None = "073_consent_templates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "clients", sa.Column("mailing_address_line1", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "clients", sa.Column("mailing_address_line2", sa.String(length=255), nullable=True)
    )
    op.add_column("clients", sa.Column("mailing_city", sa.String(length=100), nullable=True))
    op.add_column("clients", sa.Column("mailing_state", sa.String(length=50), nullable=True))
    op.add_column("clients", sa.Column("mailing_postal_code", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "mailing_postal_code")
    op.drop_column("clients", "mailing_state")
    op.drop_column("clients", "mailing_city")
    op.drop_column("clients", "mailing_address_line2")
    op.drop_column("clients", "mailing_address_line1")
