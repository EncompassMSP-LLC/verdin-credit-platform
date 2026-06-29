"""Reflected documents table for worker DB access."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)
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
    Column("file_name", String(255), nullable=False),
    Column("title", String(255), nullable=False),
    Column("document_type", String(50)),
    Column("confidence_score", Numeric(5, 4)),
    Column("classification_method", String(20)),
    Column("classified_at", DateTime(timezone=True)),
    Column("classified_by_id", UUID(as_uuid=True)),
    Column("deleted_at", DateTime(timezone=True)),
    Column("is_duplicate", Boolean),
)
