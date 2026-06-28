"""OCR job placeholder — document text extraction (Sprint 2+)."""

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.registry import register_job

logger = structlog.get_logger(__name__)

PLACEHOLDER_MESSAGE = "OCR job registered; implementation deferred to Sprint 2+"


@register_job
class OcrJob(BaseJob):
    job_type = JobType.OCR

    def run(self, context: JobContext) -> JobResult:
        logger.info(
            "ocr_job_placeholder",
            job_id=context.job_id,
            payload_keys=list(context.payload),
        )
        return JobResult(status=JobStatus.COMPLETED, message=PLACEHOLDER_MESSAGE)
