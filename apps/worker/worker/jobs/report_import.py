"""Report import job placeholder — bulk credit report ingestion (Sprint 2+)."""

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.registry import register_job

logger = structlog.get_logger(__name__)

PLACEHOLDER_MESSAGE = (
    "Report import job registered; implementation deferred to Sprint 2+"
)


@register_job
class ReportImportJob(BaseJob):
    job_type = JobType.REPORT_IMPORT

    def run(self, context: JobContext) -> JobResult:
        logger.info(
            "report_import_job_placeholder",
            job_id=context.job_id,
            payload_keys=list(context.payload),
        )
        return JobResult(status=JobStatus.COMPLETED, message=PLACEHOLDER_MESSAGE)
