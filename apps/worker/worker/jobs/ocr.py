"""OCR job — async document text extraction."""

from uuid import UUID

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.documents import (
    DocumentRecord,
    get_document,
    mark_processing,
    save_ocr_failure,
    save_ocr_success,
)
from worker.queue import enqueue_job
from worker.ocr.extractor import (
    OcrExtractionError,
    UnsupportedOcrFormatError,
    extract_text,
)
from worker.registry import register_job
from worker.storage import get_document_storage

logger = structlog.get_logger(__name__)


def _parse_document_id(payload: dict) -> UUID:
    raw = payload.get("document_id")
    if not raw:
        raise ValueError("document_id is required")
    return UUID(str(raw))


def _process_document(document: DocumentRecord) -> JobResult:
    if document.deleted_at is not None:
        return JobResult(status=JobStatus.CANCELLED, message="Document was deleted")

    storage = get_document_storage()
    try:
        data = storage.get_object(document.storage_key)
    except Exception as exc:
        return JobResult(status=JobStatus.FAILED, message=f"Storage read failed: {exc}")

    try:
        text = extract_text(data, document.mime_type)
    except (OcrExtractionError, UnsupportedOcrFormatError) as exc:
        return JobResult(status=JobStatus.FAILED, message=str(exc))

    return JobResult(
        status=JobStatus.COMPLETED,
        message="OCR completed",
        data={"text": text, "version_number": document.version_number},
    )


@register_job
class OcrJob(BaseJob):
    job_type = JobType.OCR

    def run(self, context: JobContext) -> JobResult:
        try:
            document_id = _parse_document_id(context.payload)
        except ValueError as exc:
            logger.warning(
                "ocr_job_invalid_payload", job_id=context.job_id, error=str(exc)
            )
            return JobResult(status=JobStatus.FAILED, message=str(exc))

        with session_scope() as session:
            document = get_document(session, document_id)
            if document is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")

            mark_processing(session, document_id)

        result = _process_document(document)

        with session_scope() as session:
            if result.status == JobStatus.COMPLETED and result.data is not None:
                save_ocr_success(
                    session,
                    document_id,
                    text=result.data["text"],
                    version_number=result.data["version_number"],
                )
                enqueue_job(
                    JobType.DOCUMENT_CLASSIFY, {"document_id": str(document_id)}
                )
            elif result.status == JobStatus.FAILED:
                save_ocr_failure(session, document_id, result.message)
            elif result.status == JobStatus.CANCELLED:
                save_ocr_failure(session, document_id, result.message)

        logger.info(
            "ocr_job_finished",
            job_id=context.job_id,
            document_id=str(document_id),
            status=result.status.value,
            message=result.message,
        )
        return result
