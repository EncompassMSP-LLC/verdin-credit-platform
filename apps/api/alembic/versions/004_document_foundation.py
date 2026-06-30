"""Document foundation — MinIO storage, versioning, duplicate detection.

Revision ID: 004_document_foundation
Revises: 003_credit_accounts
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "004_document_foundation"
down_revision: str | None = "003_credit_accounts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "documents", sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column("documents", sa.Column("storage_key", sa.String(500), nullable=True))
    op.add_column("documents", sa.Column("file_hash", sa.String(64), nullable=True))
    op.add_column(
        "documents",
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("documents", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("duplicate_of_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("is_duplicate", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.execute(
        """
        UPDATE documents d
        SET organization_id = c.organization_id,
            storage_key = d.file_path
        FROM cases c
        WHERE d.case_id = c.id
        """
    )

    op.alter_column("documents", "organization_id", nullable=False)
    op.alter_column("documents", "storage_key", nullable=False)
    op.alter_column("documents", "file_hash", nullable=False, server_default="")
    op.alter_column("documents", "file_hash", server_default=None)

    op.drop_column("documents", "file_path")

    op.create_foreign_key(
        "documents_organization_id_fkey",
        "documents",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "documents_account_id_fkey",
        "documents",
        "accounts",
        ["account_id"],
        ["id"],
    )
    op.create_foreign_key(
        "documents_duplicate_of_id_fkey",
        "documents",
        "documents",
        ["duplicate_of_id"],
        ["id"],
    )
    op.create_index("ix_documents_organization_id", "documents", ["organization_id"])
    op.create_index("ix_documents_file_hash", "documents", ["file_hash"])
    op.create_index("ix_documents_case_id", "documents", ["case_id"])

    op.create_table(
        "document_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_version"),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")

    op.drop_index("ix_documents_case_id", table_name="documents")
    op.drop_index("ix_documents_file_hash", table_name="documents")
    op.drop_index("ix_documents_organization_id", table_name="documents")
    op.drop_constraint("documents_duplicate_of_id_fkey", "documents", type_="foreignkey")
    op.drop_constraint("documents_account_id_fkey", "documents", type_="foreignkey")
    op.drop_constraint("documents_organization_id_fkey", "documents", type_="foreignkey")

    op.add_column("documents", sa.Column("file_path", sa.String(500), nullable=True))
    op.execute("UPDATE documents SET file_path = storage_key")
    op.alter_column("documents", "file_path", nullable=False)

    op.drop_column("documents", "is_duplicate")
    op.drop_column("documents", "duplicate_of_id")
    op.drop_column("documents", "description")
    op.drop_column("documents", "version_number")
    op.drop_column("documents", "file_hash")
    op.drop_column("documents", "storage_key")
    op.drop_column("documents", "account_id")
    op.drop_column("documents", "organization_id")
