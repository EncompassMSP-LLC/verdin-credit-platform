"""Unit tests for checklist staff override merge."""

from __future__ import annotations

import uuid

from api.modules.documents.dispute_strategy import (
    ChecklistEvidenceSnapshot,
    ChecklistOverrideValue,
    apply_checklist_overrides,
    build_case_cfpb_checklist,
    enrich_case_cfpb_checklist,
    generate_case_dispute_strategy,
)


def test_apply_checklist_overrides_marks_staff_source() -> None:
    strategy = generate_case_dispute_strategy(
        case_id=uuid.uuid4(),
        scored_issues=[
            {
                "source_kind": "cross_bureau",
                "source_id": "cross_bureau:a",
                "rule_id": "cross_bureau.dofd_mismatch",
                "score": 98,
                "rank": 1,
                "title": "DOFD mismatch",
                "severity": "high",
                "bureau": None,
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "match_key": "capital one:4242",
            },
        ],
    )
    evidence = ChecklistEvidenceSnapshot(
        has_identity=False,
        has_proof_of_address=False,
        has_credit_report_doc=False,
        has_bureau_response_doc=False,
        has_parsed_credit_report=False,
        letters_by_match_key={},
        response_received_by_match_key={},
    )
    checklist = enrich_case_cfpb_checklist(
        build_case_cfpb_checklist(
            case_id=strategy.case_id,
            strategies=strategy.strategies,
            recommended_only=True,
        ),
        evidence,
    )
    account_key = checklist.accounts[0].account_key
    identity = next(
        item for item in checklist.accounts[0].items if item.item_id == "identity_exhibits"
    )
    assert identity.completion_status == "missing"
    assert identity.completion_source == "computed"

    overridden = apply_checklist_overrides(
        checklist,
        {
            (account_key, "identity_exhibits"): ChecklistOverrideValue(
                completion_status="present",
                note="Verified ID packet on desk",
            )
        },
    )
    assert overridden.accounts[0].account_key == account_key
    by_id = {item.item_id: item for item in overridden.accounts[0].items}
    assert by_id["identity_exhibits"].completion_status == "present"
    assert by_id["identity_exhibits"].completion_source == "staff"
    assert by_id["identity_exhibits"].override_note == "Verified ID packet on desk"
    assert overridden.summary["items_present"] >= 1
