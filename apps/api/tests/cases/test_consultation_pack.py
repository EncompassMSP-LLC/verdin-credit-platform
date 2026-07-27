"""Consultation completed pack tests (LRP-204)."""

import io
import uuid
import zipfile

from fastapi.testclient import TestClient

from tests.accounts.conftest import sample_account_payload


def _create_case(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Consult Pack {uuid.uuid4().hex[:6]}",
            "client_name": f"Consult Client {uuid.uuid4().hex[:6]}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_consultation_pack_create_export_and_guardrails(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id = _create_case(api_client, manager_headers)
    account = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(case_id),
    )
    assert account.status_code == 201, account.text
    analysis = api_client.post(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert analysis.status_code == 201, analysis.text

    created = api_client.post(
        f"/api/v1/cases/{case_id}/consultation-pack/runs",
        headers=manager_headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["case_id"] == case_id
    assert body["status"] == "draft"
    assert body["disclaimer"]
    artifacts = body["payload"]["artifacts"]
    assert "readiness_snapshot" in artifacts
    assert "timeline" in artifacts
    assert "action_plan" in artifacts
    assert "status_report" in artifacts
    assert "partner_notification" in artifacts
    assert artifacts["partner_notification"]["status"] == "draft_never_sent"
    assert body["payload"]["send_guardrails"]["auto_transmit"] is False
    assert body["payload"]["send_guardrails"]["partner_notification_sent"] is False

    latest = api_client.get(
        f"/api/v1/cases/{case_id}/consultation-pack/runs/latest",
        headers=manager_headers,
    )
    assert latest.status_code == 200, latest.text
    run_id = latest.json()["id"]

    text_export = api_client.get(
        f"/api/v1/cases/{case_id}/consultation-pack/runs/{run_id}/export",
        headers=manager_headers,
        params={"export_format": "text"},
    )
    assert text_export.status_code == 200, text_export.text
    assert "text/plain" in text_export.headers.get("content-type", "")
    assert "DRAFT" in text_export.text
    assert "never auto-transmitted" in text_export.text.lower()

    zip_export = api_client.get(
        f"/api/v1/cases/{case_id}/consultation-pack/runs/{run_id}/export",
        headers=manager_headers,
        params={"export_format": "zip"},
    )
    assert zip_export.status_code == 200, zip_export.text
    assert "application/zip" in zip_export.headers.get("content-type", "")
    with zipfile.ZipFile(io.BytesIO(zip_export.content)) as archive:
        names = set(archive.namelist())
        assert "00-README.txt" in names
        assert "manifest.json" in names
        assert any(name.endswith("partner_notification.txt") for name in names)


def test_consultation_pack_without_readiness_still_drafts(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id = _create_case(api_client, manager_headers)
    created = api_client.post(
        f"/api/v1/cases/{case_id}/consultation-pack/runs",
        headers=manager_headers,
    )
    assert created.status_code == 201, created.text
    snapshot = created.json()["payload"]["artifacts"]["readiness_snapshot"]
    assert snapshot["status"] == "missing_readiness"
