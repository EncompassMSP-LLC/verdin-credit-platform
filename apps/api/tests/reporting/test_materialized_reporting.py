"""Reporting materialized view tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_reporting import get_enterprise_reporting_status
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def materialized_reporting_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_MATERIALIZED_REPORTING", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def _create_case(api_client: TestClient, headers: dict[str, str], *, title: str) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": title, "client_name": "MV Reporting Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_account(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
    bureau: str,
) -> str:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json={
            "case_id": case_id,
            "creditor_name": f"{bureau.title()} Creditor",
            "bureau": bureau,
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "current",
            "dispute_status": "dispute_sent",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_enterprise_status_lists_materialized_views_when_enabled(
    materialized_reporting_enabled: None,
) -> None:
    status = get_enterprise_reporting_status()
    assert "materialized_views" in status.capabilities
    assert "materialized_views" not in status.deferred_capabilities


def test_enterprise_status_defers_materialized_views_when_disabled() -> None:
    status = get_enterprise_reporting_status()
    assert "materialized_views" in status.deferred_capabilities


def test_materialized_endpoints_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/reporting/materialized-views/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_materialized_status_when_enabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    materialized_reporting_enabled: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/materialized-views/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["enabled"] is True
    assert "mv_bureau_account_counts" in data["views"]
    assert data["last_refreshed_at"] is None


def test_refresh_materialized_views_requires_admin(
    api_client: TestClient,
    manager_headers: dict[str, str],
    materialized_reporting_enabled: None,
) -> None:
    response = api_client.post(
        "/api/v1/reporting/materialized-views/refresh",
        headers=manager_headers,
    )
    assert response.status_code == 403


def test_bureau_performance_uses_materialized_views_when_enabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    materialized_reporting_enabled: None,
) -> None:
    case_id = _create_case(api_client, manager_headers, title="MV Bureau Case")
    _create_account(api_client, manager_headers, case_id=case_id, bureau="equifax")

    refresh = api_client.post(
        "/api/v1/reporting/materialized-views/refresh",
        headers=admin_headers,
    )
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()["views_refreshed"] == 3

    response = api_client.get("/api/v1/reporting/bureau-performance", headers=manager_headers)
    assert response.status_code == 200, response.text
    performance = response.json()["bureau_performance"]
    assert performance["total_accounts"] >= 1
    bureaus = {item["bureau"]: item for item in performance["bureaus"]}
    assert bureaus["equifax"]["total_accounts"] >= 1

    status = api_client.get(
        "/api/v1/reporting/materialized-views/status",
        headers=admin_headers,
    )
    assert status.status_code == 200
    assert status.json()["last_refreshed_at"] is not None

    runs = api_client.get(
        "/api/v1/reporting/materialized-views/runs",
        headers=admin_headers,
    )
    assert runs.status_code == 200
    assert runs.json()["total"] >= 1
