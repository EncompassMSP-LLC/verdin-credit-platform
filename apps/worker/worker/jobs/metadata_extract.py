"""Document metadata extraction worker job."""

from uuid import UUID

import structlog
from verdin_document_metadata import ExtractionContext, extract_metadata
from verdin_report_parsers.metadata_bridge import bridge_parsed_report_dict

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.metadata_documents import get_document_for_metadata, upsert_metadata
from worker.parsed_reports import get_parsed_credit_report
from worker.timeline import append_timeline_event
from worker.queue import enqueue_job
from worker.registry import register_job

logger = structlog.get_logger(__name__)


def _parse_document_id(payload: dict) -> UUID:
    raw = payload.get("document_id")
    if not raw:
        raise ValueError("document_id is required")
    return UUID(str(raw))


@register_job
class DocumentMetadataExtractJob(BaseJob):
    job_type = JobType.DOCUMENT_METADATA_EXTRACT

    def run(self, context: JobContext) -> JobResult:
        try:
            document_id = _parse_document_id(context.payload)
        except ValueError as exc:
            return JobResult(status=JobStatus.FAILED, message=str(exc))

        with session_scope() as session:
            document = get_document_for_metadata(session, document_id)
            if document is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")
            if document.deleted_at is not None:
                return JobResult(
                    status=JobStatus.CANCELLED, message="Document was deleted"
                )
            if not document.ocr_text:
                return JobResult(
                    status=JobStatus.FAILED,
                    message="OCR text is required before metadata extraction",
                )

            parsed_record = get_parsed_credit_report(session, document_id)
            if parsed_record is not None:
                bridged = bridge_parsed_report_dict(parsed_record.parsed_report)
                upsert_metadata(
                    session,
                    document,
                    consumer_name=bridged.consumer_name,
                    bureau=bridged.bureau,
                    creditor=bridged.creditor,
                    collection_agency=bridged.collection_agency,
                    account_number_masked=bridged.account_number_masked,
                    report_date=bridged.report_date,
                    open_date=bridged.open_date,
                    balance=bridged.balance,
                    payment_status=bridged.payment_status,
                    addresses=bridged.addresses,
                    phone_numbers=bridged.phone_numbers,
                    ssn_masked=bridged.ssn_masked,
                    confidence_score=bridged.confidence_score,
                    extraction_method=bridged.extraction_method,
                )
                confidence_score = bridged.confidence_score
            else:
                extraction_context = ExtractionContext(
                    ocr_text=document.ocr_text,
                    file_name=document.file_name,
                    title=document.title,
                    document_type=document.document_type,
                )
                extracted = extract_metadata(extraction_context)
                upsert_metadata(
                    session,
                    document,
                    consumer_name=extracted.consumer_name,
                    bureau=extracted.bureau,
                    creditor=extracted.creditor,
                    collection_agency=extracted.collection_agency,
                    account_number_masked=extracted.account_number_masked,
                    report_date=extracted.report_date,
                    open_date=extracted.open_date,
                    balance=extracted.balance,
                    payment_status=extracted.payment_status,
                    addresses=extracted.addresses,
                    phone_numbers=extracted.phone_numbers,
                    ssn_masked=extracted.ssn_masked,
                    confidence_score=extracted.confidence_score,
                )
                confidence_score = extracted.confidence_score
            append_timeline_event(
                session,
                organization_id=document.organization_id,
                event_type="METADATA_EXTRACTED",
                event_category="document",
                title="Metadata extracted",
                description=f"Metadata extracted from '{document.title}'.",
                source_module="worker",
                case_id=document.case_id,
                account_id=document.account_id,
                document_id=document.id,
                metadata={"confidence_score": confidence_score},
            )

        enqueue_job(JobType.DOCUMENT_ENTITY_RESOLVE, {"document_id": str(document_id)})

        logger.info(
            "document_metadata_extracted",
            job_id=context.job_id,
            document_id=str(document_id),
            confidence=confidence_score,
        )
        return JobResult(
            status=JobStatus.COMPLETED,
            message="Metadata extracted",
            data={"confidence_score": confidence_score},
        )
