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


def test_select_match_keys_for_cra_stage() -> None:
    from api.modules.documents.dispute_strategy import (
        select_accounts_for_stage,
        select_match_keys_for_stage,
        stage_recipient_type,
    )

    result = generate_case_dispute_strategy(
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
            {
                "source_kind": "metro2",
                "source_id": "metro2:b",
                "rule_id": "metro2.date_closed_before_open",
                "score": 95,
                "rank": 2,
                "title": "Impossible dates",
                "severity": "high",
                "bureau": "experian",
                "creditor_name": "Metro Auto",
                "account_number_masked": "****9999",
                "match_key": None,
            },
            {
                "source_kind": "chronology",
                "source_id": "chronology:c",
                "rule_id": "chronology.field_changed",
                "score": 45,
                "rank": 3,
                "title": "remarks",
                "severity": "low",
                "bureau": "experian",
                "creditor_name": "Retail",
                "account_number_masked": "****1111",
                "match_key": "retail:1111",
            },
        ],
    )
    cra_keys = select_match_keys_for_stage(result.strategies, stage_kind="cra_dispute")
    assert "capital one:4242" in cra_keys
    assert "retail:1111" in cra_keys
    assert stage_recipient_type("cra_dispute") == "credit_bureau"
    assert stage_recipient_type("furnisher_dispute") == "furnisher"

    furnisher_keys = select_match_keys_for_stage(
        result.strategies,
        stage_kind="furnisher_dispute",
        recommended_only=True,
    )
    assert "capital one:4242" in furnisher_keys
    assert "retail:1111" not in furnisher_keys

    targets = select_accounts_for_stage(result.strategies, stage_kind="cra_dispute")
    assert any(target.match_key == "capital one:4242" for target in targets)
    direct = [target for target in targets if target.match_key is None]
    assert len(direct) == 1
    assert direct[0].creditor_name == "Metro Auto"
    assert direct[0].account_key.startswith("acct:")


def test_infer_account_metadata_from_rules() -> None:
    from api.modules.documents.dispute_strategy import infer_account_metadata_from_rules

    closed = infer_account_metadata_from_rules(["metro2.date_closed_before_open"])
    assert closed.account_status == "closed"
    assert closed.account_type == "other"

    collection = infer_account_metadata_from_rules(["fcra.collection_missing_original_creditor"])
    assert collection.account_type == "collection"
    assert collection.account_status == "collection"

    past_due = infer_account_metadata_from_rules(["metro2.past_due_without_dofd"])
    assert past_due.payment_status == "late_90"

    charge_off = infer_account_metadata_from_rules(["metro2.charge_off_zero_past_due"])
    assert charge_off.account_status == "charge_off"


def test_resolve_strategy_account_metadata_prefers_tradeline() -> None:
    from api.modules.documents.dispute_strategy import (
        find_matching_tradeline,
        resolve_strategy_account_metadata,
    )

    tradeline = {
        "creditor_name": "Metro Auto",
        "account_number_masked": "****4242",
        "account_type": "Auto Loan",
        "account_status": "Open",
        "payment_status": "30 days late",
    }
    resolved = resolve_strategy_account_metadata(
        ["metro2.date_closed_before_open"],
        tradeline=tradeline,
    )
    assert resolved.account_type == "auto"
    assert resolved.account_status == "open"
    assert resolved.payment_status == "late_30"

    matched = find_matching_tradeline(
        [
            (
                "experian",
                {
                    "accounts": [
                        {
                            "creditor_name": "Other Bank",
                            "account_number_masked": "****0000",
                            "account_type": "Credit Card",
                        },
                        tradeline,
                    ]
                },
            )
        ],
        creditor_name="Metro Auto",
        account_number_masked="****4242",
        bureau="experian",
    )
    assert matched is tradeline


def test_resolve_strategy_account_metadata_falls_back_to_rules() -> None:
    from api.modules.documents.dispute_strategy import resolve_strategy_account_metadata

    resolved = resolve_strategy_account_metadata(
        ["fcra.collection_missing_original_creditor"],
        tradeline={"creditor_name": "Acme", "account_type": None},
    )
    assert resolved.account_type == "collection"
    assert resolved.account_status == "collection"


def test_parse_finding_source_ref_and_indexed_tradeline() -> None:
    from api.modules.documents.dispute_strategy import (
        find_tradeline_by_source_ref,
        parse_finding_source_ref,
        select_accounts_for_stage,
    )

    document_id = uuid.uuid4()
    parsed = parse_finding_source_ref(
        f"metro2:experian:metro2.past_due_without_dofd#1@{document_id}"
    )
    assert parsed is not None
    assert parsed.document_id == document_id
    assert parsed.tradeline_index == 1

    tradeline = {
        "creditor_name": "Metro Auto",
        "account_number_masked": "****4242",
        "account_type": "Auto Loan",
        "account_status": "Open",
        "payment_status": "Current",
    }
    matched = find_tradeline_by_source_ref(
        {
            document_id: {
                "accounts": [
                    {"creditor_name": "Other", "account_type": "Credit Card"},
                    tradeline,
                ]
            }
        },
        document_id=document_id,
        tradeline_index=1,
    )
    assert matched is tradeline

    case_id = uuid.uuid4()
    strategy = generate_case_dispute_strategy(
        case_id=case_id,
        scored_issues=[
            {
                "source_kind": "metro2",
                "source_id": f"metro2:experian:metro2.past_due_without_dofd#1@{document_id}",
                "rule_id": "metro2.past_due_without_dofd",
                "score": 80,
                "rank": 1,
                "title": "Past due",
                "severity": "medium",
                "bureau": "experian",
                "creditor_name": "Metro Auto",
                "account_number_masked": "****4242",
                "match_key": None,
            }
        ],
    )
    targets = select_accounts_for_stage(
        strategy.strategies,
        stage_kind="cra_dispute",
        recommended_only=True,
    )
    assert len(targets) == 1
    assert targets[0].source_document_id == document_id
    assert targets[0].tradeline_index == 1


def test_build_case_cfpb_checklist_for_high_strength_accounts() -> None:
    from api.modules.documents.dispute_strategy import build_case_cfpb_checklist

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
            {
                "source_kind": "chronology",
                "source_id": "chronology:b",
                "rule_id": "chronology.field_changed",
                "score": 45,
                "rank": 2,
                "title": "remarks",
                "severity": "low",
                "bureau": "experian",
                "creditor_name": "Retail",
                "account_number_masked": "****1111",
                "match_key": "retail:1111",
            },
        ],
    )
    checklist = build_case_cfpb_checklist(
        case_id=strategy.case_id,
        strategies=strategy.strategies,
        recommended_only=True,
    )
    assert checklist.summary["accounts_listed"] == 1
    assert checklist.accounts[0].creditor_name == "Capital One"
    assert checklist.accounts[0].top_score >= 95
    assert any(item.item_id == "cfpb_narrative" for item in checklist.accounts[0].items)
    assert checklist.summary["required_items"] >= 1


def test_build_case_attorney_checklist_for_strategy_accounts() -> None:
    from api.modules.documents.dispute_strategy import build_case_attorney_checklist

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
            {
                "source_kind": "chronology",
                "source_id": "chronology:b",
                "rule_id": "chronology.field_changed",
                "score": 45,
                "rank": 2,
                "title": "remarks",
                "severity": "low",
                "bureau": "experian",
                "creditor_name": "Retail",
                "account_number_masked": "****1111",
                "match_key": "retail:1111",
            },
        ],
    )
    checklist = build_case_attorney_checklist(
        case_id=strategy.case_id,
        strategies=strategy.strategies,
        recommended_only=True,
    )
    # attorney_preserve is always recommended hygiene → both accounts listed
    assert checklist.summary["accounts_listed"] == 2
    assert checklist.accounts[0].creditor_name == "Capital One"
    assert checklist.accounts[0].attorney_escalation is True
    assert any(item.item_id == "attorney_handoff_narrative" for item in checklist.accounts[0].items)
    assert checklist.summary["escalation_flagged"] >= 1
    assert checklist.summary["required_items"] >= 1


def test_enrich_checklist_completion_against_evidence_snapshot() -> None:
    from api.modules.documents.dispute_strategy import (
        ChecklistEvidenceSnapshot,
        LetterSignal,
        build_case_attorney_checklist,
        build_case_cfpb_checklist,
        enrich_case_attorney_checklist,
        enrich_case_cfpb_checklist,
    )

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
        has_identity=True,
        has_proof_of_address=True,
        has_credit_report_doc=True,
        has_bureau_response_doc=False,
        has_parsed_credit_report=True,
        letters_by_match_key={
            "capital one:4242": (LetterSignal(recipient_type="credit_bureau", status="draft"),),
        },
        response_received_by_match_key={},
    )
    cfpb = enrich_case_cfpb_checklist(
        build_case_cfpb_checklist(
            case_id=strategy.case_id,
            strategies=strategy.strategies,
            recommended_only=True,
        ),
        evidence,
    )
    by_id = {item.item_id: item.completion_status for item in cfpb.accounts[0].items}
    assert by_id["identity_exhibits"] == "present"
    assert by_id["report_excerpts"] == "present"
    assert by_id["cra_dispute_packet"] == "present"
    assert by_id["cra_responses"] == "missing"
    assert by_id["cfpb_narrative"] == "unknown"
    assert cfpb.summary["items_present"] >= 1

    attorney = enrich_case_attorney_checklist(
        build_case_attorney_checklist(
            case_id=strategy.case_id,
            strategies=strategy.strategies,
            recommended_only=True,
        ),
        evidence,
    )
    attorney_by_id = {item.item_id: item.completion_status for item in attorney.accounts[0].items}
    assert attorney_by_id["dispute_correspondence_chain"] == "present"
    assert attorney_by_id["attorney_handoff_narrative"] == "unknown"
    assert attorney_by_id["litigation_escalation_flag"] == "present"
