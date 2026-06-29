"""Reflected documents table for worker DB access."""

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()

documents_table = Table(
    "documents",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("storage_key", String(500), nullable=False),
    Column("mime_type", String(100)),
    Column("version_number", Integer, nullable=False),
    Column("processing_status", String(20), nullable=False),
    Column("ocr_text", Text),
    Column("ocr_error", Text),
    Column("ocr_processed_at", DateTime(timezone=True)),
    Column("ocr_version_number", Integer),
    Column("deleted_at", DateTime(timezone=True)),
    Column("is_duplicate", Boolean),
)
