"""Unit + API tests for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from api.modules.accounts.letter_draft_builder_engine import (
    build_letter_draft,
    validate_draft_text,
)


def test_build_bureau_dispute_uses_best_legal_pursuant() -> None:
    case_id = uuid.uuid4()
    built = build_letter_draft(
        template_kind="bureau_dispute",
        client_name="Pat Borrower",
        case_id=case_id,
        issue_title="Obsolete adverse info",
        what_we_found="Adverse item appears past the reporting period.",
        why_disputable="Obsolescence may require deletion under FCRA §605.",
        creditor_name="Example Bank",
        account_number_masked="****1234",
        bureau="experian",
        issue_source_id="src-1",
        issue_rule_id="fcra.obsolete_adverse_info",
        legal_pursuant="15 U.S.C. § 1681i (FCRA Section 611) and 15 U.S.C. § 1681c (FCRA Section 605)",
        legal_citations=[
            "15 U.S.C. § 1681i (FCRA Section 611)",
            "15 U.S.C. § 1681c (FCRA Section 605)",
        ],
        legal_reference_rule_id="fcra.obsolete_adverse_info",
        legal_alternatives_summary=[
            "Compared `fcra.past_due_exceeds_balance` — accuracy path.",
        ],
    )
    legal = next(s for s in built["sections"] if s["key"] == "legal_references")
    assert "1681c" in legal["body"]
    assert "fcra.obsolete_adverse_info" in legal["body"]
    assert "not legal advice" in legal["body"].lower()


def test_build_bureau_dispute_is_claim_safe() -> None:
    case_id = uuid.uuid4()
    built = build_letter_draft(
        template_kind="bureau_dispute",
        client_name="Pat Borrower",
        case_id=case_id,
        issue_title="Incorrect late payment",
        what_we_found="Tradeline shows a late payment that may not match payment records.",
        why_disputable="Accuracy of payment history may be disputable.",
        creditor_name="Example Bank",
        account_number_masked="****1234",
        bureau="experian",
        issue_source_id="src-1",
        issue_rule_id="metro2.late_payment",
    )
    assert built["workflow_status"] == "ai_draft_created"
    assert built["send_guardrails"]["auto_transmit"] is False
    assert built["send_guardrails"]["transmission_blocked"] is True
    assert built["validation"]["ok"] is True
    assert any(s["key"] == "issue" for s in built["sections"])
    assert "score" not in built["full_text"].lower() or "never" in built["disclaimer"].lower()


def test_validate_blocks_score_guarantee_language() -> None:
    result = validate_draft_text(
        "We guarantee your score will increase by 50 points.",
        sections=[],
        template_kind="bureau_dispute",
    )
    assert result["ok"] is False
    assert any(f["code"] == "score_guarantee" for f in result["findings"])


def test_pay_for_delete_requires_not_guaranteed_disclaimer() -> None:
    case_id = uuid.uuid4()
    built = build_letter_draft(
        template_kind="pay_for_delete",
        client_name="Pat Borrower",
        case_id=case_id,
    )
    assert built["validation"]["ok"] is True
    assert "not guaranteed" in built["full_text"].lower()

    bad = validate_draft_text(
        "Please delete this account after payment.",
        sections=built["sections"],
        template_kind="pay_for_delete",
    )
    assert bad["ok"] is False
    assert any(f["code"] == "pay_for_delete_disclaimer_missing" for f in bad["findings"])


def test_create_list_and_advance_letter_draft(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/letter-drafts",
        headers=manager_headers,
        json={"template_kind": "bureau_dispute"},
    )
    assert create.status_code == 201, create.text
    draft = create.json()
    assert draft["workflow_status"] == "ai_draft_created"
    assert draft["send_guardrails"]["auto_transmit"] is False
    draft_id = draft["id"]

    listed = api_client.get(
        f"/api/v1/cases/{sample_case_id}/letter-drafts",
        headers=manager_headers,
    )
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert any(item["id"] == draft_id for item in body["items"])
    assert any(t["kind"] == "bureau_dispute" for t in body["templates"])

    patched = api_client.patch(
        f"/api/v1/cases/{sample_case_id}/letter-drafts/{draft_id}/sections/issue",
        headers=manager_headers,
        json={
            "body": "Updated issue description from staff review.",
            "fact_classification": "staff_observation",
        },
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["version"] == 2
    assert "Updated issue description" in patched.json()["full_text"]

    advanced = api_client.post(
        f"/api/v1/cases/{sample_case_id}/letter-drafts/{draft_id}/advance",
        headers=manager_headers,
        json={"target_status": "staff_review"},
    )
    assert advanced.status_code == 200, advanced.text
    assert advanced.json()["workflow_status"] == "staff_review"

    # Cannot jump to sent via advance
    blocked = api_client.post(
        f"/api/v1/cases/{sample_case_id}/letter-drafts/{draft_id}/advance",
        headers=manager_headers,
        json={"target_status": "sent_recorded"},
    )
    assert blocked.status_code == 400


def test_mark_sent_requires_ready_to_send(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/letter-drafts",
        headers=manager_headers,
        json={"template_kind": "goodwill"},
    )
    assert create.status_code == 201, create.text
    draft_id = create.json()["id"]

    early = api_client.post(
        f"/api/v1/cases/{sample_case_id}/letter-drafts/{draft_id}/mark-sent",
        headers=manager_headers,
        json={"note": "mailed"},
    )
    assert early.status_code == 400
