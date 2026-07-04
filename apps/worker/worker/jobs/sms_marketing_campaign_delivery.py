"""Marketing SMS campaign delivery worker job."""

import uuid

import structlog

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.registry import register_job
from worker.sms_marketing_delivery import (
    STATUS_COMPLETED,
    deliver_sms_marketing_campaign_run,
)

logger = structlog.get_logger(__name__)


@register_job
class SmsMarketingCampaignDeliveryJob(BaseJob):
    job_type = JobType.SMS_MARKETING_CAMPAIGN_DELIVERY

    def run(self, context: JobContext) -> JobResult:
        campaign_run_id = uuid.UUID(str(context.payload["campaign_run_id"]))

        with session_scope() as session:
            result = deliver_sms_marketing_campaign_run(
                session,
                campaign_run_id=campaign_run_id,
            )

        if result.status != STATUS_COMPLETED:
            message = result.error_message or "Marketing SMS campaign delivery failed"
            logger.warning(
                "sms_marketing_campaign_delivery_failed",
                job_id=context.job_id,
                campaign_run_id=str(campaign_run_id),
                status=result.status,
                error=result.error_message,
            )
            return JobResult(status=JobStatus.FAILED, message=message)

        message = (
            f"Delivered {result.messages_sent} marketing SMS message(s); "
            f"{result.messages_failed} failed"
        )
        logger.info(
            "sms_marketing_campaign_delivery_completed",
            job_id=context.job_id,
            campaign_run_id=str(campaign_run_id),
            messages_sent=result.messages_sent,
            messages_failed=result.messages_failed,
        )
        return JobResult(status=JobStatus.COMPLETED, message=message)
