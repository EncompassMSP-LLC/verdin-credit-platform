"""Public client enrollment tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.client_enrollment import get_client_enrollment_settings
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def enrollment_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_ENROLLMENT", "true")
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    monkeypatch.setenv("ENROLLMENT_ORGANIZATION_SLUG", "verdin-demo")
    monkeypatch.setenv("ENROLLMENT_SKIP_PAYMENT", "true")
    get_feature_flags.cache_clear()
    get_client_enrollment_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_client_enrollment_settings.cache_clear()


def test_enrollment_status_ready_when_skip_payment(
    api_client: TestClient,
    enrollment_env: None,
    test_org: object,
) -> None:
    response = api_client.get("/api/v1/enrollment/status")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["annual_credit_report_url"].endswith("annualcreditreport.com/index.action")


def test_register_without_payment_provisions_portal_account(
    api_client: TestClient,
    enrollment_env: None,
    test_org: object,
) -> None:
    email = "newclient.enroll@example.com"
    response = api_client.post(
        "/api/v1/enrollment/register",
        json={
            "email": email,
            "password": "changeme123",
            "first_name": "New",
            "last_name": "Client",
            "phone": "555-0100",
            "mailing_address_line1": "123 Main St",
            "mailing_city": "Senoia",
            "mailing_state": "GA",
            "mailing_postal_code": "30276",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["enrollment"]["status"] == "completed"
    assert payload["enrollment"]["case_id"] is not None
    assert payload["portal"]["access_token"]

    login_response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "changeme123"},
    )
    assert login_response.status_code == 200, login_response.text


def test_enrollment_hidden_when_disabled(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_ENROLLMENT", "false")
    get_feature_flags.cache_clear()
    response = api_client.get("/api/v1/enrollment/status")
    assert response.status_code == 404
