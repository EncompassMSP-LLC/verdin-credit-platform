"""Tests for reinvestigation outcome analytics (Phase 11 slice 4)."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from api.modules.accounts.reinvestigation_analytics import (
    ReinvestigationOutcomeRow,
    compute_reinvestigation_outcome_analytics,
)
from tests.accounts.conftest import sample_account_payload


def test_analytics_empty_rows_are_zeroed() -> None:
    result = compute_reinvestigation_outcome_analytics([])
    assert result.total_responses == 0
    assert result.counts == {
        "deleted": 0,
        "verified": 0,
        "updated": 0,
        "corrected": 0,
        "no_response": 0,
        "rejected": 0,
    }
    assert result.deletion_rate == 0.0
    assert result.favorable_rate == 0.0
    assert result.avg_days_to_response is None
    assert result.median_days_to_response is None
    assert result.measured_response_count == 0


def test_analytics_rates_and_durations() -> None:
    rows = [
        ReinvestigationOutcomeRow("deleted", 15),
        ReinvestigationOutcomeRow("verified", 20),
        ReinvestigationOutcomeRow("corrected", 10),
        ReinvestigationOutcomeRow("no_response", None),
    ]
    result = compute_reinvestigation_outcome_analytics(rows)
    assert result.total_responses == 4
    assert result.counts["deleted"] == 1
    assert result.counts["no_response"] == 1
    assert result.deletion_rate == 0.25
    assert result.verification_rate == 0.25
    assert result.correction_rate == 0.25
    assert result.favorable_rate == 0.5  # deleted + corrected
    assert result.no_response_rate == 0.25
    # Only substantive responses with a duration contribute to timing stats.
    assert result.measured_response_count == 3
    assert result.avg_days_to_response == 15.0
    assert result.median_days_to_response == 15.0


def test_analytics_ignores_no_response_durations() -> None:
    rows = [
        ReinvestigationOutcomeRow("verified", 30),
        # A stray duration on a no_response row must not skew the timing stats.
        ReinvestigationOutcomeRow("no_response", 99),
    ]
    result = compute_reinvestigation_outcome_analytics(rows)
    assert result.measured_response_count == 1
    assert result.avg_days_to_response == 30.0


def _create_account_with_dispute_date(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    creditor_name: str,
    last_dispute_date: str,
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    payload["last_dispute_date"] = last_dispute_date
    create = api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    assert create.status_code == 201, create.text
    return create.json()["id"]


def _record_response(
    api_client: TestClient,
    manager_headers: dict[str, str],
    account_id: str,
    *,
    outcome: str,
    response_date: str,
) -> None:
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": outcome, "response_method": "mail", "response_date": response_date},
    )
    assert response.status_code == 201, response.text


def test_reinvestigation_outcomes_endpoint_aggregates_org(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    deleted_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Deleted Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        deleted_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),  # 15 days
    )

    verified_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Verified Bank",
        last_dispute_date=(today - timedelta(days=30)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        verified_id,
        outcome="verified",
        response_date=(today - timedelta(days=10)).isoformat(),  # 20 days
    )

    response = api_client.get("/api/v1/reporting/reinvestigation-outcomes", headers=manager_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "generated_at" in body
    analytics = body["analytics"]
    assert analytics["total_responses"] == 2
    assert analytics["counts"]["deleted"] == 1
    assert analytics["counts"]["verified"] == 1
    assert analytics["deletion_rate"] == 0.5
    assert analytics["verification_rate"] == 0.5
    assert analytics["favorable_rate"] == 0.5
    assert analytics["measured_response_count"] == 2
    assert analytics["avg_days_to_response"] == 17.5


def test_reinvestigation_outcomes_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/reporting/reinvestigation-outcomes")
    assert response.status_code == 401
