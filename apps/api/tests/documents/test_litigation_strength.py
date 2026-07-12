"""Unit tests for litigation strength scoring."""

from __future__ import annotations

import uuid

from api.modules.documents.litigation_strength import score_case_litigation_strength


def test_score_ranks_cross_bureau_dofd_above_cosmetic_chronology() -> None:
    case_id = uuid.uuid4()
    document_id = uuid.uuid4()
    result = score_case_litigation_strength(
        case_id=case_id,
        metro2_documents=[
            {
                "document_id": document_id,
                "bureau": "experian",
                "findings": [
                    {
                        "rule_id": "metro2.balance_exceeds_high_credit",
                        "severity": "medium",
                        "title": "Balance exceeds high credit",
                        "tradeline_index": 0,
                        "creditor_name": "Retail Card",
                        "account_number_masked": "****1111",
                    }
                ],
            }
        ],
        fcra_documents=[],
        discrepancies=[
            {
                "match_key": "capital one:4242",
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "discrepancy_types": ["dofd_mismatch"],
                "classification_label": "DOFD mismatch",
                "bureaus_reporting": ["experian", "equifax"],
            }
        ],
        chronology_events=[
            {
                "event_type": "field_changed",
                "severity": "low",
                "summary": "remarks changed",
                "match_key": "retail card:1111",
                "bureau": "experian",
                "creditor_name": "Retail Card",
                "account_number_masked": "****1111",
                "to_document_id": document_id,
            }
        ],
    )

    assert result.summary["issues_scored"] == 3
    assert result.issues[0].rank == 1
    assert result.issues[0].rule_id == "cross_bureau.dofd_mismatch"
    assert result.issues[0].score >= 95
    assert result.issues[-1].rule_id == "chronology.field_changed"
    assert result.issues[0].score > result.issues[-1].score


def test_score_applies_severity_bonus_for_high_metro2() -> None:
    result = score_case_litigation_strength(
        case_id=uuid.uuid4(),
        metro2_documents=[
            {
                "document_id": uuid.uuid4(),
                "bureau": "equifax",
                "findings": [
                    {
                        "rule_id": "metro2.date_closed_before_open",
                        "severity": "high",
                        "title": "Impossible dates",
                        "tradeline_index": 2,
                        "creditor_name": "Metro Auto",
                        "account_number_masked": "****9999",
                    }
                ],
            }
        ],
        fcra_documents=[],
        discrepancies=[],
        chronology_events=[],
    )
    assert result.issues[0].score == 100  # 95 base + 5 high severity, clamped
    assert result.summary["high_priority"] == 1
