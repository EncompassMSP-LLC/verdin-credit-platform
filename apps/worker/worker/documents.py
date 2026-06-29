"""Document row access for OCR worker jobs."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from worker.documents_table import documents_table


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    id: UUID
    storage_key: str
    mime_type: str | None
    version_number: int
    processing_status: str
    deleted_at: datetime | None


def get_document(session: Session, document_id: UUID) -> DocumentRecord | None:
    row = session.execute(
        select(
            documents_table.c.id,
            documents_table.c.storage_key,
            documents_table.c.mime_type,
            documents_table.c.version_number,
            documents_table.c.processing_status,
            documents_table.c.deleted_at,
        ).where(documents_table.c.id == document_id)
    ).one_or_none()
    if row is None:
        return None
    return DocumentRecord(
        id=row.id,
        storage_key=row.storage_key,
        mime_type=row.mime_type,
        version_number=row.version_number,
        processing_status=row.processing_status,
        deleted_at=row.deleted_at,
    )


def mark_processing(session: Session, document_id: UUID) -> None:
    session.execute(
        update(documents_table)
        .where(documents_table.c.id == document_id)
        .values(processing_status="processing")
    )


def save_ocr_success(
    session: Session,
    document_id: UUID,
    *,
    text: str,
    version_number: int,
) -> None:
    session.execute(
        update(documents_table)
        .where(documents_table.c.id == document_id)
        .values(
            processing_status="completed",
            ocr_text=text,
            ocr_error=None,
            ocr_processed_at=datetime.now(UTC),
            ocr_version_number=version_number,
        )
    )


def save_ocr_failure(session: Session, document_id: UUID, error: str) -> None:
    session.execute(
        update(documents_table)
        .where(documents_table.c.id == document_id)
        .values(
            processing_status="failed",
            ocr_error=error[:2000],
            ocr_processed_at=datetime.now(UTC),
        )
    )
