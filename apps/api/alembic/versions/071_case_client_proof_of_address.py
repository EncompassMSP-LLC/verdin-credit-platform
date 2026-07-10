"""Case and client proof-of-address document references for mail packets.

Revision ID: 071_case_proof_address
Revises: 070_case_client_identity_document
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "071_case_proof_address"
down_revision: str | None = "070_case_identity_doc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("proof_of_address_document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_cases_proof_of_address_document_id_documents",
        "cases",
        "documents",
        ["proof_of_address_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_cases_proof_of_address_document_id",
        "cases",
        ["proof_of_address_document_id"],
        unique=False,
    )

    op.add_column(
        "clients",
        sa.Column("proof_of_address_document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_clients_proof_of_address_document_id_documents",
        "clients",
        "documents",
        ["proof_of_address_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_clients_proof_of_address_document_id",
        "clients",
        ["proof_of_address_document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_clients_proof_of_address_document_id", table_name="clients")
    op.drop_constraint(
        "fk_clients_proof_of_address_document_id_documents", "clients", type_="foreignkey"
    )
    op.drop_column("clients", "proof_of_address_document_id")

    op.drop_index("ix_cases_proof_of_address_document_id", table_name="cases")
    op.drop_constraint(
        "fk_cases_proof_of_address_document_id_documents", "cases", type_="foreignkey"
    )
    op.drop_column("cases", "proof_of_address_document_id")
