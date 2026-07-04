"""Marketing SMS campaign delivery integration tests."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.core.sms_delivery import SmsSendResult, get_sms_delivery_settings
from api.modules.auth.models import User
from api.modules.notifications.sms_campaign_delivery_processor import (
    deliver_sms_marketing_campaign_run,
)
from api.modules.notifications.sms_campaign_models import SmsMarketingCampaignStatus
from api.modules.notifications.sms_campaign_processor import enqueue_sms_marketing_campaign


@pytest.fixture
def sms_marketing_delivery_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_CAMPAIGNS", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_DELIVERY", "true")
    monkeypatch.setenv("SMS_PROVIDER", "twilio")
    monkeypatch.setenv("SMS_FROM_NUMBER", "+15555550100")
    monkeypatch.setenv("SMS_TWILIO_ACCOUNT_SID", "ACtest123")
    monkeypatch.setenv("SMS_TWILIO_AUTH_TOKEN", "test-token")
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()


@pytest.fixture
def mock_send_sms(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(
        return_value=SmsSendResult(success=True, provider_message_id="SMtest123"),
    )
    monkeypatch.setattr(
        "api.modules.notifications.sms_campaign_delivery_processor.send_sms_message",
        mock,
    )
    return mock


@pytest.mark.asyncio
async def test_enqueue_campaign_with_delivery_creates_pending_run(
    db_session: AsyncSession,
    admin_user: User,
    case_manager_with_phone: User,
    sms_marketing_delivery_env: None,
) -> None:
    assert admin_user.organization_id is not None
    with patch("api.modules.notifications.sms_campaign_processor.enqueue_job") as mock_enqueue:
        summary = await enqueue_sms_marketing_campaign(
            session=db_session,
            organization_id=admin_user.organization_id,
            campaign_name="Worker Queue",
            message_body="Hello from worker",
            recipient_user_ids=[case_manager_with_phone.id],
            performed_by_user_id=admin_user.id,
        )
        await db_session.commit()

    assert summary.run.status == SmsMarketingCampaignStatus.PENDING
    assert summary.run.messages_sent == 0
    assert summary.run.recipients_queued == 1
    mock_enqueue.assert_called_once()
    assert mock_enqueue.call_args.args[0].value == "sms_marketing_campaign_delivery"


@pytest.mark.asyncio
async def test_deliver_campaign_run_sends_and_logs(
    db_session: AsyncSession,
    admin_user: User,
    case_manager_with_phone: User,
    sms_marketing_delivery_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    assert admin_user.organization_id is not None
    with patch("api.modules.notifications.sms_campaign_processor.enqueue_job"):
        summary = await enqueue_sms_marketing_campaign(
            session=db_session,
            organization_id=admin_user.organization_id,
            campaign_name="Deliver Me",
            message_body="Promo message",
            recipient_user_ids=[case_manager_with_phone.id],
            performed_by_user_id=admin_user.id,
        )
        await db_session.commit()

    delivery = await deliver_sms_marketing_campaign_run(
        session=db_session,
        campaign_run_id=summary.run.id,
    )
    await db_session.commit()

    assert delivery.status == SmsMarketingCampaignStatus.COMPLETED
    assert delivery.messages_sent == 1
    assert delivery.messages_failed == 0
    mock_send_sms.assert_awaited_once()


@pytest.mark.asyncio
async def test_deliver_campaign_run_counts_missing_phone_as_failed(
    db_session: AsyncSession,
    admin_user: User,
    case_manager_user: User,
    sms_marketing_delivery_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    assert admin_user.organization_id is not None
    with patch("api.modules.notifications.sms_campaign_processor.enqueue_job"):
        summary = await enqueue_sms_marketing_campaign(
            session=db_session,
            organization_id=admin_user.organization_id,
            campaign_name="No Phone",
            message_body="Hello",
            recipient_user_ids=[case_manager_user.id],
            performed_by_user_id=admin_user.id,
        )
        await db_session.commit()

    delivery = await deliver_sms_marketing_campaign_run(
        session=db_session,
        campaign_run_id=summary.run.id,
    )
    await db_session.commit()

    assert delivery.messages_sent == 0
    assert delivery.messages_failed == 1
    mock_send_sms.assert_not_awaited()
