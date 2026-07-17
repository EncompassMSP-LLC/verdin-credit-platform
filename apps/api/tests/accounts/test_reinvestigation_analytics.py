"""Tests for reinvestigation outcome analytics (Phase 11 slice 4)."""

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
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
    bureau: str = "equifax",
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    payload["last_dispute_date"] = last_dispute_date
    payload["bureau"] = bureau
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
    assert body["filters"] == {"start": None, "end": None, "bureau": None, "group_by": None}
    assert body["by_bureau"] == []
    assert body["by_recipient"] == []
    analytics = body["analytics"]
    assert analytics["total_responses"] == 2
    assert analytics["counts"]["deleted"] == 1
    assert analytics["counts"]["verified"] == 1
    assert analytics["deletion_rate"] == 0.5
    assert analytics["verification_rate"] == 0.5
    assert analytics["favorable_rate"] == 0.5
    assert analytics["measured_response_count"] == 2
    assert analytics["avg_days_to_response"] == 17.5


def test_reinvestigation_outcomes_filters_by_bureau(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    equifax_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Equifax Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
        bureau="equifax",
    )
    _record_response(
        api_client,
        manager_headers,
        equifax_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),
    )
    experian_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Experian Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
        bureau="experian",
    )
    _record_response(
        api_client,
        manager_headers,
        experian_id,
        outcome="verified",
        response_date=(today - timedelta(days=5)).isoformat(),
    )

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes",
        headers=manager_headers,
        params={"bureau": "experian"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filters"]["bureau"] == "experian"
    analytics = body["analytics"]
    assert analytics["total_responses"] == 1
    assert analytics["counts"]["verified"] == 1
    assert analytics["counts"]["deleted"] == 0


def test_reinvestigation_outcomes_filters_by_date_range(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    old_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Old Response Bank",
        last_dispute_date=(today - timedelta(days=90)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        old_id,
        outcome="deleted",
        response_date=(today - timedelta(days=60)).isoformat(),
    )
    recent_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Recent Response Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        recent_id,
        outcome="verified",
        response_date=(today - timedelta(days=5)).isoformat(),
    )

    # Window that only includes the recent response.
    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes",
        headers=manager_headers,
        params={"start": (today - timedelta(days=30)).isoformat()},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filters"]["start"] == (today - timedelta(days=30)).isoformat()
    analytics = body["analytics"]
    assert analytics["total_responses"] == 1
    assert analytics["counts"]["verified"] == 1
    assert analytics["counts"]["deleted"] == 0


def test_reinvestigation_outcomes_group_by_bureau(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    equifax_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Equifax Group Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
        bureau="equifax",
    )
    _record_response(
        api_client,
        manager_headers,
        equifax_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),
    )
    experian_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Experian Group Bank",
        last_dispute_date=(today - timedelta(days=30)).isoformat(),
        bureau="experian",
    )
    _record_response(
        api_client,
        manager_headers,
        experian_id,
        outcome="verified",
        response_date=(today - timedelta(days=10)).isoformat(),
    )

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes",
        headers=manager_headers,
        params={"group_by": "bureau"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filters"]["group_by"] == "bureau"
    assert body["analytics"]["total_responses"] == 2
    by_bureau = {entry["bureau"]: entry["analytics"] for entry in body["by_bureau"]}
    assert set(by_bureau) == {"equifax", "experian"}
    assert by_bureau["equifax"]["total_responses"] == 1
    assert by_bureau["equifax"]["counts"]["deleted"] == 1
    assert by_bureau["equifax"]["deletion_rate"] == 1.0
    assert by_bureau["experian"]["total_responses"] == 1
    assert by_bureau["experian"]["counts"]["verified"] == 1
    assert by_bureau["experian"]["verification_rate"] == 1.0
    # Stable ordering: equifax before experian.
    assert [entry["bureau"] for entry in body["by_bureau"]] == ["equifax", "experian"]


async def test_reinvestigation_outcomes_group_by_recipient(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """group_by=recipient rolls up outcomes by the linked letter recipient type."""
    today = date.today()
    bureau_account = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Recipient Bureau Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    furnisher_account = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Recipient Furnisher Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    bureau_acct = api_client.get(
        f"/api/v1/accounts/{bureau_account}", headers=manager_headers
    ).json()
    org_id = bureau_acct["organization_id"]
    sent_at = datetime.now(UTC) - timedelta(days=20)

    bureau_letter_id = uuid.uuid4()
    furnisher_letter_id = uuid.uuid4()
    for letter_id, account_id, recipient in (
        (bureau_letter_id, bureau_account, "credit_bureau"),
        (furnisher_letter_id, furnisher_account, "furnisher"),
    ):
        db_session.add(
            DisputeLetter(
                id=letter_id,
                organization_id=uuid.UUID(org_id),
                case_id=uuid.UUID(sample_case_id),
                account_id=uuid.UUID(account_id),
                recipient_type=recipient,
                status=DisputeLetterStatus.SENT,
                template_id="fcra_611",
                subject=f"Dispute to {recipient}",
                body="Body",
                disputed_items=["late payment"],
                requested_action="Delete the inaccurate tradeline.",
                evidence_checklist=[],
                compliance_notes=[],
                generated_by="system",
                generated_at=sent_at,
                sent_at=sent_at,
            )
        )
    await db_session.commit()

    for account_id, letter_id, outcome in (
        (bureau_account, bureau_letter_id, "deleted"),
        (furnisher_account, furnisher_letter_id, "verified"),
    ):
        response = api_client.post(
            f"/api/v1/accounts/{account_id}/dispute-responses",
            headers=manager_headers,
            json={
                "outcome": outcome,
                "response_method": "mail",
                "response_date": (today - timedelta(days=5)).isoformat(),
                "dispute_letter_id": str(letter_id),
            },
        )
        assert response.status_code == 201, response.text

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes",
        headers=manager_headers,
        params={"group_by": "recipient"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filters"]["group_by"] == "recipient"
    assert body["by_bureau"] == []
    by_recipient = {entry["recipient"]: entry["analytics"] for entry in body["by_recipient"]}
    assert set(by_recipient) == {"credit_bureau", "furnisher"}
    assert by_recipient["credit_bureau"]["counts"]["deleted"] == 1
    assert by_recipient["furnisher"]["counts"]["verified"] == 1
    assert [entry["recipient"] for entry in body["by_recipient"]] == [
        "credit_bureau",
        "furnisher",
    ]


def test_reinvestigation_outcomes_rejects_invalid_group_by(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes",
        headers=manager_headers,
        params={"group_by": "creditor"},
    )
    assert response.status_code == 422


def test_reinvestigation_outcomes_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/reporting/reinvestigation-outcomes")
    assert response.status_code == 401


def test_reinvestigation_outcome_benchmarks_returns_org_baseline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    # Inside the recent (30d) window — counts toward both baseline and recent.
    recent_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Recent Deleted Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        recent_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),
    )
    # Outside recent, inside a 90-day baseline — baseline-only.
    baseline_only_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Baseline Verified Bank",
        last_dispute_date=(today - timedelta(days=80)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        baseline_only_id,
        outcome="verified",
        response_date=(today - timedelta(days=60)).isoformat(),
    )

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks",
        headers=manager_headers,
        params={"baseline_days": 90, "recent_days": 30},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["scope"] == "organization"
    assert body["bureau"] is None
    assert body["baseline_period"]["window_days"] == 90
    assert body["recent_period"]["window_days"] == 30
    assert body["baseline"]["total_responses"] == 2
    assert body["baseline"]["counts"]["deleted"] == 1
    assert body["baseline"]["counts"]["verified"] == 1
    assert body["baseline"]["deletion_rate"] == 0.5
    assert body["recent"]["total_responses"] == 1
    assert body["recent"]["counts"]["deleted"] == 1
    assert body["recent"]["deletion_rate"] == 1.0
    assert body["rate_deltas"]["deletion_rate"] == 0.5
    assert body["rate_deltas"]["verification_rate"] == -0.5
    assert body["by_bureau"] == []
    assert body["group_by"] is None
    assert body.get("by_recipient", []) == []


async def test_reinvestigation_outcome_benchmarks_group_by_recipient(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """group_by=recipient rolls up benchmark windows by linked letter recipient type."""
    today = date.today()
    bureau_account = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Bench Recipient Bureau Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    furnisher_account = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Bench Recipient Furnisher Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    bureau_acct = api_client.get(
        f"/api/v1/accounts/{bureau_account}", headers=manager_headers
    ).json()
    org_id = bureau_acct["organization_id"]
    sent_at = datetime.now(UTC) - timedelta(days=20)

    bureau_letter_id = uuid.uuid4()
    furnisher_letter_id = uuid.uuid4()
    for letter_id, account_id, recipient in (
        (bureau_letter_id, bureau_account, "credit_bureau"),
        (furnisher_letter_id, furnisher_account, "furnisher"),
    ):
        db_session.add(
            DisputeLetter(
                id=letter_id,
                organization_id=uuid.UUID(org_id),
                case_id=uuid.UUID(sample_case_id),
                account_id=uuid.UUID(account_id),
                recipient_type=recipient,
                status=DisputeLetterStatus.SENT,
                template_id="fcra_611",
                subject=f"Dispute to {recipient}",
                body="Body",
                disputed_items=["late payment"],
                requested_action="Delete the inaccurate tradeline.",
                evidence_checklist=[],
                compliance_notes=[],
                generated_by="system",
                generated_at=sent_at,
                sent_at=sent_at,
            )
        )
    await db_session.commit()

    for account_id, letter_id, outcome in (
        (bureau_account, bureau_letter_id, "deleted"),
        (furnisher_account, furnisher_letter_id, "verified"),
    ):
        response = api_client.post(
            f"/api/v1/accounts/{account_id}/dispute-responses",
            headers=manager_headers,
            json={
                "outcome": outcome,
                "response_method": "mail",
                "response_date": (today - timedelta(days=5)).isoformat(),
                "dispute_letter_id": str(letter_id),
            },
        )
        assert response.status_code == 201, response.text

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks",
        headers=manager_headers,
        params={"baseline_days": 90, "recent_days": 30, "group_by": "recipient"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["group_by"] == "recipient"
    assert body["by_bureau"] == []
    recipients = {item["recipient"]: item for item in body["by_recipient"]}
    assert set(recipients) == {"credit_bureau", "furnisher"}
    assert recipients["credit_bureau"]["recent"]["counts"]["deleted"] == 1
    assert recipients["furnisher"]["recent"]["counts"]["verified"] == 1
    assert "rate_deltas" in recipients["credit_bureau"]
    assert [item["recipient"] for item in body["by_recipient"]] == [
        "credit_bureau",
        "furnisher",
    ]


def test_reinvestigation_outcome_benchmarks_group_by_bureau(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    equifax_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Equifax Bench Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
        bureau="equifax",
    )
    _record_response(
        api_client,
        manager_headers,
        equifax_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),
    )
    experian_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Experian Bench Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
        bureau="experian",
    )
    _record_response(
        api_client,
        manager_headers,
        experian_id,
        outcome="verified",
        response_date=(today - timedelta(days=5)).isoformat(),
    )

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks",
        headers=manager_headers,
        params={"baseline_days": 90, "recent_days": 30, "group_by": "bureau"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["group_by"] == "bureau"
    bureaus = {item["bureau"]: item for item in body["by_bureau"]}
    assert "equifax" in bureaus
    assert "experian" in bureaus
    assert bureaus["equifax"]["recent"]["counts"]["deleted"] == 1
    assert bureaus["experian"]["recent"]["counts"]["verified"] == 1
    assert "rate_deltas" in bureaus["equifax"]


def test_reinvestigation_outcome_benchmarks_rejects_invalid_group_by(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks",
        headers=manager_headers,
        params={"group_by": "creditor"},
    )
    assert response.status_code == 422


def test_reinvestigation_outcome_benchmarks_rejects_recent_gt_baseline(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks",
        headers=manager_headers,
        params={"baseline_days": 30, "recent_days": 60},
    )
    assert response.status_code == 422


def test_reinvestigation_outcome_benchmarks_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/reporting/reinvestigation-outcomes/benchmarks")
    assert response.status_code == 401


def test_reinvestigation_outcome_benchmarks_csv_export(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today()
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="CSV Bench Bank",
        last_dispute_date=(today - timedelta(days=20)).isoformat(),
    )
    _record_response(
        api_client,
        manager_headers,
        account_id,
        outcome="deleted",
        response_date=(today - timedelta(days=5)).isoformat(),
    )

    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks/export",
        headers=manager_headers,
        params={"format": "csv", "baseline_days": 90, "recent_days": 30},
    )
    assert response.status_code == 200, response.text
    assert "text/csv" in response.headers.get("content-type", "")
    body = response.text
    assert "breakdown_type" in body
    assert "organization" in body
    assert "baseline_deletion_rate" in body
    assert "client_id" not in body.lower()
    assert "account_id" not in body.lower()


def test_reinvestigation_outcome_benchmarks_csv_export_requires_auth(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/reinvestigation-outcomes/benchmarks/export",
        params={"format": "csv"},
    )
    assert response.status_code == 401
