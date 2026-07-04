"""SMS marketing campaign run audit table.

Revision ID: 034_sms_marketing_campaign_runs
Revises: 033_idp_federation_providers
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "034_sms_marketing_campaign_runs"
down_revision: str | None = "033_idp_federation_providers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE TYPE sms_marketing_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute(
        "CREATE TYPE sms_marketing_campaign_status AS ENUM ('pending', 'running', 'completed', 'failed')"
    )

    op.create_table(
        "sms_marketing_campaign_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_name", sa.String(length=120), nullable=False),
        sa.Column("message_body", sa.Text(), nullable=False),
        sa.Column("recipient_user_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="sms_marketing_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "running",
                "completed",
                "failed",
                name="sms_marketing_campaign_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("recipients_queued", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("messages_sent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("messages_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sms_marketing_campaign_runs_org_started",
        "sms_marketing_campaign_runs",
        ["organization_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sms_marketing_campaign_runs_org_started",
        table_name="sms_marketing_campaign_runs",
    )
    op.drop_table("sms_marketing_campaign_runs")
    op.execute("DROP TYPE sms_marketing_campaign_status")
    op.execute("DROP TYPE sms_marketing_trigger_source")
