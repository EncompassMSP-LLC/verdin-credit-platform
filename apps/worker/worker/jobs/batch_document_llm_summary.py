"""Batch document LLM summary worker job."""

import uuid

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.batch_document_llm_summary import (
    STATUS_COMPLETED,
    run_batch_document_llm_summary,
)
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.registry import register_job

logger = structlog.get_logger(__name__)


@register_job
class BatchDocumentLlmSummaryJob(BaseJob):
    job_type = JobType.BATCH_DOCUMENT_LLM_SUMMARY

    def run(self, context: JobContext) -> JobResult:
        run_id = uuid.UUID(str(context.payload["run_id"]))
        organization_id = uuid.UUID(str(context.payload["organization_id"]))
        document_ids = list(context.payload.get("document_ids") or [])
        performed_by_raw = context.payload.get("performed_by_user_id")
        performed_by_user_id = (
            uuid.UUID(str(performed_by_raw)) if performed_by_raw else None
        )

        with session_scope() as session:
            result = run_batch_document_llm_summary(
                session,
                run_id=run_id,
                organization_id=organization_id,
                document_ids=document_ids,
                performed_by_user_id=performed_by_user_id,
            )

        if result.status != STATUS_COMPLETED:
            return JobResult(
                status=JobStatus.FAILED,
                message=result.error_message or "Batch document LLM summary failed",
            )

        message = (
            f"Batch summarized {result.documents_succeeded} document(s); "
            f"{result.documents_failed} failed"
        )
        logger.info(
            "batch_document_llm_summary_job_completed",
            job_id=context.job_id,
            run_id=str(run_id),
            documents_succeeded=result.documents_succeeded,
            documents_failed=result.documents_failed,
        )
        return JobResult(status=JobStatus.COMPLETED, message=message)
