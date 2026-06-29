"""Document classification worker job."""

import sys
from pathlib import Path
from uuid import UUID

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.documents import get_document_for_classification, save_classification
from worker.queue import enqueue_job
from worker.registry import register_job

logger = structlog.get_logger(__name__)


def _load_classifier():
    apps_dir = Path(__file__).resolve().parents[3]
    api_root = apps_dir / "api"
    if str(api_root) not in sys.path:
        sys.path.insert(0, str(api_root))
    from api.modules.documents.classification import (
        ClassificationContext,
        classify_document,
    )

    return ClassificationContext, classify_document


def _parse_document_id(payload: dict) -> UUID:
    raw = payload.get("document_id")
    if not raw:
        raise ValueError("document_id is required")
    return UUID(str(raw))


@register_job
class DocumentClassifyJob(BaseJob):
    job_type = JobType.DOCUMENT_CLASSIFY

    def run(self, context: JobContext) -> JobResult:
        try:
            document_id = _parse_document_id(context.payload)
        except ValueError as exc:
            return JobResult(status=JobStatus.FAILED, message=str(exc))

        try:
            context_cls, classify_fn = _load_classifier()
        except ImportError as exc:
            logger.exception("classification_module_unavailable", error=str(exc))
            return JobResult(
                status=JobStatus.FAILED,
                message="Classification module unavailable in worker runtime",
            )

        with session_scope() as session:
            document = get_document_for_classification(session, document_id)
            if document is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")
            if document.deleted_at is not None:
                return JobResult(
                    status=JobStatus.CANCELLED, message="Document was deleted"
                )

            classification_context = context_cls(
                ocr_text=document.ocr_text,
                file_name=document.file_name,
                title=document.title,
                mime_type=document.mime_type,
            )
            result = classify_fn(classification_context)
            save_classification(
                session,
                document_id,
                document_type=result.document_type.value,
                confidence_score=result.confidence_score,
                classification_method=result.classification_method.value,
            )

        enqueue_job(
            JobType.DOCUMENT_METADATA_EXTRACT, {"document_id": str(document_id)}
        )

        logger.info(
            "document_classified",
            job_id=context.job_id,
            document_id=str(document_id),
            document_type=result.document_type.value,
            confidence=result.confidence_score,
        )
        return JobResult(
            status=JobStatus.COMPLETED,
            message="Document classified",
            data={
                "document_type": result.document_type.value,
                "confidence_score": result.confidence_score,
            },
        )
