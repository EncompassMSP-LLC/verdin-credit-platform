"""API tests for lock-aware dispute preparation.

Bulk dispute preparation must *skip* tradelines paused by an identity-theft
indicator or a confirmed §605B claim (recording them under ``locked``) instead
of aborting the whole batch with a 409.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.modules.documents.cross_bureau_comparison import tradeline_match_key
from api.modules.documents.schemas import (
    AccountDisputeStrategyItem,
    CaseCreditReportDiscrepanciesResponse,
    CaseDisputeStrategyResponse,
    CrossBureauComparisonSummary,
    CrossBureauDiscrepancyResponse,
    DisputeStrategyStage,
    DisputeStrategySummary,
)
from tests.helpers.client_payload import sample_client_payload

_CREDITOR = "Fake Bank"
_MASKED = "****9999"


def _create_client(api_client: TestClient, headers: dict[str, str], *, email: str) -> str:
    payload = sample_client_payload(
        display_name=f"Lock Aware {uuid.uuid4().hex[:6]}",
        email=email,
    )
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_case(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    client_name: str,
) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "title": f"Lock aware case {uuid.uuid4().hex[:6]}",
            "client_id": client_id,
            "client_name": client_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _confirm_identity_theft(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
    match_key: str,
) -> None:
    response = api_client.post(
        f"/api/v1/cases/{case_id}/identity-theft/account-reviews",
        headers=headers,
        json={
            "confirmation": "identity_theft",
            "attestation_accepted": True,
            "bureau": "experian",
            "tradeline_index": 0,
            "match_key": match_key,
            "creditor_name": _CREDITOR,
            "account_number_masked": _MASKED,
            "detection_source": "TRADELINE_HEURISTIC",
            "confidence": 0.9,
        },
    )
    assert response.status_code == 201, response.text


def _strategy_with_direct_target(case_id: str) -> CaseDisputeStrategyResponse:
    return CaseDisputeStrategyResponse(
        case_id=uuid.UUID(case_id),
        disclaimer="Staff-mediated planning aid only.",
        summary=DisputeStrategySummary(
            accounts_planned=1,
            issues_covered=1,
            high_strength_accounts=0,
            cfpb_recommended=0,
            attorney_recommended=0,
        ),
        strategies=[
            AccountDisputeStrategyItem(
                account_key="acct:fakebank",
                creditor_name=_CREDITOR,
                account_number_masked=_MASKED,
                bureau="experian",
                match_key=None,
                top_score=90,
                issue_count=1,
                primary_rule_ids=["metro2.closed_with_balance"],
                summary="Closed with balance",
                stages=[
                    DisputeStrategyStage(
                        stage_order=1,
                        stage_kind="cra_dispute",
                        title="CRA dispute",
                        objective="Dispute inaccurate tradeline",
                        rationale="Cross-bureau discrepancy",
                        issue_source_ids=[],
                        evidence_hints=[],
                        recommended=True,
                    )
                ],
            )
        ],
    )


def _discrepancies_with_match(
    case_id: str, match_key: str
) -> CaseCreditReportDiscrepanciesResponse:
    return CaseCreditReportDiscrepanciesResponse(
        case_id=uuid.UUID(case_id),
        reports_compared=["experian", "equifax"],
        document_ids_by_bureau={},
        summary=CrossBureauComparisonSummary(
            total_tradelines=1,
            actionable=1,
            investigation_needed=0,
            dispute_ready=1,
            consistent=0,
            missing_from_bureau=0,
            balance_mismatch=0,
            status_mismatch=0,
        ),
        discrepancies=[
            CrossBureauDiscrepancyResponse(
                match_key=match_key,
                creditor_name=_CREDITOR,
                account_number_masked=_MASKED,
                discrepancy_types=["balance_mismatch"],
                classification="dispute",
                classification_label="Dispute-ready",
                confidence_score=90,
                workflow_tier="dispute",
                bureaus_reporting=["experian", "equifax"],
                bureaus_missing=[],
                bureau_snapshots=[],
                possible_causes=[],
                recommended_next_step="Dispute with bureau",
                recommended_action="File a §611 dispute",
                requires_investigation=False,
                dispute_ready=True,
                is_actionable=True,
            )
        ],
    )


def test_prepare_strategy_stage_skips_identity_theft_locked_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"lock-aware-strategy-{uuid.uuid4().hex[:8]}@test.example"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name="Lock Aware Strategy",
    )
    match_key = tradeline_match_key(_CREDITOR, _MASKED)
    _confirm_identity_theft(api_client, manager_headers, case_id=case_id, match_key=match_key)

    strategy = _strategy_with_direct_target(case_id)
    with patch(
        "api.modules.documents.service.DocumentService._build_case_dispute_strategy_response",
        new_callable=AsyncMock,
        return_value=strategy,
    ):
        response = api_client.post(
            f"/api/v1/cases/{case_id}/dispute-strategy/prepare",
            headers=manager_headers,
            json={"stage_kind": "cra_dispute", "recommended_only": True},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["prepared"] == []
    assert len(body["locked"]) == 1
    locked = body["locked"][0]
    assert locked["match_key"] == "acct:fakebank"
    assert "paused" in locked["reason"].lower()
    assert body["note"] and "identity-theft" in body["note"].lower()


def test_prepare_credit_report_disputes_skips_locked_tradeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"lock-aware-discrepancy-{uuid.uuid4().hex[:8]}@test.example"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name="Lock Aware Discrepancy",
    )
    match_key = tradeline_match_key(_CREDITOR, _MASKED)
    _confirm_identity_theft(api_client, manager_headers, case_id=case_id, match_key=match_key)

    discrepancies = _discrepancies_with_match(case_id, match_key)
    with patch(
        "api.modules.documents.service.DocumentService.get_case_credit_report_discrepancies",
        new_callable=AsyncMock,
        return_value=discrepancies,
    ):
        response = api_client.post(
            f"/api/v1/cases/{case_id}/credit-report-discrepancies/prepare-disputes",
            headers=manager_headers,
            json={},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["prepared"] == []
    assert len(body["locked"]) == 1
    assert body["locked"][0]["match_key"] == match_key
    assert body["locked"][0]["creditor_name"] == _CREDITOR
