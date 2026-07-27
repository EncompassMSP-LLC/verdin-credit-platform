"""Portal readiness timeline tests (LRP-401)."""

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


def _setup_portal_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    *,
    with_run: bool = True,
) -> tuple[str, dict[str, str]]:
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Timeline Case {uuid.uuid4().hex[:6]}",
            "client_name": f"Timeline Client {uuid.uuid4().hex[:6]}",
        },
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    if with_run:
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

    email = f"timeline-{uuid.uuid4().hex[:8]}@example.com"
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Timeline Borrower", email=email),
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


def test_portal_timeline_composes_case_and_readiness(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id, portal_headers = _setup_portal_case(api_client, manager_headers)

    timeline = api_client.get(
        f"/api/v1/portal/cases/{case_id}/timeline",
        headers=portal_headers,
    )
    assert timeline.status_code == 200, timeline.text
    body = timeline.json()
    assert body["case_id"] == case_id
    types = {item["event_type"] for item in body["items"]}
    assert "case" in types
    assert "readiness" in types
    assert all("href" in item for item in body["items"])
    assert all(item["title"] for item in body["items"])

    filtered = api_client.get(
        f"/api/v1/portal/cases/{case_id}/timeline",
        headers=portal_headers,
        params={"event_type": "readiness"},
    )
    assert filtered.status_code == 200, filtered.text
    filtered_items = filtered.json()["items"]
    assert filtered_items
    assert all(item["event_type"] == "readiness" for item in filtered_items)


def test_portal_timeline_includes_completed_tasks(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id, portal_headers = _setup_portal_case(api_client, manager_headers)

    patched = api_client.patch(
        "/api/v1/portal/checklist/baseline:review-readiness",
        headers=portal_headers,
        json={"status": "done"},
    )
    assert patched.status_code == 200, patched.text

    timeline = api_client.get(
        f"/api/v1/portal/cases/{case_id}/timeline",
        headers=portal_headers,
        params={"event_type": "task"},
    )
    assert timeline.status_code == 200, timeline.text
    items = timeline.json()["items"]
    assert any(item["id"].startswith("task-") for item in items)


def test_portal_timeline_404_for_unknown_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    _, portal_headers = _setup_portal_case(api_client, manager_headers, with_run=False)
    missing = api_client.get(
        f"/api/v1/portal/cases/{uuid.uuid4()}/timeline",
        headers=portal_headers,
    )
    assert missing.status_code == 404
