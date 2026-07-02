"""Secure messaging thread tables for portal and staff communication.

Revision ID: 018_secure_messaging_threads
Revises: 017_compliance_consent_retention
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "018_secure_messaging_threads"
down_revision: str | None = "017_compliance_consent_retention"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE message_thread_status AS ENUM ('open', 'closed')")
    op.execute("CREATE TYPE message_sender_role AS ENUM ('portal_client', 'staff')")

    op.create_table(
        "message_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("open", "closed", name="message_thread_status", create_type=False),
            nullable=False,
            server_default="open",
        ),
        sa.Column("subject", sa.String(length=255), nullable=True),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "case_id", name="uq_message_threads_org_case"),
    )
    op.create_index("ix_message_threads_organization_id", "message_threads", ["organization_id"])
    op.create_index("ix_message_threads_case_id", "message_threads", ["case_id"])
    op.create_index("ix_message_threads_client_id", "message_threads", ["client_id"])

    op.create_table(
        "thread_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "sender_role",
            postgresql.ENUM(
                "portal_client",
                "staff",
                name="message_sender_role",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("portal_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("staff_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["message_threads.id"]),
        sa.ForeignKeyConstraint(["portal_user_id"], ["client_portal_users.id"]),
        sa.ForeignKeyConstraint(["staff_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_thread_messages_organization_id", "thread_messages", ["organization_id"])
    op.create_index("ix_thread_messages_thread_id", "thread_messages", ["thread_id"])


def downgrade() -> None:
    op.drop_index("ix_thread_messages_thread_id", table_name="thread_messages")
    op.drop_index("ix_thread_messages_organization_id", table_name="thread_messages")
    op.drop_table("thread_messages")

    op.drop_index("ix_message_threads_client_id", table_name="message_threads")
    op.drop_index("ix_message_threads_case_id", table_name="message_threads")
    op.drop_index("ix_message_threads_organization_id", table_name="message_threads")
    op.drop_table("message_threads")

    op.execute("DROP TYPE message_sender_role")
    op.execute("DROP TYPE message_thread_status")
