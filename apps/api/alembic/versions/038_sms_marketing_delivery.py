"""Link SMS delivery logs to marketing campaign runs.

Revision ID: 038_sms_marketing_delivery
Revises: 037_saml_federation_metadata
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "038_sms_marketing_delivery"
down_revision: str | None = "037_saml_federation_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sms_delivery_logs",
        sa.Column("campaign_run_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_sms_delivery_logs_campaign_run_id",
        "sms_delivery_logs",
        "sms_marketing_campaign_runs",
        ["campaign_run_id"],
        ["id"],
    )
    op.create_index(
        "ix_sms_delivery_logs_campaign_run_id",
        "sms_delivery_logs",
        ["campaign_run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_sms_delivery_logs_campaign_run_id", table_name="sms_delivery_logs")
    op.drop_constraint(
        "fk_sms_delivery_logs_campaign_run_id",
        "sms_delivery_logs",
        type_="foreignkey",
    )
    op.drop_column("sms_delivery_logs", "campaign_run_id")
