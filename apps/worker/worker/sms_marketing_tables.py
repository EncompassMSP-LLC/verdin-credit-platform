"""Reflected SMS marketing tables for the worker."""

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

sms_marketing_campaign_runs_table = Table(
    "sms_marketing_campaign_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("campaign_name", String(120), nullable=False),
    Column("message_body", Text, nullable=False),
    Column("recipient_user_ids", JSONB, nullable=False),
    Column("trigger_source", String(20), nullable=False),
    Column("status", String(20), nullable=False),
    Column("recipients_queued", Integer, nullable=False),
    Column("messages_sent", Integer, nullable=False),
    Column("messages_failed", Integer, nullable=False),
    Column("performed_by_user_id", UUID(as_uuid=True)),
    Column("started_at", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

users_table = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True)),
    Column("phone_number", String(50)),
)

sms_delivery_logs_table = Table(
    "sms_delivery_logs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("notification_id", UUID(as_uuid=True)),
    Column("recipient_user_id", UUID(as_uuid=True)),
    Column("recipient_phone", String(50), nullable=False),
    Column("body", Text, nullable=False),
    Column("provider", String(50), nullable=False),
    Column("status", String(20), nullable=False),
    Column("provider_message_id", String(255)),
    Column("error_message", Text),
    Column("sent_by_user_id", UUID(as_uuid=True)),
    Column("campaign_run_id", UUID(as_uuid=True)),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)
