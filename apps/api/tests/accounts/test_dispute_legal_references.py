"""Unit tests for best-available FCRA legal reference selection."""

from __future__ import annotations

from api.modules.accounts.dispute_legal_references import (
    LegalCitationCandidate,
    candidates_from_fcra_documents,
    select_best_legal_reference,
)


def test_select_defaults_to_cra_611_without_findings() -> None:
    selected = select_best_legal_reference("credit_bureau", ())
    assert selected.source == "default"
    assert selected.sections == ("611",)
    assert "1681i" in selected.pursuant_clause


def test_select_defaults_to_furnisher_623_without_findings() -> None:
    selected = select_best_legal_reference("furnisher", ())
    assert selected.source == "default"
    assert selected.sections == ("623",)
    assert "1681s-2" in selected.pursuant_clause


def test_select_best_matched_finding_sections() -> None:
    candidates = [
        LegalCitationCandidate(
            rule_id="fcra.collection_missing_original_creditor",
            fcra_sections=("623",),
            score=75,
            matched=True,
        ),
        LegalCitationCandidate(
            rule_id="fcra.obsolete_adverse_info",
            fcra_sections=("605",),
            score=92,
            matched=True,
        ),
        LegalCitationCandidate(
            rule_id="fcra.past_due_exceeds_balance",
            fcra_sections=("607", "623"),
            score=88,
            matched=False,
        ),
    ]
    selected = select_best_legal_reference("credit_bureau", candidates)
    assert selected.source == "finding"
    assert selected.source_rule_id == "fcra.obsolete_adverse_info"
    assert selected.sections[0] == "611"
    assert "605" in selected.sections
    assert "1681c" in selected.pursuant_clause
    assert "1681i" in selected.pursuant_clause


def test_unmatched_findings_do_not_override_default() -> None:
    candidates = [
        LegalCitationCandidate(
            rule_id="fcra.obsolete_adverse_info",
            fcra_sections=("605",),
            score=99,
            matched=False,
        )
    ]
    selected = select_best_legal_reference("credit_bureau", candidates)
    assert selected.source == "default"
    assert selected.sections == ("611",)


def test_candidates_from_fcra_documents_match_tradeline() -> None:
    documents = [
        {
            "bureau": "experian",
            "findings": [
                {
                    "rule_id": "fcra.obsolete_adverse_info",
                    "severity": "high",
                    "fcra_sections": ["605"],
                    "creditor_name": "ACHIEVE PERSONAL LOANS",
                    "account_number_masked": "****1081",
                },
                {
                    "rule_id": "fcra.closed_missing_date_closed",
                    "severity": "medium",
                    "fcra_sections": ["623"],
                    "creditor_name": "OTHER BANK",
                    "account_number_masked": "****9999",
                },
            ],
        }
    ]
    candidates = candidates_from_fcra_documents(
        documents,
        creditor_name="ACHIEVE PERSONAL LOANS",
        account_number_masked="****1081",
        bureau="experian",
    )
    assert len(candidates) == 2
    matched = [c for c in candidates if c.matched]
    assert len(matched) == 1
    assert matched[0].rule_id == "fcra.obsolete_adverse_info"
    assert matched[0].score >= 92

    selected = select_best_legal_reference("credit_bureau", candidates)
    assert selected.source == "finding"
    assert "605" in selected.sections
