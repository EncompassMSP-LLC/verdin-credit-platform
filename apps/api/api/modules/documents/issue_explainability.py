"""Plain-language case issue explainability cards (LRP-208).

Projects ranked compliance findings into client/staff-readable cards with
impact categories and evidence-strength bands. Advisory only — never promises
score-point increases or auto-files disputes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Literal

FindingStrength = Literal["strong", "moderate", "needs_more_evidence", "informational"]
ImpactCategory = Literal[
    "high",
    "medium",
    "low",
    "unknown",
    "no_score_impact_expected",
]

DISCLAIMER = (
    "Advisory case explainability only. Not legal advice and not a credit score "
    "prediction. Correcting inaccurate information may improve, leave unchanged, "
    "or temporarily change a consumer's credit profile; outcomes depend on the "
    "full file and lender models. The platform never guarantees point increases "
    "or loan approval. Dispute letters remain staff-mediated."
)

_DEFAULT_EVIDENCE = (
    "Account statement covering the disputed period",
    "Payment confirmation or bank record",
    "Creditor letter, email, or portal screenshot with date and account reference",
    "Prior dispute results, if any",
)


@dataclass(frozen=True, slots=True)
class IssueExplainabilityCard:
    source_id: str
    rule_id: str
    source_kind: str
    title: str
    what_we_found: str
    why_disputable: str
    possible_outcomes: tuple[str, ...]
    evidence_recommendations: tuple[str, ...]
    finding_strength: FindingStrength
    credit_profile_impact: ImpactCategory
    mortgage_readiness_impact: ImpactCategory
    recommended_next_action: str
    creditor_name: str | None
    account_number_masked: str | None
    bureau: str | None
    investigator_score: int
    rank: int


@dataclass(frozen=True, slots=True)
class CaseIssueExplainabilityResult:
    case_id: uuid.UUID
    disclaimer: str
    summary: dict[str, int]
    cards: tuple[IssueExplainabilityCard, ...]


def _finding_strength(score: int, severity: str) -> FindingStrength:
    if score >= 85 or severity == "high":
        return "strong"
    if score >= 70:
        return "moderate"
    if score >= 50:
        return "needs_more_evidence"
    return "informational"


def _credit_impact(rule_id: str, source_kind: str) -> ImpactCategory:
    lowered = rule_id.lower()
    if "freeze" in lowered or "fraud_alert" in lowered:
        return "no_score_impact_expected"
    if any(
        token in lowered
        for token in (
            "dofd",
            "late",
            "past_due",
            "charge_off",
            "collection",
            "status_mismatch",
            "missing_from_bureau",
            "obsolete",
            "identity_theft",
            "duplicate",
        )
    ):
        return "high"
    if any(
        token in lowered
        for token in ("balance", "utilization", "high_credit", "date_closed", "open_date")
    ):
        return "medium"
    if source_kind in {"chronology"} and "field_changed" in lowered:
        return "low"
    return "unknown"


def _mortgage_impact(rule_id: str, source_kind: str, credit: ImpactCategory) -> ImpactCategory:
    lowered = rule_id.lower()
    if any(
        token in lowered
        for token in (
            "dispute",
            "freeze",
            "fraud_alert",
            "identity_theft",
            "collection",
            "charge_off",
            "dofd",
            "status_mismatch",
            "missing_from_bureau",
        )
    ):
        return "high"
    if credit in {"high", "medium"}:
        return "medium"
    if source_kind == "metro2" and "closed" in lowered:
        return "medium"
    if credit == "no_score_impact_expected":
        return "medium"  # underwriting clarity can still matter
    return credit


def _title_for(rule_id: str, fallback: str) -> str:
    templates: dict[str, str] = {
        "cross_bureau.dofd_mismatch": "Possible incorrect late-payment or DOFD reporting",
        "cross_bureau.balance_mismatch": "Possible incorrect balance across bureaus",
        "cross_bureau.status_mismatch": "Possible incorrect account status across bureaus",
        "cross_bureau.past_due_mismatch": "Possible incorrect past-due amount across bureaus",
        "cross_bureau.missing_from_bureau": "Account missing from one or more bureaus",
        "metro2.current_with_past_due": "Account marked current while showing past due",
        "metro2.date_closed_before_open": "Impossible account dates (closed before opened)",
        "metro2.dofd_before_open": "Date of first delinquency before account open date",
        "metro2.closed_with_balance": "Closed account still showing a balance",
        "metro2.balance_exceeds_high_credit": "Balance exceeds high credit / credit limit",
        "fcra.obsolete_adverse_info": "Possibly obsolete adverse information",
        "fcra.adverse_missing_dofd": "Adverse item missing date of first delinquency",
        "chronology.dofd_changed": "Date of first delinquency changed across reports",
        "chronology.balance_increased": "Balance increased after a prior report",
        "chronology.status_changed": "Account status changed across stored reports",
    }
    if rule_id in templates:
        return templates[rule_id]
    clean = fallback.strip() or rule_id.replace(".", " ").replace("_", " ")
    return clean[:120]


def _what_we_found(issue: dict[str, Any]) -> str:
    creditor = issue.get("creditor_name") or "This account"
    bureau = issue.get("bureau")
    masked = issue.get("account_number_masked")
    title = str(issue.get("title") or "a reporting inconsistency")
    rationale = str(issue.get("rationale") or "").strip()
    parts = [f"{creditor}"]
    if masked:
        parts.append(f"({masked})")
    if bureau:
        parts.append(f"on {str(bureau).title()}")
    head = " ".join(parts)
    if rationale:
        return f"{head}: {rationale}"
    return f"{head} shows a finding described as “{title}.”"


def _why_disputable(rule_id: str, source_kind: str) -> str:
    if source_kind == "cross_bureau" or "mismatch" in rule_id:
        return (
            "The same account appears to have conflicting information across bureaus. "
            "Inconsistent reporting can support a request to investigate and correct the file."
        )
    if "dofd" in rule_id or "obsolete" in rule_id:
        return (
            "Aging and first-delinquency dates affect how long adverse information may remain "
            "and how lenders interpret payment history."
        )
    if "identity_theft" in rule_id:
        return (
            "Identity-theft or mixed-file indicators may support blocking ordinary disputes "
            "until the consumer confirms ownership and evidence is reviewed."
        )
    if source_kind == "metro2":
        return (
            "The reported fields appear internally inconsistent under Metro 2 reporting "
            "conventions, which can justify a request for verification or correction."
        )
    if source_kind == "fcra":
        return (
            "The finding touches accuracy or completeness obligations under the FCRA and may "
            "warrant staff-reviewed dispute preparation."
        )
    return (
        "The stored reports show a change or inconsistency that may warrant staff review "
        "and, if appropriate, a documented dispute."
    )


def _possible_outcomes(credit: ImpactCategory, mortgage: ImpactCategory) -> tuple[str, ...]:
    outcomes = [
        "If inaccurate, the item could be corrected or removed after investigation.",
        "A credit score could improve, remain unchanged, or temporarily change while a dispute "
        "is investigated — the platform does not estimate point changes.",
    ]
    if mortgage in {"high", "medium"}:
        outcomes.append(
            "A mortgage lender may require unresolved dispute comments or serious derogatories "
            "to be clarified before completing underwriting."
        )
    if credit == "no_score_impact_expected":
        outcomes.append(
            "This item may primarily affect documentation or underwriting clarity rather than "
            "a score factor."
        )
    return tuple(outcomes)


def _evidence_for(rule_id: str, hints: list[str] | None) -> tuple[str, ...]:
    extras: list[str] = []
    lowered = rule_id.lower()
    if "dofd" in lowered or "late" in lowered or "past_due" in lowered:
        extras.extend(
            [
                "Monthly statement covering the alleged late period",
                "Payment confirmation for the disputed month",
                "Bank statement showing the payment cleared",
            ]
        )
    if "balance" in lowered:
        extras.append("Statement or payoff letter matching the correct balance")
    if "identity_theft" in lowered:
        extras.extend(
            [
                "Identity-theft report or affidavit",
                "Police report or FTC IdentityTheft.gov materials, if applicable",
            ]
        )
    if "status" in lowered or "closed" in lowered:
        extras.append("Creditor letter confirming account status or closure date")
    merged: list[str] = []
    for item in [*(hints or []), *extras, *_DEFAULT_EVIDENCE]:
        if item and item not in merged:
            merged.append(item)
    return tuple(merged[:8])


def _next_action(strength: FindingStrength) -> str:
    if strength == "strong":
        return "Staff should review evidence readiness and consider a documented dispute draft."
    if strength == "moderate":
        return "Request supporting documents, then staff-review before preparing any letter."
    if strength == "needs_more_evidence":
        return "Collect stronger evidence before treating this as dispute-ready."
    return "Track as informational; no dispute action required unless new facts appear."


def build_issue_explainability_cards(
    *,
    case_id: uuid.UUID,
    issues: list[dict[str, Any]],
    checklist_hints_by_source_id: dict[str, list[str]] | None = None,
) -> CaseIssueExplainabilityResult:
    hints_map = checklist_hints_by_source_id or {}
    cards: list[IssueExplainabilityCard] = []
    counts = {
        "issues_explained": 0,
        "strong": 0,
        "moderate": 0,
        "needs_more_evidence": 0,
        "informational": 0,
        "high_credit_impact": 0,
        "high_mortgage_impact": 0,
    }

    for issue in issues:
        score = int(issue.get("score") or 0)
        severity = str(issue.get("severity") or "medium")
        rule_id = str(issue.get("rule_id") or "unknown")
        source_kind = str(issue.get("source_kind") or "unknown")
        source_id = str(issue.get("source_id") or rule_id)
        strength = _finding_strength(score, severity)
        credit = _credit_impact(rule_id, source_kind)
        mortgage = _mortgage_impact(rule_id, source_kind, credit)
        card = IssueExplainabilityCard(
            source_id=source_id,
            rule_id=rule_id,
            source_kind=source_kind,
            title=_title_for(rule_id, str(issue.get("title") or "")),
            what_we_found=_what_we_found(issue),
            why_disputable=_why_disputable(rule_id, source_kind),
            possible_outcomes=_possible_outcomes(credit, mortgage),
            evidence_recommendations=_evidence_for(rule_id, hints_map.get(source_id)),
            finding_strength=strength,
            credit_profile_impact=credit,
            mortgage_readiness_impact=mortgage,
            recommended_next_action=_next_action(strength),
            creditor_name=issue.get("creditor_name"),
            account_number_masked=issue.get("account_number_masked"),
            bureau=issue.get("bureau"),
            investigator_score=score,
            rank=int(issue.get("rank") or 0),
        )
        cards.append(card)
        counts["issues_explained"] += 1
        counts[strength] += 1
        if credit == "high":
            counts["high_credit_impact"] += 1
        if mortgage == "high":
            counts["high_mortgage_impact"] += 1

    cards.sort(
        key=lambda c: (0 if c.finding_strength == "strong" else 1, -c.investigator_score, c.rank)
    )
    return CaseIssueExplainabilityResult(
        case_id=case_id,
        disclaimer=DISCLAIMER,
        summary=counts,
        cards=tuple(cards),
    )
