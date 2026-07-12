"""Unit tests for dispute strategy generation."""

from __future__ import annotations

import uuid

from api.modules.documents.dispute_strategy import generate_case_dispute_strategy


def test_strategy_recommends_cfpb_for_high_dofd_mismatch() -> None:
    case_id = uuid.uuid4()
    result = generate_case_dispute_strategy(
        case_id=case_id,
        scored_issues=[
            {
                "source_kind": "cross_bureau",
                "source_id": "cross_bureau:capital one:4242:dofd_mismatch",
                "rule_id": "cross_bureau.dofd_mismatch",
                "score": 98,
                "rank": 1,
                "title": "DOFD mismatch",
                "severity": "high",
                "bureau": None,
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "match_key": "capital one:4242",
            }
        ],
        evidence_hints_by_source_id={
            "cross_bureau:capital one:4242:dofd_mismatch": [
                "Attach both bureau report excerpts",
            ]
        },
    )

    assert result.summary["accounts_planned"] == 1
    assert result.summary["cfpb_recommended"] == 1
    strategy = result.strategies[0]
    assert strategy.creditor_name == "Capital One"
    assert strategy.top_score == 98
    kinds = [stage.stage_kind for stage in strategy.stages]
    assert kinds == [
        "cra_dispute",
        "furnisher_dispute",
        "cfpb_escalation",
        "attorney_preserve",
    ]
    by_kind = {stage.stage_kind: stage for stage in strategy.stages}
    assert by_kind["cra_dispute"].recommended is True
    assert by_kind["furnisher_dispute"].recommended is True
    assert by_kind["cfpb_escalation"].recommended is True
    assert by_kind["attorney_preserve"].recommended is True
    assert "Attach both bureau report excerpts" in by_kind["cra_dispute"].evidence_hints


def test_strategy_skips_cfpb_for_low_cosmetic_issue() -> None:
    result = generate_case_dispute_strategy(
        case_id=uuid.uuid4(),
        scored_issues=[
            {
                "source_kind": "chronology",
                "source_id": "chronology:experian:retail:field_changed",
                "rule_id": "chronology.field_changed",
                "score": 45,
                "rank": 1,
                "title": "remarks changed",
                "severity": "low",
                "bureau": "experian",
                "creditor_name": "Retail Card",
                "account_number_masked": "****1111",
                "match_key": "retail card:1111",
            }
        ],
    )
    by_kind = {stage.stage_kind: stage for stage in result.strategies[0].stages}
    assert by_kind["cra_dispute"].recommended is True
    assert by_kind["cfpb_escalation"].recommended is False
    assert result.summary["cfpb_recommended"] == 0
    assert result.summary["attorney_recommended"] == 1


def test_strategy_groups_issues_by_match_key() -> None:
    result = generate_case_dispute_strategy(
        case_id=uuid.uuid4(),
        scored_issues=[
            {
                "source_kind": "metro2",
                "source_id": "metro2:a",
                "rule_id": "metro2.closed_with_balance",
                "score": 88,
                "rank": 1,
                "title": "Closed with balance",
                "severity": "high",
                "bureau": "experian",
                "creditor_name": "Bank A",
                "account_number_masked": "****2222",
                "match_key": "bank a:2222",
            },
            {
                "source_kind": "fcra",
                "source_id": "fcra:b",
                "rule_id": "fcra.adverse_missing_dofd",
                "score": 85,
                "rank": 2,
                "title": "Missing DOFD",
                "severity": "high",
                "bureau": "equifax",
                "creditor_name": "Bank A",
                "account_number_masked": "****2222",
                "match_key": "bank a:2222",
            },
            {
                "source_kind": "metro2",
                "source_id": "metro2:c",
                "rule_id": "metro2.balance_exceeds_high_credit",
                "score": 70,
                "rank": 3,
                "title": "Balance high",
                "severity": "medium",
                "bureau": "transunion",
                "creditor_name": "Other",
                "account_number_masked": "****3333",
                "match_key": "other:3333",
            },
        ],
    )
    assert result.summary["accounts_planned"] == 2
    assert result.strategies[0].issue_count == 2
    assert result.strategies[0].top_score == 88
    assert result.strategies[1].issue_count == 1
