"""Alembic migration: secure message attachments (LRP-302B).

Revision ID: 119_message_attachments
Revises: 118_portal_notifications
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "119_message_attachments"
down_revision: str | None = "118_portal_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE message_attachment_scan_status AS ENUM ("
        "'pending', 'clean', 'rejected', 'failed'"
        ")"
    )
    op.execute("CREATE TYPE message_attachment_uploader AS ENUM ('staff', 'portal_client')")

    op.add_column(
        "thread_messages",
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "uq_thread_messages_org_staff_idempotency",
        "thread_messages",
        ["organization_id", "staff_user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL AND staff_user_id IS NOT NULL"),
    )
    op.create_index(
        "uq_thread_messages_org_portal_idempotency",
        "thread_messages",
        ["organization_id", "portal_user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL AND portal_user_id IS NOT NULL"),
    )

    op.create_table(
        "thread_message_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "uploaded_by_type",
            postgresql.ENUM(
                "staff",
                "portal_client",
                name="message_attachment_uploader",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("uploaded_by_staff_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by_portal_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("display_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column(
            "scan_status",
            postgresql.ENUM(
                "pending",
                "clean",
                "rejected",
                "failed",
                name="message_attachment_scan_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("scan_detail", sa.String(length=255), nullable=True),
        sa.Column("scanned_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["thread_messages.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_staff_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_portal_user_id"], ["client_portal_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_thread_message_attachments_org_case",
        "thread_message_attachments",
        ["organization_id", "case_id"],
    )
    op.create_index(
        "ix_thread_message_attachments_message_id",
        "thread_message_attachments",
        ["message_id"],
    )
    op.create_index(
        "uq_thread_message_attachments_document_active",
        "thread_message_attachments",
        ["document_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_thread_message_attachments_document_active",
        table_name="thread_message_attachments",
    )
    op.drop_index(
        "ix_thread_message_attachments_message_id",
        table_name="thread_message_attachments",
    )
    op.drop_index(
        "ix_thread_message_attachments_org_case",
        table_name="thread_message_attachments",
    )
    op.drop_table("thread_message_attachments")
    op.drop_index(
        "uq_thread_messages_org_portal_idempotency",
        table_name="thread_messages",
    )
    op.drop_index(
        "uq_thread_messages_org_staff_idempotency",
        table_name="thread_messages",
    )
    op.drop_column("thread_messages", "idempotency_key")
    op.execute("DROP TYPE message_attachment_scan_status")
    op.execute("DROP TYPE message_attachment_uploader")
