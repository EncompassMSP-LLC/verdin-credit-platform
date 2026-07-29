"""Approved letter-template catalog for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LetterTemplateKind = Literal[
    "bureau_dispute",
    "furnisher_dispute",
    "method_of_verification",
    "cfpb_complaint",
    "ftc_identity_theft",
    "debt_validation",
    "goodwill",
    "late_payment_forgiveness",
    "pay_for_delete",
    "communication_preference",
    "cease_communication",
    "mortgage_explanation",
    "custom_staff",
]

LetterSectionKey = Literal[
    "introduction",
    "account_summary",
    "issue",
    "legal_references",
    "requested_resolution",
    "attachments",
    "closing",
]

FactClassification = Literal[
    "verified",
    "client_statement",
    "document_supported",
    "staff_observation",
]


@dataclass(frozen=True, slots=True)
class LetterTemplate:
    kind: LetterTemplateKind
    title: str
    description: str
    default_sections: tuple[LetterSectionKey, ...]
    claim_warnings: tuple[str, ...]


LETTER_TEMPLATES: tuple[LetterTemplate, ...] = (
    LetterTemplate(
        kind="bureau_dispute",
        title="Credit bureau dispute",
        description="Request investigation/correction of inaccurate tradeline information with a CRA.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "legal_references",
            "requested_resolution",
            "attachments",
            "closing",
        ),
        claim_warnings=("Do not promise score increases or automatic removals.",),
    ),
    LetterTemplate(
        kind="furnisher_dispute",
        title="Direct creditor / furnisher dispute",
        description="Direct dispute to the furnisher regarding reported account information.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "legal_references",
            "requested_resolution",
            "attachments",
            "closing",
        ),
        claim_warnings=("Do not promise score increases or automatic removals.",),
    ),
    LetterTemplate(
        kind="method_of_verification",
        title="Method of verification request",
        description="Ask how the CRA verified disputed information.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "legal_references",
            "requested_resolution",
            "closing",
        ),
        claim_warnings=("Do not assert verification was unlawful without evidence.",),
    ),
    LetterTemplate(
        kind="cfpb_complaint",
        title="CFPB complaint draft",
        description="Staff-mediated CFPB complaint narrative draft for review.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "requested_resolution",
            "attachments",
            "closing",
        ),
        claim_warnings=("Draft only — never auto-file with CFPB.",),
    ),
    LetterTemplate(
        kind="ftc_identity_theft",
        title="FTC identity-theft draft",
        description="Identity-theft recovery narrative for staff/client review.",
        default_sections=(
            "introduction",
            "issue",
            "requested_resolution",
            "attachments",
            "closing",
        ),
        claim_warnings=("Never silently submit to FTC IdentityTheft.gov.",),
    ),
    LetterTemplate(
        kind="debt_validation",
        title="Debt validation letter",
        description="Request validation of an alleged debt from a collector.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "legal_references",
            "requested_resolution",
            "closing",
        ),
        claim_warnings=("Do not claim the debt is invalid without supporting facts.",),
    ),
    LetterTemplate(
        kind="goodwill",
        title="Goodwill letter",
        description="Request discretionary goodwill adjustment of a reported late payment.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "requested_resolution",
            "closing",
        ),
        claim_warnings=("Goodwill is discretionary — never guarantee an outcome.",),
    ),
    LetterTemplate(
        kind="late_payment_forgiveness",
        title="Late-payment forgiveness request",
        description="Request removal or correction of a late-payment notation.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "requested_resolution",
            "attachments",
            "closing",
        ),
        claim_warnings=("Never guarantee score-point recovery.",),
    ),
    LetterTemplate(
        kind="pay_for_delete",
        title="Pay-for-delete request",
        description="Request deletion after payment — clearly marked as a request, not a guarantee.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "requested_resolution",
            "closing",
        ),
        claim_warnings=(
            "Pay-for-delete is a request only; many furnishers decline. Never guarantee deletion.",
        ),
    ),
    LetterTemplate(
        kind="communication_preference",
        title="Communication preference letter",
        description="Document preferred contact channels and opt-out preferences.",
        default_sections=("introduction", "requested_resolution", "closing"),
        claim_warnings=("Draft only — staff-gated before transmission.",),
    ),
    LetterTemplate(
        kind="cease_communication",
        title="Cease-communication letter",
        description="Request that a collector cease further communication where appropriate.",
        default_sections=("introduction", "account_summary", "requested_resolution", "closing"),
        claim_warnings=("Staff and client review required before any transmission.",),
    ),
    LetterTemplate(
        kind="mortgage_explanation",
        title="Mortgage lender explanation letter",
        description="Explain readiness context or dispute status for a mortgage underwriting condition.",
        default_sections=(
            "introduction",
            "account_summary",
            "issue",
            "requested_resolution",
            "closing",
        ),
        claim_warnings=("Never predict approval, funding, or underwriting outcomes.",),
    ),
    LetterTemplate(
        kind="custom_staff",
        title="Custom attorney/staff letter",
        description="Blank structured draft for staff/attorney customization.",
        default_sections=("introduction", "issue", "requested_resolution", "closing"),
        claim_warnings=("Staff must supply verified facts; do not invent case details.",),
    ),
)


def get_template(kind: LetterTemplateKind) -> LetterTemplate:
    for template in LETTER_TEMPLATES:
        if template.kind == kind:
            return template
    raise KeyError(kind)


DISCLAIMER = (
    "Staff-gated letter draft only. Not legal advice. Not automatically mailed, emailed, "
    "or submitted to any bureau, creditor, collector, CFPB, or FTC. Client approval and "
    "staff review are required before any transmission. The platform never guarantees "
    "score increases, deletions, approvals, or funding."
)

SEND_GUARDRAILS = {
    "auto_transmit": False,
    "transmission_blocked": True,
    "requires_staff_review": True,
    "requires_client_approval_when_configured": True,
}
