"""Parse classified credit reports into canonical ParsedCreditReport records."""

from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy import select
from verdin_report_parsers import parse_credit_report
from verdin_report_parsers.base import ParsedDocument

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.documents import (
    get_document_for_classification,
    get_document_timeline_context,
)
from worker.documents_table import documents_table
from worker.parsed_reports import upsert_parsed_credit_report
from worker.queue import enqueue_job
from worker.registry import register_job
from worker.tasks import create_parsed_report_review_task
from worker.timeline import append_timeline_event

logger = structlog.get_logger(__name__)


def _parse_document_id(payload: dict) -> UUID:
    raw = payload.get("document_id")
    if not raw:
        raise ValueError("document_id is required")
    return UUID(str(raw))


@register_job
class DocumentCreditReportParseJob(BaseJob):
    job_type = JobType.DOCUMENT_CREDIT_REPORT_PARSE

    def run(self, context: JobContext) -> JobResult:
        try:
            document_id = _parse_document_id(context.payload)
        except ValueError as exc:
            return JobResult(status=JobStatus.FAILED, message=str(exc))

        with session_scope() as session:
            document = get_document_for_classification(session, document_id)
            if document is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")
            if document.deleted_at is not None:
                return JobResult(
                    status=JobStatus.CANCELLED, message="Document was deleted"
                )
            if not document.ocr_text:
                return JobResult(
                    status=JobStatus.FAILED,
                    message="OCR text is required before credit report parsing",
                )

            classification_row = session.execute(
                select(
                    documents_table.c.confidence_score,
                    documents_table.c.organization_id,
                    documents_table.c.document_type,
                ).where(documents_table.c.id == document_id)
            ).one_or_none()
            if classification_row is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")

            classification_confidence = (
                float(classification_row.confidence_score)
                if classification_row.confidence_score is not None
                else None
            )
            parsed_document = ParsedDocument(
                ocr_text=document.ocr_text,
                file_name=document.file_name,
                title=document.title,
                mime_type=document.mime_type,
                document_type=classification_row.document_type,
                classification_confidence=classification_confidence,
                document_id=str(document_id),
            )
            parsed = parse_credit_report(parsed_document)

            parser_confidence = 0.0
            if parsed.metadata and parsed.metadata.field_confidence:
                layout_confidence = parsed.metadata.field_confidence.get(
                    "parser.layout_confidence"
                )
                if layout_confidence is not None:
                    parser_confidence = float(layout_confidence)

            metadata = parsed.metadata
            parsed_report_payload = parsed.as_dict()
            parsed_report_id = upsert_parsed_credit_report(
                session,
                document_id=document_id,
                organization_id=classification_row.organization_id,
                schema_version=parsed.schema_version,
                bureau=parsed.bureau.value,
                parser_name=metadata.parser_name if metadata else "unknown",
                parser_confidence=parser_confidence,
                parsed_report=parsed_report_payload,
                is_partial=metadata.is_partial if metadata else True,
                warnings=metadata.warnings if metadata else (),
            )

            timeline_context = get_document_timeline_context(session, document_id)
            if timeline_context is not None:
                review_task_id = create_parsed_report_review_task(
                    session,
                    organization_id=timeline_context.organization_id,
                    case_id=timeline_context.case_id,
                    account_id=timeline_context.account_id,
                    document_id=timeline_context.id,
                    document_title=timeline_context.title,
                    parsed_report_id=parsed_report_id,
                    parsed_report=parsed_report_payload,
                )
                append_timeline_event(
                    session,
                    organization_id=timeline_context.organization_id,
                    event_type="CREDIT_REPORT_PARSED",
                    event_category="document",
                    title="Credit report parsed",
                    description=(
                        f"Structured credit report extracted via "
                        f"{metadata.parser_name if metadata else 'parser'}"
                    ),
                    source_module="worker",
                    case_id=timeline_context.case_id,
                    account_id=timeline_context.account_id,
                    document_id=timeline_context.id,
                    metadata={
                        "bureau": parsed.bureau.value,
                        "parser_name": metadata.parser_name if metadata else None,
                        "is_partial": metadata.is_partial if metadata else True,
                        "review_task_id": str(review_task_id)
                        if review_task_id
                        else None,
                    },
                )

        enqueue_job(
            JobType.DOCUMENT_METADATA_EXTRACT, {"document_id": str(document_id)}
        )

        logger.info(
            "credit_report_parsed",
            job_id=context.job_id,
            document_id=str(document_id),
            bureau=parsed.bureau.value,
            parser_name=metadata.parser_name if metadata else None,
        )
        return JobResult(
            status=JobStatus.COMPLETED,
            message="Credit report parsed",
            data={
                "bureau": parsed.bureau.value,
                "parser_name": metadata.parser_name if metadata else None,
                "is_partial": metadata.is_partial if metadata else True,
            },
        )
