"""Reflected metadata and resolution tables for worker DB access."""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

document_metadata_table = Table(
    "document_metadata",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("document_id", UUID(as_uuid=True), nullable=False),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("consumer_name", String(255)),
    Column("bureau", String(50)),
    Column("creditor", String(255)),
    Column("collection_agency", String(255)),
    Column("account_number_masked", String(50)),
    Column("report_date", Date),
    Column("open_date", Date),
    Column("balance", Numeric(12, 2)),
    Column("payment_status", String(50)),
    Column("addresses", JSONB),
    Column("phone_numbers", JSONB),
    Column("ssn_masked", String(20)),
    Column("confidence_score", Numeric(5, 4)),
    Column("extraction_method", String(20)),
    Column("metadata_status", String(20)),
    Column("extracted_at", DateTime(timezone=True)),
    Column("extraction_error", Text),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

document_entity_resolutions_table = Table(
    "document_entity_resolutions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("document_id", UUID(as_uuid=True), nullable=False),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("entity_type", String(20), nullable=False),
    Column("matched_entity_id", UUID(as_uuid=True)),
    Column("confidence_score", Numeric(5, 4), nullable=False),
    Column("resolution_status", String(20), nullable=False),
    Column("resolution_method", String(20), nullable=False),
    Column("reasoning", Text),
    Column("candidate_entity_ids", JSONB),
    Column("reviewed_at", DateTime(timezone=True)),
    Column("reviewed_by_id", UUID(as_uuid=True)),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

cases_table = Table(
    "cases",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True)),
    Column("client_name", String(255)),
    Column("case_number", String(50)),
    Column("deleted_at", DateTime(timezone=True)),
)

accounts_table = Table(
    "accounts",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("case_id", UUID(as_uuid=True)),
    Column("organization_id", UUID(as_uuid=True)),
    Column("creditor_name", String(255)),
    Column("account_number_masked", String(50)),
    Column("bureau", String(50)),
    Column("balance", Numeric(12, 2)),
    Column("deleted_at", DateTime(timezone=True)),
)
