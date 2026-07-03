"""Reflected compliance tables for worker retention enforcement."""

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()

retention_policies_table = Table(
    "retention_policies",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("name", String(255), nullable=False),
    Column("scope", String(50), nullable=False),
    Column("retention_days", Integer, nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("description", Text),
    Column("deleted_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

retention_enforcement_runs_table = Table(
    "retention_enforcement_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("policy_id", UUID(as_uuid=True)),
    Column("scope", String(50)),
    Column("trigger_source", String(20), nullable=False),
    Column("status", String(20), nullable=False),
    Column("items_scanned", Integer, nullable=False),
    Column("items_enforced", Integer, nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True), nullable=False),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

documents_table = Table(
    "documents",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("created_at", DateTime(timezone=True)),
    Column("deleted_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

communications_table = Table(
    "communications",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("case_id", UUID(as_uuid=True), nullable=False),
    Column("created_at", DateTime(timezone=True)),
    Column("deleted_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

cases_table = Table(
    "cases",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
)

clients_table = Table(
    "clients",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("created_at", DateTime(timezone=True)),
    Column("deleted_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)
