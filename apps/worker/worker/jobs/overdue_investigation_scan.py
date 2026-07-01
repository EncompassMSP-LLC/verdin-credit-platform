"""Scheduled scan for overdue CRA investigations."""

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.overdue_investigations import scan_and_escalate_overdue_investigations
from worker.registry import register_job

logger = structlog.get_logger(__name__)


@register_job
class OverdueInvestigationScanJob(BaseJob):
    job_type = JobType.OVERDUE_INVESTIGATION_SCAN

    def run(self, context: JobContext) -> JobResult:
        with session_scope() as session:
            result = scan_and_escalate_overdue_investigations(session)

        message = (
            f"Scanned {result.scanned} account(s); "
            f"escalated {result.escalated}; "
            f"created {result.tasks_created} task(s)"
        )
        logger.info(
            "overdue_investigation_scan_completed",
            job_id=context.job_id,
            scanned=result.scanned,
            escalated=result.escalated,
            tasks_created=result.tasks_created,
        )
        return JobResult(status=JobStatus.COMPLETED, message=message)
