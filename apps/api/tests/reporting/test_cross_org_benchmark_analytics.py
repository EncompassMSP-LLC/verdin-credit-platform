"""Cross-org benchmark analytics scaffold tests."""

from fastapi.testclient import TestClient


def _create_case(api_client: TestClient, headers: dict[str, str], *, title: str) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": title, "client_name": "Benchmark Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_account(api_client: TestClient, headers: dict[str, str], *, case_id: str) -> None:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json={
            "case_id": case_id,
            "creditor_name": "Benchmark Creditor",
            "bureau": "experian",
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "current",
            "dispute_status": "corrected",
        },
    )
    assert response.status_code == 201, response.text


def test_cross_org_benchmarks_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/cross-org-benchmarks/status", headers=manager_headers
    )
    assert response.status_code == 404


def test_cross_org_benchmark_summary_and_refresh(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    cross_org_benchmark_enabled: None,
) -> None:
    case_id = _create_case(api_client, manager_headers, title="Cross Org Benchmark Case")
    _create_account(api_client, manager_headers, case_id=case_id)

    status_response = api_client.get(
        "/api/v1/reporting/cross-org-benchmarks/status",
        headers=manager_headers,
    )
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["enabled"] is True

    summary_response = api_client.get(
        "/api/v1/reporting/cross-org-benchmarks", headers=manager_headers
    )
    assert summary_response.status_code == 200, summary_response.text
    payload = summary_response.json()["benchmarks"]
    assert payload["organizations_evaluated"] >= 1
    assert payload["resolved_accounts"] >= 1

    refresh_response = api_client.post(
        "/api/v1/reporting/cross-org-benchmarks/refresh",
        headers=admin_headers,
    )
    assert refresh_response.status_code == 200, refresh_response.text
    assert refresh_response.json()["run"]["status"] == "completed"

    runs_response = api_client.get(
        "/api/v1/reporting/cross-org-benchmarks/runs", headers=manager_headers
    )
    assert runs_response.status_code == 200, runs_response.text
    assert len(runs_response.json()) >= 1
