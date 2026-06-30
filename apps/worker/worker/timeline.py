"""Worker timeline event persistence."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from worker.metadata_tables import metadata as worker_metadata
from sqlalchemy import Column, DateTime, String, Table, Text, insert
from sqlalchemy.dialects.postgresql import JSONB, UUID

timeline_events_table = Table(
    "timeline_events",
    worker_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("case_id", UUID(as_uuid=True)),
    Column("account_id", UUID(as_uuid=True)),
    Column("document_id", UUID(as_uuid=True)),
    Column("event_type", String(100), nullable=False),
    Column("event_category", String(50), nullable=False),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column("metadata", JSONB, nullable=False),
    Column("performed_by", UUID(as_uuid=True)),
    Column("source_module", String(50), nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def append_timeline_event(
    session: Session,
    *,
    organization_id: uuid.UUID,
    event_type: str,
    event_category: str,
    title: str,
    description: str | None,
    source_module: str,
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
    performed_by: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    now = datetime.now(UTC)
    session.execute(
        insert(timeline_events_table).values(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            document_id=document_id,
            event_type=event_type,
            event_category=event_category,
            title=title,
            description=description,
            metadata=metadata or {},
            performed_by=performed_by,
            source_module=source_module,
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
    )
