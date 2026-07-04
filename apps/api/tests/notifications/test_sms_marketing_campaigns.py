"""SMS marketing campaign integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.core.sms_delivery import get_sms_delivery_settings
from api.modules.auth.models import User


@pytest.fixture
def sms_marketing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "true")
    monkeypatch.setenv("ENABLE_SMS_MARKETING_CAMPAIGNS", "true")
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
async def case_manager_with_phone(
    db_session: AsyncSession,
    case_manager_user: User,
) -> User:
    case_manager_user.phone_number = "+15555550123"
    db_session.add(case_manager_user)
    await db_session.commit()
    await db_session.refresh(case_manager_user)
    return case_manager_user


def test_sms_marketing_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/notifications/sms-campaigns/status", headers=manager_headers)
    assert response.status_code == 404


def test_sms_marketing_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sms_marketing_env: None,
) -> None:
    response = api_client.get("/api/v1/notifications/sms-campaigns/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["sms_delivery_ready"] is True
    assert payload["blockers"] == []


def test_enqueue_sms_marketing_campaign(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_marketing_env: None,
    case_manager_with_phone: User,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms-campaigns/run",
        headers=admin_headers,
        json={
            "campaign_name": "July Promo",
            "message_body": "Your credit review update is ready.",
            "recipient_user_ids": [str(case_manager_with_phone.id)],
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["run"]["campaign_name"] == "July Promo"
    assert payload["run"]["recipients_queued"] == 1
    assert payload["run"]["messages_sent"] == 1
    assert payload["run"]["messages_failed"] == 0

    listing = api_client.get(
        "/api/v1/notifications/sms-campaigns/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] == 1


def test_enqueue_sms_marketing_campaign_missing_phone_counts_failed(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_marketing_env: None,
    case_manager_user: User,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms-campaigns/run",
        headers=admin_headers,
        json={
            "campaign_name": "No Phone",
            "message_body": "Hello",
            "recipient_user_ids": [str(case_manager_user.id)],
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["run"]["messages_sent"] == 0
    assert payload["run"]["messages_failed"] == 1


def test_enqueue_sms_marketing_campaign_unknown_recipient(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_marketing_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms-campaigns/run",
        headers=admin_headers,
        json={
            "campaign_name": "Unknown",
            "message_body": "Hello",
            "recipient_user_ids": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["run"]["messages_failed"] == 1


def test_enqueue_sms_marketing_campaign_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    sms_marketing_env: None,
    case_manager_user: User,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms-campaigns/run",
        headers=readonly_headers,
        json={
            "campaign_name": "Denied",
            "message_body": "Hello",
            "recipient_user_ids": [str(case_manager_user.id)],
        },
    )
    assert response.status_code == 403
