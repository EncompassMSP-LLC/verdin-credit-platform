"""Unit tests for Identity Theft Detection & Recovery Engine."""

from __future__ import annotations

import uuid

from api.modules.documents.identity_theft_rules import (
    assess_fcra_605b_readiness,
    classification_payload,
    evaluate_identity_theft,
)


def test_evaluate_detects_report_level_fraud_alert_and_banner() -> None:
    result = evaluate_identity_theft(
        document_id=uuid.uuid4(),
        bureau="experian",
        parsed_report={
            "schema_version": "1.1",
            "consumer": {"name": "Test Consumer"},
            "personal_information": [
                {"field_name": "consumer_statement", "value": "Initial fraud alert is on file"}
            ],
            "accounts": [
                {
                    "creditor_name": "Some Bank",
                    "account_number_masked": "****1111",
                    "account_status": "Open",
                    "payment_status": "Current",
                }
            ],
        },
    )
    rule_ids = {f.rule_id for f in result.findings}
    assert "identity_theft.report.fraud_alert" in rule_ids or (
        "identity_theft.report.initial_fraud_alert" in rule_ids
    )
    assert result.banner_active is True
    assert result.banner_title is not None
    assert result.ordinary_dispute_locked is True
    finding = result.findings[0]
    assert finding.consumer_confirmed is False
    assert finding.issue_type == "IDENTITY_THEFT_INDICATOR"
    payload = classification_payload(finding)
    assert payload["ordinaryDisputeLocked"] is True
    assert payload["requiredAction"] == "CONSUMER_REVIEW"
    assert payload["legalPath"] is None


def test_evaluate_tradeline_denial_and_open_before_age() -> None:
    result = evaluate_identity_theft(
        document_id=uuid.uuid4(),
        bureau="equifax",
        parsed_report={
            "consumer": {"date_of_birth": "01/15/2005"},
            "accounts": [
                {
                    "creditor_name": "Mystery Collections",
                    "account_number_masked": "****9999",
                    "account_status": "Collection",
                    "remarks": "Consumer states I did not open this account",
                    "open_date": "06/01/2018",
                    "date_reported": "06/01/2024",
                }
            ],
        },
    )
    rule_ids = {f.rule_id for f in result.findings}
    assert "identity_theft.tradeline.consumer_denies_account" in rule_ids
    assert "identity_theft.tradeline.open_before_plausible_age" in rule_ids
    for finding in result.findings:
        if finding.tradeline_index == 0:
            assert finding.ordinary_dispute_locked is True
            assert finding.detection_source == "TRADELINE_HEURISTIC"


def test_evaluate_inquiry_burst() -> None:
    result = evaluate_identity_theft(
        document_id=uuid.uuid4(),
        bureau="transunion",
        parsed_report={
            "accounts": [],
            "inquiries": [
                {"creditor_name": "A", "inquiry_date": "01/01/2024"},
                {"creditor_name": "B", "inquiry_date": "01/05/2024"},
                {"creditor_name": "C", "inquiry_date": "01/10/2024"},
                {"creditor_name": "D", "inquiry_date": "01/15/2024"},
            ],
        },
    )
    assert any(f.rule_id == "identity_theft.report.inquiry_burst" for f in result.findings)


def test_assess_fcra_605b_readiness() -> None:
    readiness = assess_fcra_605b_readiness(
        has_proof_of_identity=True,
        has_identity_theft_report=True,
        has_identified_fraudulent_info=True,
        has_consumer_statement=True,
        has_proof_of_address=False,
        has_supporting_creditor_records=None,
    )
    assert readiness.remedy_type.startswith("FCRA §605B")
    assert readiness.not_ordinary_dispute is True
    assert readiness.packet_readiness >= 80
    assert "PROOF_OF_ADDRESS" in readiness.missing_evidence
    required_present = [i for i in readiness.items if i.required and i.status == "present"]
    assert len(required_present) == 4
