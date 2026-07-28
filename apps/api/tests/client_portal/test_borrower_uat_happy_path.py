"""Borrower portal UAT happy-path API coverage (LRP-303).

Exercises the V1.0 borrower journey without demo credentials:
login → me → cases → readiness → checklist → timeline → report → documents → messages,
plus staff/cross-client isolation.
"""

from __future__ import annotations

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


def _setup_uat_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> tuple[str, dict[str, str], str]:
    """Return case_id, portal_headers, portal_email."""
    email = f"uat-borrower-{uuid.uuid4().hex[:8]}@example.com"
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"UAT Case {uuid.uuid4().hex[:6]}",
            "client_name": "UAT Borrower",
            "client_email": email,
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
    run_resp = api_client.post(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert run_resp.status_code == 201, run_resp.text

    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="UAT Borrower", email=email),
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]
    link = api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": email},
    )
    assert link.status_code == 200, link.text

    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "password": "password123"},
    )
    assert provision.status_code == 201, provision.text

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    portal_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return case_id, portal_headers, email


def test_borrower_uat_happy_path_and_isolation(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id, portal_headers, email = _setup_uat_case(api_client, manager_headers)

    me = api_client.get("/api/v1/portal/auth/me", headers=portal_headers)
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email

    cases = api_client.get("/api/v1/portal/cases", headers=portal_headers)
    assert cases.status_code == 200, cases.text
    case_ids = {row["id"] for row in cases.json()["items"]}
    assert case_id in case_ids

    detail = api_client.get(f"/api/v1/portal/cases/{case_id}", headers=portal_headers)
    assert detail.status_code == 200, detail.text

    readiness = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness",
        headers=portal_headers,
    )
    assert readiness.status_code == 200, readiness.text
    readiness_body = readiness.json()
    assert readiness_body["band"]
    assert readiness_body["disclaimer"]
    assert "mortgage_readiness_score" not in readiness_body

    checklist = api_client.get(
        f"/api/v1/portal/cases/{case_id}/checklist",
        headers=portal_headers,
    )
    assert checklist.status_code == 200, checklist.text
    checklist_body = checklist.json()
    assert checklist_body["case_id"] == case_id
    items = checklist_body["items"]
    assert len(items) >= 1
    open_item = next(item for item in items if item["status"] == "open")
    patch = api_client.patch(
        f"/api/v1/portal/checklist/{open_item['id']}",
        headers=portal_headers,
        json={"status": "done"},
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["status"] == "done"

    timeline = api_client.get(
        f"/api/v1/portal/cases/{case_id}/timeline",
        headers=portal_headers,
    )
    assert timeline.status_code == 200, timeline.text
    timeline_items = timeline.json()["items"]
    assert len(timeline_items) >= 1
    types = {item["event_type"] for item in timeline_items}
    assert "case" in types
    assert "readiness" in types

    report = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report",
        headers=portal_headers,
    )
    assert report.status_code == 200, report.text
    report_body = report.json()
    assert report_body["disclaimer"]
    assert report_body["band"]
    assert "mortgage_readiness_score" not in report_body

    export = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness-report/export",
        headers=portal_headers,
        params={"format": "text"},
    )
    assert export.status_code == 200, export.text
    assert "DISCLAIMER" in export.text

    documents = api_client.get(
        f"/api/v1/portal/cases/{case_id}/documents",
        headers=portal_headers,
    )
    assert documents.status_code == 200, documents.text

    messages = api_client.get(
        f"/api/v1/portal/cases/{case_id}/messages",
        headers=portal_headers,
    )
    assert messages.status_code == 200, messages.text
    assert "messages" in messages.json()
    send = api_client.post(
        f"/api/v1/portal/cases/{case_id}/messages",
        headers=portal_headers,
        json={"body": "UAT borrower check-in — please confirm next steps."},
    )
    assert send.status_code == 201, send.text

    # Staff JWT is not a portal session
    staff_on_portal = api_client.get("/api/v1/portal/cases", headers=manager_headers)
    assert staff_on_portal.status_code in {401, 403}

    # Isolation: another client's case is not visible
    other_case = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Other Case {uuid.uuid4().hex[:6]}",
            "client_name": "Other Client",
        },
    )
    assert other_case.status_code == 201, other_case.text
    other_id = other_case.json()["id"]
    forbidden = api_client.get(
        f"/api/v1/portal/cases/{other_id}/readiness",
        headers=portal_headers,
    )
    assert forbidden.status_code in {403, 404}
