"""Reflected batch summary tables for the worker."""

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

batch_document_summary_runs_table = Table(
    "batch_document_summary_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("trigger_source", String(20), nullable=False),
    Column("status", String(20), nullable=False),
    Column("document_ids", JSONB, nullable=False),
    Column("documents_queued", Integer, nullable=False),
    Column("documents_succeeded", Integer, nullable=False),
    Column("documents_failed", Integer, nullable=False),
    Column("performed_by_user_id", UUID(as_uuid=True)),
    Column("started_at", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

documents_table = Table(
    "documents",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("case_id", UUID(as_uuid=True)),
    Column("account_id", UUID(as_uuid=True)),
    Column("title", String(255), nullable=False),
    Column("file_name", String(255), nullable=False),
    Column("document_type", String(50)),
    Column("processing_status", String(50)),
    Column("ocr_text", Text),
    Column("deleted_at", DateTime(timezone=True)),
)
