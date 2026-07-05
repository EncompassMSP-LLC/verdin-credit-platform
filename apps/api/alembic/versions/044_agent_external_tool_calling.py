"""Human-gated agent external tool invocation audit table.

Revision ID: 044_agent_external_tool_calling
Revises: 043_dispute_bureau_submission
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "044_agent_external_tool_calling"
down_revision: str | None = "043_dispute_bureau_submission"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE agent_external_tool_kind AS ENUM "
        "('web_lookup', 'document_fetch', 'crm_update')"
    )
    op.execute(
        "CREATE TYPE agent_tool_invocation_status AS ENUM "
        "('pending_approval', 'invoked', 'rejected', 'failed')"
    )

    op.create_table(
        "agent_tool_invocation_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tool_kind",
            postgresql.ENUM(
                "web_lookup",
                "document_fetch",
                "crm_update",
                name="agent_external_tool_kind",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "invoked",
                "rejected",
                "failed",
                name="agent_tool_invocation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invocation_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["timeline_event_id"], ["timeline_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_tool_invocation_requests_org_requested",
        "agent_tool_invocation_requests",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_agent_tool_invocation_requests_case",
        "agent_tool_invocation_requests",
        ["case_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_tool_invocation_requests_case",
        table_name="agent_tool_invocation_requests",
    )
    op.drop_index(
        "ix_agent_tool_invocation_requests_org_requested",
        table_name="agent_tool_invocation_requests",
    )
    op.drop_table("agent_tool_invocation_requests")
    op.execute("DROP TYPE agent_tool_invocation_status")
    op.execute("DROP TYPE agent_external_tool_kind")
