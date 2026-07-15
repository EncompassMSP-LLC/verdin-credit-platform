"""Tests for cross-bureau discrepancy evidence in the litigation packet (Phase 12 slice 4)."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from api.modules.accounts.cross_bureau import (
    BureauTradelineView,
    detect_cross_bureau_discrepancies,
)
from api.modules.accounts.litigation_packet import (
    LitigationReadinessInputs,
    build_litigation_readiness,
)
from tests.accounts.conftest import sample_account_payload


def _view(bureau: str, **overrides: object) -> BureauTradelineView:
    base: dict[str, object] = {
        "account_id": bureau,
        "bureau": bureau,
        "latest_outcome": None,
        "dispute_status": None,
        "account_status": None,
        "payment_status": None,
        "balance": None,
    }
    base.update(overrides)
    return BureauTradelineView(**base)  # type: ignore[arg-type]


def test_detect_outcome_conflict_across_bureaus() -> None:
    target = _view("experian", latest_outcome="verified")
    sibling = _view("equifax", latest_outcome="deleted")
    evidence = detect_cross_bureau_discrepancies(target, [sibling])
    assert evidence.has_outcome_conflict is True
    assert evidence.compared_bureaus == ["equifax"]
    kinds = {d.kind for d in evidence.discrepancies}
    assert "outcome_conflict" in kinds


def test_detect_no_conflict_when_outcomes_agree() -> None:
    target = _view("experian", latest_outcome="verified")
    sibling = _view("equifax", latest_outcome="verified")
    evidence = detect_cross_bureau_discrepancies(target, [sibling])
    assert evidence.has_outcome_conflict is False
    assert evidence.conflict_count == 0


def test_detect_balance_and_status_conflicts() -> None:
    target = _view(
        "experian",
        dispute_status="verified",
        account_status="open",
        balance=Decimal("1500.00"),
    )
    sibling = _view(
        "equifax",
        dispute_status="deleted",
        account_status="closed",
        balance=Decimal("900.00"),
    )
    evidence = detect_cross_bureau_discrepancies(target, [sibling])
    kinds = {d.kind for d in evidence.discrepancies}
    assert "dispute_status_conflict" in kinds
    assert "account_status_conflict" in kinds
    assert "balance_conflict" in kinds


def test_detect_empty_when_no_siblings() -> None:
    evidence = detect_cross_bureau_discrepancies(_view("experian"), [])
    assert evidence.conflict_count == 0
    assert evidence.compared_bureaus == []


def test_readiness_folds_outcome_conflict() -> None:
    inputs = LitigationReadinessInputs(
        clock_state="responded",
        latest_outcome="verified",
        dispute_round=1,
        risk_score=None,
        sent_letter_count=1,
        response_count=1,
        cross_bureau_conflicts=2,
        cross_bureau_outcome_conflict=True,
    )
    readiness = build_litigation_readiness(inputs)
    # verified (20) + cross-bureau outcome conflict (25) = 45 → moderate.
    assert readiness.score == 45
    assert readiness.strength == "moderate"
    assert any("inconsistently across bureaus" in i for i in readiness.indicators)


def test_readiness_folds_minor_cross_bureau_conflict() -> None:
    inputs = LitigationReadinessInputs(
        clock_state="responded",
        latest_outcome="verified",
        dispute_round=1,
        risk_score=None,
        sent_letter_count=1,
        response_count=1,
        cross_bureau_conflicts=1,
        cross_bureau_outcome_conflict=False,
    )
    readiness = build_litigation_readiness(inputs)
    # verified (20) + divergent data (10) = 30 → moderate.
    assert readiness.score == 30
    assert any("divergent data across bureaus" in i for i in readiness.indicators)


def _create_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    creditor_name: str,
    bureau: str,
    last_dispute_date: str,
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    payload["bureau"] = bureau
    payload["last_dispute_date"] = last_dispute_date
    create = api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    assert create.status_code == 201, create.text
    return create.json()["id"]


def _record_response(
    api_client: TestClient,
    manager_headers: dict[str, str],
    account_id: str,
    outcome: str,
) -> None:
    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": outcome, "response_method": "mail"},
    )
    assert record.status_code == 201, record.text


def test_litigation_packet_surfaces_cross_bureau_outcome_conflict(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    today = date.today().isoformat()
    experian_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Cross Bureau Bank",
        bureau="experian",
        last_dispute_date=today,
    )
    equifax_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Cross Bureau Bank",
        bureau="equifax",
        last_dispute_date=today,
    )
    # Same tradeline: verified at Experian, deleted at Equifax → willful-noncompliance signal.
    _record_response(api_client, manager_headers, experian_id, "verified")
    _record_response(api_client, manager_headers, equifax_id, "deleted")

    packet = api_client.get(
        f"/api/v1/accounts/{experian_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    body = packet.json()
    cross_bureau = body["cross_bureau"]
    assert "equifax" in cross_bureau["compared_bureaus"]
    kinds = {d["kind"] for d in cross_bureau["discrepancies"]}
    assert "outcome_conflict" in kinds
    assert any(
        "inconsistently across bureaus" in indicator
        for indicator in body["assessment"]["indicators"]
    )
    assert body["assessment"]["eligible"] is True


def test_litigation_packet_no_cross_bureau_conflict_when_single_bureau(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Solo Bureau Bank",
        bureau="transunion",
        last_dispute_date=date.today().isoformat(),
    )
    _record_response(api_client, manager_headers, account_id, "verified")

    packet = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    body = packet.json()
    assert body["cross_bureau"]["compared_bureaus"] == []
    assert body["cross_bureau"]["discrepancies"] == []
