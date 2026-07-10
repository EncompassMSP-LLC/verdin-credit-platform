"""Case and client identity document references for mail packets.

Revision ID: 070_case_identity_doc
Revises: 069_full_auto_bureau_api
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "070_case_identity_doc"
down_revision: str | None = "069_full_auto_bureau_api"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("identity_document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_cases_identity_document_id_documents",
        "cases",
        "documents",
        ["identity_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_cases_identity_document_id",
        "cases",
        ["identity_document_id"],
        unique=False,
    )

    op.add_column(
        "clients",
        sa.Column("identity_document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_clients_identity_document_id_documents",
        "clients",
        "documents",
        ["identity_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_clients_identity_document_id",
        "clients",
        ["identity_document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_clients_identity_document_id", table_name="clients")
    op.drop_constraint("fk_clients_identity_document_id_documents", "clients", type_="foreignkey")
    op.drop_column("clients", "identity_document_id")

    op.drop_index("ix_cases_identity_document_id", table_name="cases")
    op.drop_constraint("fk_cases_identity_document_id_documents", "cases", type_="foreignkey")
    op.drop_column("cases", "identity_document_id")
