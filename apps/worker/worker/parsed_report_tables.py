"""Reflected document_parsed_credit_reports table for worker DB access."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    MetaData,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

document_parsed_credit_reports_table = Table(
    "document_parsed_credit_reports",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("document_id", UUID(as_uuid=True), nullable=False),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("schema_version", String(20), nullable=False),
    Column("bureau", String(50), nullable=False),
    Column("parser_name", String(50), nullable=False),
    Column("parser_confidence", Numeric(5, 4), nullable=False),
    Column("parsed_report", JSONB, nullable=False),
    Column("is_partial", Boolean, nullable=False),
    Column("warnings", JSONB, nullable=False),
    Column("parsed_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)
