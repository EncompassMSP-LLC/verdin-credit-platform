"""API tests for credit analysis runs + portal readiness."""

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from tests.accounts.conftest import sample_account_payload
from tests.helpers.client_payload import sample_client_payload


@pytest.fixture(autouse=True)
def _enable_client_portal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_staff_credit_analysis_run_and_portal_readiness(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    case_id = sample_case_id

    account_resp = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(case_id),
    )
    assert account_resp.status_code == 201, account_resp.text

    create = api_client.post(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["case_id"] == case_id
    assert body["status"] == "published"
    assert body["band"] in {"building", "progressing", "near_ready", "lending_ready"}
    assert 0 <= body["borrower_readiness_score"] <= 100
    assert body["tradelines_evaluated"] == 1
    assert "disclaimer" in body["payload"]

    latest = api_client.get(
        f"/api/v1/cases/{case_id}/credit-analysis/runs/latest",
        headers=manager_headers,
    )
    assert latest.status_code == 200, latest.text
    assert latest.json()["id"] == body["id"]

    listed = api_client.get(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert listed.status_code == 200, listed.text
    assert len(listed.json()["items"]) >= 1

    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(
            display_name="Portal Borrower",
            email="borrower-lrs@example.com",
        ),
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]

    case_link = api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": "borrower-lrs@example.com"},
    )
    assert case_link.status_code == 200, case_link.text

    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": "borrower-lrs@example.com", "password": "password123"},
    )
    assert provision.status_code == 201, provision.text

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": "borrower-lrs@example.com", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    portal_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    readiness = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness",
        headers=portal_headers,
    )
    assert readiness.status_code == 200, readiness.text
    payload = readiness.json()
    assert payload["case_id"] == case_id
    assert payload["band"] == body["band"]
    assert payload["disclaimer"]
    assert isinstance(payload["dimensions"], list)
    assert len(payload["dimensions"]) == 8


def test_portal_readiness_404_without_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(
            display_name="Empty Readiness",
            email="empty-lrs@example.com",
        ),
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]
    api_client.patch(
        f"/api/v1/cases/{sample_case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": "empty-lrs@example.com"},
    )
    api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": "empty-lrs@example.com", "password": "password123"},
    )
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": "empty-lrs@example.com", "password": "password123"},
    )
    portal_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    readiness = api_client.get(
        f"/api/v1/portal/cases/{sample_case_id}/readiness",
        headers=portal_headers,
    )
    assert readiness.status_code == 404
