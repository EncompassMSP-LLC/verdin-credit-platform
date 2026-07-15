"""Tests for the per-case reinvestigation summary read model (Phase 10 slice 5)."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.accounts.conftest import sample_account_payload


def _create_account_with_dispute_date(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    creditor_name: str,
    last_dispute_date: str | None,
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    if last_dispute_date is not None:
        payload["last_dispute_date"] = last_dispute_date
    create = api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    assert create.status_code == 201, create.text
    return create.json()["id"]


def test_case_reinvestigation_summary_aggregates(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    overdue_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Overdue Bank",
        last_dispute_date=overdue_date,
    )
    _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Awaiting Bank",
        last_dispute_date=date.today().isoformat(),
    )
    _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Not Sent Bank",
        last_dispute_date=None,
    )

    summary = api_client.get(
        "/api/v1/accounts/reinvestigation-summary",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    assert summary.status_code == 200, summary.text
    body = summary.json()

    assert body["total_accounts"] >= 3
    assert body["disputed_accounts"] >= 2
    assert body["clock"]["overdue"] >= 1
    assert body["clock"]["awaiting"] >= 1
    assert body["clock"]["not_sent"] >= 1
    assert body["readiness"]["high_priority"] >= 1
    # Overdue tradeline drives a high-priority action item + most-overdue metric.
    assert body["most_overdue_days"] is not None and body["most_overdue_days"] >= 9
    assert any(item["account_id"] == overdue_id for item in body["action_items"])
    # The awaiting tradeline (mailed today) provides the next upcoming deadline.
    assert body["next_deadline"] is not None


def test_case_reinvestigation_summary_counts_responses(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Responded Bank",
        last_dispute_date=overdue_date,
    )
    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "deleted", "response_method": "mail"},
    )
    assert record.status_code == 201

    summary = api_client.get(
        "/api/v1/accounts/reinvestigation-summary",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    body = summary.json()
    assert body["total_responses"] >= 1
    assert body["readiness"]["resolved"] >= 1
