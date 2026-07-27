"""Portal action-plan checklist tests (LRP-104)."""

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


def _create_case(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Checklist Case {uuid.uuid4().hex[:6]}",
            "client_name": f"Checklist Client {uuid.uuid4().hex[:6]}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _portal_headers_for_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    email: str,
) -> dict[str, str]:
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Checklist Borrower", email=email),
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
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_portal_checklist_baseline_and_blocker_parity(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id = _create_case(api_client, manager_headers)
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

    portal_headers = _portal_headers_for_case(
        api_client,
        manager_headers,
        case_id,
        email=f"checklist-parity-{uuid.uuid4().hex[:8]}@example.com",
    )

    readiness = api_client.get(
        f"/api/v1/portal/cases/{case_id}/readiness",
        headers=portal_headers,
    )
    assert readiness.status_code == 200, readiness.text
    blockers = readiness.json()["blockers"]

    checklist = api_client.get(
        f"/api/v1/portal/cases/{case_id}/checklist",
        headers=portal_headers,
    )
    assert checklist.status_code == 200, checklist.text
    body = checklist.json()
    assert body["case_id"] == case_id
    keys = {item["id"] for item in body["items"]}
    assert "baseline:review-readiness" in keys
    assert "baseline:upload-documents" in keys
    assert "baseline:ask-advisor" in keys
    for blocker in blockers:
        assert f"blocker:{blocker['id']}" in keys

    target = next(item for item in body["items"] if item["id"] == "baseline:review-readiness")
    assert target["status"] == "open"

    patched = api_client.patch(
        "/api/v1/portal/checklist/baseline:review-readiness",
        headers=portal_headers,
        json={"status": "done"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["status"] == "done"

    refreshed = api_client.get(
        f"/api/v1/portal/cases/{case_id}/checklist",
        headers=portal_headers,
    )
    assert refreshed.status_code == 200, refreshed.text
    done_item = next(
        item for item in refreshed.json()["items"] if item["id"] == "baseline:review-readiness"
    )
    assert done_item["status"] == "done"


def test_portal_checklist_without_published_run_still_returns_baseline(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id = _create_case(api_client, manager_headers)
    portal_headers = _portal_headers_for_case(
        api_client,
        manager_headers,
        case_id,
        email=f"checklist-empty-{uuid.uuid4().hex[:8]}@example.com",
    )
    checklist = api_client.get(
        f"/api/v1/portal/cases/{case_id}/checklist",
        headers=portal_headers,
    )
    assert checklist.status_code == 200, checklist.text
    items = checklist.json()["items"]
    assert len(items) == 3
    assert all(item["id"].startswith("baseline:") for item in items)
