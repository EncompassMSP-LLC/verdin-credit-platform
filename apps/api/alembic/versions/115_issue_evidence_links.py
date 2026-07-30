"""Alembic migration: issue evidence vault links (LRP-208A).

Revision ID: 115_issue_evidence_links
Revises: 114_crm_automation_audit
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "115_issue_evidence_links"
down_revision: str | None = "114_crm_automation_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE issue_evidence_link_role AS ENUM ("
        "'supporting', 'primary', 'identity', 'statement')"
    )
    op.create_table(
        "issue_evidence_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", sa.String(length=512), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "supporting",
                "primary",
                "identity",
                "statement",
                name="issue_evidence_link_role",
                create_type=False,
            ),
            nullable=False,
            server_default="supporting",
        ),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_issue_evidence_links_organization_id",
        "issue_evidence_links",
        ["organization_id"],
    )
    op.create_index("ix_issue_evidence_links_case_id", "issue_evidence_links", ["case_id"])
    op.create_index(
        "ix_issue_evidence_links_document_id",
        "issue_evidence_links",
        ["document_id"],
    )
    op.create_index(
        "ix_issue_evidence_links_source_id",
        "issue_evidence_links",
        ["source_id"],
    )
    op.create_index(
        "uq_issue_evidence_links_case_source_doc_active",
        "issue_evidence_links",
        ["case_id", "source_id", "document_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_issue_evidence_links_case_source_doc_active",
        table_name="issue_evidence_links",
    )
    op.drop_index("ix_issue_evidence_links_source_id", table_name="issue_evidence_links")
    op.drop_index("ix_issue_evidence_links_document_id", table_name="issue_evidence_links")
    op.drop_index("ix_issue_evidence_links_case_id", table_name="issue_evidence_links")
    op.drop_index("ix_issue_evidence_links_organization_id", table_name="issue_evidence_links")
    op.drop_table("issue_evidence_links")
    op.execute("DROP TYPE IF EXISTS issue_evidence_link_role")
