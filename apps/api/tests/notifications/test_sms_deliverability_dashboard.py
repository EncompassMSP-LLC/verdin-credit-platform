"""SMS deliverability dashboard integration tests."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.sms_deliverability_dashboard import compute_delivery_success_rate
from api.core.sms_delivery import SmsSendResult, get_sms_delivery_settings
from api.modules.notifications.sms_campaign_delivery_processor import (
    deliver_sms_marketing_campaign_run,
)
from api.modules.notifications.sms_campaign_processor import enqueue_sms_marketing_campaign


@pytest.fixture
def sms_deliverability_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_CAMPAIGNS", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_DELIVERABILITY_DASHBOARD", "true")
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
def sms_marketing_delivery_only_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_CAMPAIGNS", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_DELIVERABILITY_DASHBOARD", "false")
    monkeypatch.setenv("SMS_PROVIDER", "twilio")
    monkeypatch.setenv("SMS_FROM_NUMBER", "+15555550100")
    monkeypatch.setenv("SMS_TWILIO_ACCOUNT_SID", "ACtest123")
    monkeypatch.setenv("SMS_TWILIO_AUTH_TOKEN", "test-token")
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()


def test_compute_delivery_success_rate() -> None:
    assert compute_delivery_success_rate(messages_sent=0, messages_failed=0) is None
    assert compute_delivery_success_rate(messages_sent=3, messages_failed=1) == 75.0


def test_deliverability_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_marketing_delivery_only_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/notifications/sms-campaigns/deliverability/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_deliverability_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_deliverability_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/notifications/sms-campaigns/deliverability/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["delivery_ready"] is True
    assert payload["blockers"] == []


def test_deliverability_summary_empty(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_deliverability_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/notifications/sms-campaigns/deliverability/summary",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total_campaign_runs"] == 0
    assert payload["delivery_success_rate"] is None
    assert payload["recent_campaign_outcomes"] == []


@pytest.mark.asyncio
async def test_deliverability_summary_after_campaign_delivery(
    api_client: TestClient,
    admin_headers: dict[str, str],
    db_session,
    admin_user,
    case_manager_with_phone,
    sms_deliverability_env: None,
) -> None:
    assert admin_user.organization_id is not None
    mock = AsyncMock(return_value=SmsSendResult(success=True, provider_message_id="SMtest123"))
    with patch(
        "api.modules.notifications.sms_campaign_delivery_processor.send_sms_message",
        mock,
    ):
        with patch("api.modules.notifications.sms_campaign_processor.enqueue_job"):
            summary = await enqueue_sms_marketing_campaign(
                session=db_session,
                organization_id=admin_user.organization_id,
                campaign_name="Dashboard Promo",
                message_body="Hello metrics",
                recipient_user_ids=[case_manager_with_phone.id],
                performed_by_user_id=admin_user.id,
            )
            await db_session.commit()
            await deliver_sms_marketing_campaign_run(
                session=db_session,
                campaign_run_id=summary.run.id,
            )
            await db_session.commit()

    response = api_client.get(
        "/api/v1/notifications/sms-campaigns/deliverability/summary",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total_campaign_runs"] == 1
    assert payload["completed_campaign_runs"] == 1
    assert payload["delivery_logs_sent"] == 1
    assert payload["delivery_success_rate"] == 100.0
    assert len(payload["recent_campaign_outcomes"]) == 1
    assert payload["recent_campaign_outcomes"][0]["campaign_name"] == "Dashboard Promo"
