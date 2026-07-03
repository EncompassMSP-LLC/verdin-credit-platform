"""Scheduled reporting materialized view refresh."""

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.registry import register_job
from worker.reporting_mv_refresh import STATUS_COMPLETED, run_reporting_mv_refresh

logger = structlog.get_logger(__name__)


@register_job
class ReportingMvRefreshJob(BaseJob):
    job_type = JobType.REPORTING_MV_REFRESH

    def run(self, context: JobContext) -> JobResult:
        with session_scope() as session:
            result = run_reporting_mv_refresh(session)

        if result.status != STATUS_COMPLETED:
            return JobResult(
                status=JobStatus.FAILED,
                message="Reporting materialized view refresh failed",
            )

        message = f"Refreshed {result.views_refreshed} materialized view(s)"
        logger.info(
            "reporting_mv_refresh_completed",
            job_id=context.job_id,
            views_refreshed=result.views_refreshed,
        )
        return JobResult(status=JobStatus.COMPLETED, message=message)
