"""Scheduled retention policy enforcement scan."""

import uuid

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.registry import register_job
from worker.retention_enforcement import run_retention_enforcement_scan

logger = structlog.get_logger(__name__)


@register_job
class RetentionEnforcementScanJob(BaseJob):
    job_type = JobType.RETENTION_ENFORCEMENT_SCAN

    def run(self, context: JobContext) -> JobResult:
        organization_id_raw = context.payload.get("organization_id")
        organization_id = (
            uuid.UUID(organization_id_raw) if organization_id_raw else None
        )

        with session_scope() as session:
            result = run_retention_enforcement_scan(
                session, organization_id=organization_id
            )

        message = (
            f"Processed {result.organizations_processed} organization(s); "
            f"applied {result.policies_processed} policy run(s); "
            f"enforced {result.items_enforced} item(s)"
        )
        logger.info(
            "retention_enforcement_scan_completed",
            job_id=context.job_id,
            organizations_processed=result.organizations_processed,
            policies_processed=result.policies_processed,
            items_enforced=result.items_enforced,
        )
        return JobResult(status=JobStatus.COMPLETED, message=message)
