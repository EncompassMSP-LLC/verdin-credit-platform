"""Tests for the FCRA §611 reinvestigation clock (Phase 10 slice 3)."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from api.modules.accounts.reinvestigation import compute_reinvestigation_clock
from tests.accounts.conftest import sample_account_payload

_TODAY = date(2026, 7, 15)


def test_compute_clock_not_sent() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=None, today=_TODAY, response_recorded=False
    )
    assert clock.state == "not_sent"
    assert clock.deadline is None
    assert clock.days_remaining is None


def test_compute_clock_awaiting() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY, today=_TODAY, response_recorded=False
    )
    assert clock.state == "awaiting"
    assert clock.deadline == _TODAY + timedelta(days=30)
    assert clock.days_remaining == 30


def test_compute_clock_due_soon() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=25), today=_TODAY, response_recorded=False
    )
    assert clock.state == "due_soon"
    assert clock.days_remaining == 5


def test_compute_clock_overdue() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=40), today=_TODAY, response_recorded=False
    )
    assert clock.state == "overdue"
    assert clock.days_remaining == -10


def test_compute_clock_responded_short_circuits() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=40), today=_TODAY, response_recorded=True
    )
    assert clock.state == "responded"


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


def test_case_reinvestigation_clock_classifies_and_summarizes(
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

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    assert clock.status_code == 200
    body = clock.json()
    assert body["summary"]["overdue"] >= 1
    assert body["summary"]["awaiting"] >= 1
    assert body["summary"]["not_sent"] >= 1
    # Overdue entries are sorted first.
    assert body["accounts"][0]["state"] == "overdue"
    assert body["accounts"][0]["account_id"] == overdue_id


def test_case_reinvestigation_clock_marks_responded(
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
        json={"outcome": "verified", "response_method": "mail"},
    )
    assert record.status_code == 201

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    entry = next(a for a in clock.json()["accounts"] if a["account_id"] == account_id)
    assert entry["state"] == "responded"
    assert entry["response_received"] is True
    assert entry["response_count"] == 1
