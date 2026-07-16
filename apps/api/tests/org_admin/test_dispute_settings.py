"""Tests for organization dispute settings (Version 16.0 slice 2)."""

from fastapi.testclient import TestClient

from tests.accounts.conftest import sample_account_payload

pytest_plugins = ["tests.accounts.conftest"]


def test_get_dispute_settings_defaults(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/dispute-settings", headers=admin_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["cross_bureau_balance_tolerance"] == "1.00"
    assert body["platform_default_tolerance"] == "1.00"
    assert body["updated_at"] is None


def test_patch_dispute_settings_persists_tolerance(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    patch = api_client.patch(
        "/api/v1/org-admin/dispute-settings",
        headers=admin_headers,
        json={"cross_bureau_balance_tolerance": "2.50"},
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["cross_bureau_balance_tolerance"] == "2.50"
    assert patch.json()["updated_at"] is not None

    get = api_client.get("/api/v1/org-admin/dispute-settings", headers=admin_headers)
    assert get.status_code == 200
    assert get.json()["cross_bureau_balance_tolerance"] == "2.50"


def test_patch_dispute_settings_rejects_out_of_range(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.patch(
        "/api/v1/org-admin/dispute-settings",
        headers=admin_headers,
        json={"cross_bureau_balance_tolerance": "150.00"},
    )
    assert response.status_code == 422


def test_litigation_packet_uses_org_cross_bureau_tolerance(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    sample_case_id: str,
    enterprise_enabled: None,
) -> None:
    api_client.patch(
        "/api/v1/org-admin/dispute-settings",
        headers=admin_headers,
        json={"cross_bureau_balance_tolerance": "5.00"},
    )

    payload = sample_account_payload(sample_case_id)
    payload["creditor_name"] = "Tolerance Bank"
    payload["last_dispute_date"] = "2026-07-01"
    experian_payload = {**payload, "bureau": "experian", "balance": "1000.00"}
    equifax_payload = {**payload, "bureau": "equifax", "balance": "1003.00"}
    experian = api_client.post("/api/v1/accounts", headers=manager_headers, json=experian_payload)
    equifax = api_client.post("/api/v1/accounts", headers=manager_headers, json=equifax_payload)
    assert experian.status_code == 201
    assert equifax.status_code == 201
    experian_id = experian.json()["id"]

    packet = api_client.get(
        f"/api/v1/accounts/{experian_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    kinds = {d["kind"] for d in packet.json()["cross_bureau"]["discrepancies"]}
    assert "balance_conflict" not in kinds

    api_client.patch(
        "/api/v1/org-admin/dispute-settings",
        headers=admin_headers,
        json={"cross_bureau_balance_tolerance": "1.00"},
    )
    packet_strict = api_client.get(
        f"/api/v1/accounts/{experian_id}/litigation-packet",
        headers=manager_headers,
    )
    strict_kinds = {d["kind"] for d in packet_strict.json()["cross_bureau"]["discrepancies"]}
    assert "balance_conflict" in strict_kinds
