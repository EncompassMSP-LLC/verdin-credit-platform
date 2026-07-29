"""Deterministic Intelligent Letter Draft Builder engine (LRP-406).

Generates claim-safe, sectioned drafts with fact classifications and validation.
Never invents facts, never auto-transmits, never promises score increases.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from api.modules.accounts.letter_draft_builder_catalog import (
    DISCLAIMER,
    SEND_GUARDRAILS,
    FactClassification,
    LetterSectionKey,
    LetterTemplateKind,
    get_template,
)

PROHIBITED_CLAIM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "score_guarantee",
        re.compile(
            r"(?<!\bnever\s)(?<!\bnot\s)\b("
            r"guarantee[sd]?\s+(?:your\s+)?score|"
            r"promise[sd]?\s+(?:your\s+)?score|"
            r"will\s+increase|"
            r"points?\s+increase|"
            r"raise\s+your\s+score|"
            r"boost\s+your\s+score|"
            r"\+\s*\d+\s*points?"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "auto_removal",
        re.compile(
            r"(?<!\bnever\s)(?<!\bnot\s)\b("
            r"will\s+be\s+removed|"
            r"guaranteed\s+deletion|"
            r"automatic(?:ally)?\s+delete"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "approval_prediction",
        re.compile(
            r"(?<!\bnever\s)(?<!\bnot\s)\b("
            r"guarantee[sd]?\s+(?:loan|mortgage|approval)|"
            r"will\s+be\s+approved|"
            r"funding\s+is\s+certain"
            r")\b",
            re.IGNORECASE,
        ),
    ),
)

WORKFLOW_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "ai_draft_created": ("staff_review",),
    "staff_review": ("client_review", "ai_draft_created", "approved"),
    "client_review": ("staff_review", "approved"),
    "approved": ("ready_to_send", "staff_review"),
    "ready_to_send": ("sent_recorded", "staff_review"),
    "sent_recorded": ("delivery_confirmed", "response_received"),
    "delivery_confirmed": ("response_received",),
    "response_received": (),
}

# Statuses that imply external transmission happened — only via explicit staff mark.
TRANSMISSION_STATUSES = frozenset({"sent_recorded", "delivery_confirmed", "response_received"})


def _section(
    key: LetterSectionKey,
    heading: str,
    body: str,
    *,
    fact_classification: FactClassification,
    evidence_refs: list[dict[str, Any]] | None = None,
    editable: bool = True,
) -> dict[str, Any]:
    return {
        "key": key,
        "heading": heading,
        "body": body.strip(),
        "fact_classification": fact_classification,
        "evidence_refs": evidence_refs or [],
        "editable": editable,
    }


def build_letter_draft(
    *,
    template_kind: LetterTemplateKind,
    client_name: str,
    case_id: UUID,
    issue_title: str | None = None,
    what_we_found: str | None = None,
    why_disputable: str | None = None,
    creditor_name: str | None = None,
    account_number_masked: str | None = None,
    bureau: str | None = None,
    issue_source_id: str | None = None,
    issue_rule_id: str | None = None,
    evidence_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    template = get_template(template_kind)
    refs = list(evidence_refs or [])
    if issue_source_id:
        refs.append(
            {
                "kind": "issue_explainability",
                "source_id": issue_source_id,
                "rule_id": issue_rule_id,
            }
        )

    account_bits = []
    if creditor_name:
        account_bits.append(f"Creditor/furnisher: {creditor_name}.")
    if account_number_masked:
        account_bits.append(f"Account reference: {account_number_masked}.")
    if bureau:
        account_bits.append(f"Bureau context: {bureau}.")
    account_summary = (
        " ".join(account_bits)
        if account_bits
        else "Account details should be confirmed by staff from the case file before sending."
    )

    issue_parts = []
    if issue_title:
        issue_parts.append(f"Issue: {issue_title}.")
    if what_we_found:
        issue_parts.append(f"What we found: {what_we_found}")
    if why_disputable:
        issue_parts.append(f"Why this may be disputable: {why_disputable}")
    if not issue_parts:
        issue_parts.append(
            "Staff should describe the specific inaccuracy or request using verified case facts only."
        )
    issue_body = " ".join(issue_parts)

    legal = (
        "This draft references generally applicable consumer credit reporting concepts "
        "(including accuracy and reinvestigation expectations under the FCRA where applicable). "
        "Staff must confirm which statutory citations apply before transmission."
    )

    resolution_by_kind: dict[str, str] = {
        "bureau_dispute": (
            "Please investigate the reported information and correct or delete any "
            "inaccurate or unverifiable items. Please provide the results of your investigation."
        ),
        "furnisher_dispute": (
            "Please investigate the accuracy of the information you are furnishing and "
            "update or correct any inaccurate reporting with all consumer reporting agencies."
        ),
        "method_of_verification": (
            "Please describe the method of verification used for the disputed information "
            "and identify the source of that verification."
        ),
        "cfpb_complaint": (
            "We request that the company investigate and correct inaccurate reporting "
            "and provide a written response. This draft is for staff review before any CFPB filing."
        ),
        "ftc_identity_theft": (
            "Please treat this as an identity-theft related recovery narrative draft for "
            "staff/client review. Do not submit automatically to FTC IdentityTheft.gov."
        ),
        "debt_validation": (
            "Please provide validation of this alleged debt, including the amount, original "
            "creditor, and documentation supporting the claim."
        ),
        "goodwill": (
            "We respectfully request a goodwill adjustment regarding the reported late payment "
            "as a courtesy. We understand any decision is discretionary and not guaranteed."
        ),
        "late_payment_forgiveness": (
            "We request consideration of correcting or removing the late-payment notation "
            "based on the facts in the case file. No outcome is guaranteed."
        ),
        "pay_for_delete": (
            "We request that, upon payment as discussed, the account reporting be deleted. "
            "This is a request only; deletion is not guaranteed and many furnishers decline."
        ),
        "communication_preference": (
            "Please honor the client's stated communication preferences and contact channels "
            "as documented in the case file."
        ),
        "cease_communication": (
            "Please cease further communication with the client regarding this account, "
            "except as permitted by applicable law."
        ),
        "mortgage_explanation": (
            "This letter explains dispute or readiness context for underwriting review. "
            "It does not predict mortgage approval, pricing, or funding."
        ),
        "custom_staff": (
            "Staff should specify the requested resolution using verified facts only."
        ),
    }

    section_builders: dict[LetterSectionKey, dict[str, Any]] = {
        "introduction": _section(
            "introduction",
            "Introduction",
            (
                f"Re: Consumer credit matter for {client_name} "
                f"(case reference {case_id}). "
                f"This letter concerns: {template.title}."
            ),
            fact_classification="staff_observation",
            evidence_refs=refs[:1],
        ),
        "account_summary": _section(
            "account_summary",
            "Account summary",
            account_summary,
            fact_classification="document_supported" if account_bits else "staff_observation",
            evidence_refs=refs,
        ),
        "issue": _section(
            "issue",
            "Issue description",
            issue_body,
            fact_classification="document_supported" if what_we_found else "staff_observation",
            evidence_refs=refs,
        ),
        "legal_references": _section(
            "legal_references",
            "Legal / policy references",
            legal,
            fact_classification="staff_observation",
        ),
        "requested_resolution": _section(
            "requested_resolution",
            "Requested resolution",
            resolution_by_kind[template_kind],
            fact_classification="staff_observation",
        ),
        "attachments": _section(
            "attachments",
            "Attachments / evidence checklist",
            (
                "Attach only documents already in the case evidence vault or otherwise "
                "verified by staff. Do not invent supporting exhibits."
                + (f" Linked issue source: {issue_source_id}." if issue_source_id else "")
            ),
            fact_classification="document_supported" if issue_source_id else "staff_observation",
            evidence_refs=refs,
        ),
        "closing": _section(
            "closing",
            "Closing",
            (
                "Thank you for your prompt attention. Please respond in writing. "
                "This draft requires staff review and client approval before transmission."
            ),
            fact_classification="staff_observation",
        ),
    }

    sections = [section_builders[key] for key in template.default_sections]
    composed = compose_full_text(sections)
    validation = validate_draft_text(composed, sections=sections, template_kind=template_kind)

    return {
        "template_kind": template_kind,
        "template_title": template.title,
        "template_description": template.description,
        "claim_warnings": list(template.claim_warnings),
        "sections": sections,
        "full_text": composed,
        "validation": validation,
        "disclaimer": DISCLAIMER,
        "send_guardrails": dict(SEND_GUARDRAILS),
        "workflow_status": "ai_draft_created",
        "version": 1,
    }


def compose_full_text(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        heading = str(section.get("heading") or section.get("key") or "Section")
        body = str(section.get("body") or "").strip()
        parts.append(f"{heading}\n{body}")
    return "\n\n".join(parts).strip()


def validate_draft_text(
    full_text: str,
    *,
    sections: list[dict[str, Any]] | None = None,
    template_kind: LetterTemplateKind | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    lowered = full_text or ""

    for code, pattern in PROHIBITED_CLAIM_PATTERNS:
        if pattern.search(lowered):
            findings.append(
                {
                    "code": code,
                    "severity": "blocking",
                    "message": f"Prohibited claim language detected ({code}). Remove before approval.",
                }
            )

    empty_sections = [
        str(s.get("key")) for s in (sections or []) if not str(s.get("body") or "").strip()
    ]
    if empty_sections:
        findings.append(
            {
                "code": "empty_sections",
                "severity": "warning",
                "message": f"Empty sections: {', '.join(empty_sections)}",
            }
        )

    unsupported = [
        str(s.get("key"))
        for s in (sections or [])
        if s.get("fact_classification") == "client_statement"
        and not (s.get("evidence_refs") or [])
        and str(s.get("key")) in {"issue", "account_summary"}
    ]
    if unsupported:
        findings.append(
            {
                "code": "unsupported_client_statement",
                "severity": "warning",
                "message": (
                    "Client-statement sections lack evidence refs: " + ", ".join(unsupported)
                ),
            }
        )

    if template_kind == "pay_for_delete" and "not guaranteed" not in lowered.lower():
        findings.append(
            {
                "code": "pay_for_delete_disclaimer_missing",
                "severity": "blocking",
                "message": "Pay-for-delete drafts must state deletion is not guaranteed.",
            }
        )

    blocking = [f for f in findings if f["severity"] == "blocking"]
    return {
        "ok": len(blocking) == 0,
        "blocking_count": len(blocking),
        "warning_count": len(findings) - len(blocking),
        "findings": findings,
        "checklist": [
            {
                "id": "no_score_guarantees",
                "label": "No score-increase guarantees",
                "passed": not any(f["code"] == "score_guarantee" for f in findings),
            },
            {
                "id": "no_auto_removal_promises",
                "label": "No automatic removal promises",
                "passed": not any(f["code"] == "auto_removal" for f in findings),
            },
            {
                "id": "sections_populated",
                "label": "All sections populated",
                "passed": not any(f["code"] == "empty_sections" for f in findings),
            },
            {
                "id": "transmission_blocked",
                "label": "Auto-transmission remains blocked",
                "passed": True,
            },
        ],
    }


def apply_section_edit(
    sections: list[dict[str, Any]],
    section_key: str,
    *,
    body: str | None = None,
    fact_classification: FactClassification | None = None,
) -> list[dict[str, Any]]:
    updated: list[dict[str, Any]] = []
    found = False
    for section in sections:
        item = dict(section)
        if str(item.get("key")) == section_key:
            found = True
            if not item.get("editable", True):
                raise ValueError("Section is not editable")
            if body is not None:
                item["body"] = body.strip()
            if fact_classification is not None:
                item["fact_classification"] = fact_classification
        updated.append(item)
    if not found:
        raise KeyError(section_key)
    return updated


def next_workflow_status(current: str, target: str) -> str:
    allowed = WORKFLOW_TRANSITIONS.get(current, ())
    if target not in allowed:
        raise ValueError(f"Cannot advance from {current} to {target}")
    if target in TRANSMISSION_STATUSES:
        # Caller must use explicit mark-sent path; still never auto-transmits.
        pass
    return target
