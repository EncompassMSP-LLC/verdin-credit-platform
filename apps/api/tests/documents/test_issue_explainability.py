"""Unit + API tests for case issue explainability (LRP-208)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.modules.documents.issue_explainability import build_issue_explainability_cards
from api.modules.documents.schemas import (
    CaseIssueExplainabilityResponse,
    CaseLitigationStrengthResponse,
    IssueExplainabilitySummary,
    LitigationStrengthIssue,
    LitigationStrengthSummary,
)


def test_build_cards_maps_cross_bureau_dofd_without_score_promises() -> None:
    case_id = uuid.uuid4()
    result = build_issue_explainability_cards(
        case_id=case_id,
        issues=[
            {
                "source_kind": "cross_bureau",
                "source_id": "cross_bureau:capital one:4242:dofd_mismatch",
                "rule_id": "cross_bureau.dofd_mismatch",
                "score": 98,
                "rank": 1,
                "title": "DOFD mismatch",
                "rationale": "TransUnion reports late while others report current.",
                "severity": "high",
                "bureau": None,
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
            }
        ],
    )
    assert result.summary["issues_explained"] == 1
    assert result.summary["strong"] == 1
    card = result.cards[0]
    assert "late" in card.title.lower() or "dofd" in card.title.lower()
    assert "conflicting" in card.why_disputable.lower()
    assert card.finding_strength == "strong"
    assert card.credit_profile_impact == "high"
    assert card.mortgage_readiness_impact == "high"
    assert any("does not estimate point" in outcome.lower() for outcome in card.possible_outcomes)
    assert "42 points" not in " ".join(card.possible_outcomes).lower()
    assert "never guarantees" in result.disclaimer.lower()
    assert card.evidence_recommendations


def test_build_cards_marks_informational_identity_freeze() -> None:
    result = build_issue_explainability_cards(
        case_id=uuid.uuid4(),
        issues=[
            {
                "source_kind": "identity_theft",
                "source_id": "identity_theft:freeze",
                "rule_id": "identity_theft.report.security_freeze",
                "score": 40,
                "rank": 1,
                "title": "Security freeze",
                "rationale": "Report shows a security freeze.",
                "severity": "low",
                "bureau": "experian",
                "creditor_name": None,
                "account_number_masked": None,
            }
        ],
    )
    card = result.cards[0]
    assert card.finding_strength == "informational"
    assert card.credit_profile_impact == "no_score_impact_expected"


def test_get_case_issue_explainability_endpoint(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    strength = CaseLitigationStrengthResponse(
        case_id=uuid.UUID(sample_case_id),
        summary=LitigationStrengthSummary(
            issues_scored=1,
            high_priority=1,
            medium_priority=0,
            low_priority=0,
            top_score=98,
            average_score=98.0,
        ),
        issues=[
            LitigationStrengthIssue(
                source_kind="cross_bureau",
                source_id="cross_bureau:x:dofd",
                rule_id="cross_bureau.dofd_mismatch",
                score=98,
                rank=1,
                title="DOFD mismatch",
                rationale="Conflicting DOFD across bureaus.",
                severity="high",
                bureau=None,
                creditor_name="Capital One",
                account_number_masked="****4242",
                match_key="capital one:4242",
                factors=["dofd_mismatch"],
            )
        ],
    )
    with (
        patch(
            "api.modules.documents.service.DocumentService.get_case_litigation_strength",
            new_callable=AsyncMock,
            return_value=strength,
        ),
        patch(
            "api.modules.documents.service.DocumentService.get_case_compliance_evidence_links",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=404, detail="No evidence"),
        ),
    ):
        response = api_client.get(
            f"/api/v1/cases/{sample_case_id}/issue-explainability",
            headers=manager_headers,
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"] == sample_case_id
    assert body["summary"]["issues_explained"] == 1
    assert len(body["cards"]) == 1
    assert body["cards"][0]["finding_strength"] == "strong"
    assert "point" in body["disclaimer"].lower()
    CaseIssueExplainabilityResponse.model_validate(body)
    IssueExplainabilitySummary.model_validate(body["summary"])
