"""Worker marketing SMS campaign delivery tests."""

from unittest.mock import patch
import uuid

from worker.constants import JobType
from worker.jobs import sms_marketing_campaign_delivery  # noqa: F401 — register job
from worker.jobs.sms_marketing_campaign_delivery import SmsMarketingCampaignDeliveryJob
from worker.registry import get_job
from worker.sms_marketing_delivery import SmsMarketingCampaignDeliveryResult


def test_sms_marketing_campaign_delivery_job_registered() -> None:
    job = get_job(JobType.SMS_MARKETING_CAMPAIGN_DELIVERY)
    assert isinstance(job, SmsMarketingCampaignDeliveryJob)


@patch("worker.jobs.sms_marketing_campaign_delivery.deliver_sms_marketing_campaign_run")
@patch("worker.jobs.sms_marketing_campaign_delivery.session_scope")
def test_sms_marketing_campaign_delivery_job_runs_delivery(
    mock_session_scope,
    mock_deliver,
) -> None:
    mock_session_scope.return_value.__enter__.return_value = object()
    mock_deliver.return_value = SmsMarketingCampaignDeliveryResult(
        messages_sent=2,
        messages_failed=0,
        status="completed",
    )

    job = SmsMarketingCampaignDeliveryJob()
    run_id = uuid.uuid4()
    result = job.run(
        type(
            "Ctx",
            (),
            {"job_id": "job-1", "payload": {"campaign_run_id": str(run_id)}},
        )()
    )

    assert result.status.value == "completed"
    mock_deliver.assert_called_once()
