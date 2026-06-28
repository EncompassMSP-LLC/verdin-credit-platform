"""Monthly review job placeholder — scheduled portfolio review (Sprint 2+)."""

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.registry import register_job

logger = structlog.get_logger(__name__)

PLACEHOLDER_MESSAGE = (
    "Monthly review job registered; implementation deferred to Sprint 2+"
)


@register_job
class MonthlyReviewJob(BaseJob):
    job_type = JobType.MONTHLY_REVIEW

    def run(self, context: JobContext) -> JobResult:
        logger.info(
            "monthly_review_job_placeholder",
            job_id=context.job_id,
            payload_keys=list(context.payload),
        )
        return JobResult(status=JobStatus.COMPLETED, message=PLACEHOLDER_MESSAGE)
