"""Tests for advisory re-dispute / escalation readiness (Phase 10 slice 4)."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from api.modules.accounts.redispute_readiness import compute_redispute_readiness
from tests.accounts.conftest import sample_account_payload


def test_readiness_not_sent_prepares_initial() -> None:
    rec = compute_redispute_readiness(
        clock_state="not_sent", latest_outcome=None, dispute_round=0, risk_score=None
    )
    assert rec.action == "prepare_initial"
    assert rec.priority == "medium"


def test_readiness_awaiting_waits() -> None:
    rec = compute_redispute_readiness(
        clock_state="awaiting", latest_outcome=None, dispute_round=1, risk_score=None
    )
    assert rec.action == "wait"
    assert rec.priority == "low"


def test_readiness_overdue_redisputes_high() -> None:
    rec = compute_redispute_readiness(
        clock_state="overdue", latest_outcome=None, dispute_round=1, risk_score=None
    )
    assert rec.action == "redispute"
    assert rec.priority == "high"


def test_readiness_responded_deleted_is_resolved() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="deleted", dispute_round=1, risk_score=None
    )
    assert rec.action == "resolved"
    assert rec.priority == "low"


def test_readiness_responded_updated_redisputes() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="updated", dispute_round=1, risk_score=None
    )
    assert rec.action == "redispute"
    assert rec.priority == "medium"


def test_readiness_responded_rejected_escalates_cfpb() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="rejected", dispute_round=1, risk_score=None
    )
    assert rec.action == "escalate_cfpb"
    assert rec.priority == "high"


def test_readiness_verified_first_round_redisputes_with_mov() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="verified", dispute_round=1, risk_score=40
    )
    assert rec.action == "redispute"
    assert "verification" in rec.reason.lower()


def test_readiness_verified_multi_round_escalates_cfpb() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="verified", dispute_round=2, risk_score=40
    )
    assert rec.action == "escalate_cfpb"
    assert rec.priority == "high"


def test_readiness_verified_high_strength_escalates_attorney() -> None:
    rec = compute_redispute_readiness(
        clock_state="responded", latest_outcome="verified", dispute_round=1, risk_score=90
    )
    assert rec.action == "escalate_attorney"
    assert rec.priority == "high"


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


def test_case_redispute_readiness_prioritizes_actionable(
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
        creditor_name="Not Sent Bank",
        last_dispute_date=None,
    )

    readiness = api_client.get(
        "/api/v1/accounts/redispute-readiness",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    assert readiness.status_code == 200, readiness.text
    body = readiness.json()
    assert body["summary"]["redispute"] >= 1
    assert body["summary"]["prepare_initial"] >= 1
    assert body["summary"]["high_priority"] >= 1
    # High-priority (overdue → redispute) sorts first.
    assert body["accounts"][0]["account_id"] == overdue_id
    assert body["accounts"][0]["action"] == "redispute"
    assert body["accounts"][0]["priority"] == "high"


def test_case_redispute_readiness_resolved_after_delete(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Deleted Bank",
        last_dispute_date=overdue_date,
    )
    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "deleted", "response_method": "mail"},
    )
    assert record.status_code == 201

    readiness = api_client.get(
        "/api/v1/accounts/redispute-readiness",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    entry = next(a for a in readiness.json()["accounts"] if a["account_id"] == account_id)
    assert entry["action"] == "resolved"
    assert entry["latest_outcome"] == "deleted"
