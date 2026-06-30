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


@dataclass(frozen=True, slots=True)
class DocumentTimelineContext:
    id: UUID
    organization_id: UUID
    case_id: UUID
    account_id: UUID | None
    title: str
    file_name: str


def get_document_timeline_context(
    session: Session,
    document_id: UUID,
) -> DocumentTimelineContext | None:
    row = session.execute(
        select(
            documents_table.c.id,
            documents_table.c.organization_id,
            documents_table.c.case_id,
            documents_table.c.account_id,
            documents_table.c.title,
            documents_table.c.file_name,
        ).where(documents_table.c.id == document_id)
    ).one_or_none()
    if row is None:
        return None
    return DocumentTimelineContext(
        id=row.id,
        organization_id=row.organization_id,
        case_id=row.case_id,
        account_id=row.account_id,
        title=row.title,
        file_name=row.file_name,
    )


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


@dataclass(frozen=True, slots=True)
class ClassificationDocumentRecord:
    id: UUID
    ocr_text: str | None
    file_name: str
    title: str
    mime_type: str | None
    deleted_at: datetime | None


def get_document_for_classification(
    session: Session,
    document_id: UUID,
) -> ClassificationDocumentRecord | None:
    row = session.execute(
        select(
            documents_table.c.id,
            documents_table.c.ocr_text,
            documents_table.c.file_name,
            documents_table.c.title,
            documents_table.c.mime_type,
            documents_table.c.deleted_at,
        ).where(documents_table.c.id == document_id)
    ).one_or_none()
    if row is None:
        return None
    return ClassificationDocumentRecord(
        id=row.id,
        ocr_text=row.ocr_text,
        file_name=row.file_name,
        title=row.title,
        mime_type=row.mime_type,
        deleted_at=row.deleted_at,
    )


def save_classification(
    session: Session,
    document_id: UUID,
    *,
    document_type: str,
    confidence_score: float,
    classification_method: str,
) -> None:
    session.execute(
        update(documents_table)
        .where(documents_table.c.id == document_id)
        .values(
            document_type=document_type,
            confidence_score=confidence_score,
            classification_method=classification_method,
            classified_at=datetime.now(UTC),
            classified_by_id=None,
        )
    )
