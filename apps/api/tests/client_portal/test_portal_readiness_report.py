"""Portal readiness report view + band-first export (LRP-106)."""

import uuid

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


def _setup_portal_with_published_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> tuple[str, dict[str, str]]:
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Report Case {uuid.uuid4().hex[:6]}",
            "client_name": f"Report Client {uuid.uuid4().hex[:6]}",
        },
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

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

    email = f"report-{uuid.uuid4().hex[:8]}@example.com"
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Report Borrower", email=email),
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]
    api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": email},
    )
    api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "password": "password123"},
    )
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    return case_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_portal_readiness_report_json_and_exports(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id, portal_headers = _setup_portal_with_published_run(api_client, manager_headers)

    report = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report",
        headers=portal_headers,
    )
    assert report.status_code == 200, report.text
    body = report.json()
    assert body["case_id"] == case_id
    assert body["band"]
    assert body["disclaimer"]
    assert "mortgage_readiness_score" not in body
    assert isinstance(body["dimensions"], list)
    assert isinstance(body["blockers"], list)

    text_export = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report/export",
        headers=portal_headers,
        params={"format": "text"},
    )
    assert text_export.status_code == 200, text_export.text
    assert "text/plain" in text_export.headers.get("content-type", "")
    text_body = text_export.text
    assert "DISCLAIMER" in text_body
    assert "READINESS BAND" in text_body
    assert "/100" not in text_body

    pdf_export = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report/export",
        headers=portal_headers,
        params={"format": "pdf"},
    )
    assert pdf_export.status_code == 200, pdf_export.text
    assert "application/pdf" in pdf_export.headers.get("content-type", "")
    assert pdf_export.content[:4] == b"%PDF"


def test_portal_readiness_report_404_without_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Empty Report {uuid.uuid4().hex[:6]}",
            "client_name": f"Empty Client {uuid.uuid4().hex[:6]}",
        },
    )
    case_id = case_resp.json()["id"]
    email = f"empty-report-{uuid.uuid4().hex[:8]}@example.com"
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Empty Report", email=email),
    )
    client_id = client_resp.json()["id"]
    api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": email},
    )
    api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "password": "password123"},
    )
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    portal_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    report = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report",
        headers=portal_headers,
    )
    assert report.status_code == 404
