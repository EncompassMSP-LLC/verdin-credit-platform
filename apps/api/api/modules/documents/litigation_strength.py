"""Litigation strength scoring for compliance findings (Phase 6 scaffold).

Ranks investigator issues by heuristic legal persuasiveness. Scores are
deterministic aids for prioritization — not legal advice or outcome predictions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Literal

SourceKind = Literal["metro2", "fcra", "cross_bureau", "chronology"]

# Base scores aligned to the product vision examples.
_RULE_BASE_SCORES: dict[str, int] = {
    # Impossible / strong factual Metro 2
    "metro2.date_closed_before_open": 95,
    "metro2.dofd_before_open": 95,
    "metro2.current_with_past_due": 90,
    "metro2.closed_with_balance": 88,
    "metro2.past_due_without_dofd": 85,
    "metro2.zero_balance_with_past_due": 80,
    "metro2.charge_off_zero_past_due": 78,
    "metro2.balance_exceeds_high_credit": 70,
    "metro2.open_with_date_closed": 72,
    "metro2.closed_missing_date_closed": 65,
    # FCRA statutory-oriented
    "fcra.obsolete_adverse_info": 92,
    "fcra.dofd_after_as_of": 95,
    "fcra.open_date_after_as_of": 95,
    "fcra.past_due_exceeds_balance": 88,
    "fcra.adverse_missing_dofd": 85,
    "fcra.sold_transferred_still_balance": 82,
    "fcra.collection_missing_original_creditor": 75,
    "fcra.closed_missing_date_closed": 65,
    # Cross-bureau discrepancy types
    "cross_bureau.dofd_mismatch": 98,
    "cross_bureau.balance_mismatch": 90,
    "cross_bureau.status_mismatch": 88,
    "cross_bureau.past_due_mismatch": 86,
    "cross_bureau.missing_from_bureau": 80,
    # Chronology events
    "chronology.balance_increased": 90,
    "chronology.dofd_changed": 95,
    "chronology.status_changed": 85,
    "chronology.disappeared": 88,
    "chronology.appeared": 60,
    "chronology.past_due_changed": 70,
    "chronology.date_closed_changed": 72,
    "chronology.balance_decreased": 55,
    "chronology.field_changed": 45,
}

_DEFAULT_SCORE = 50


@dataclass(frozen=True, slots=True)
class ScoredIssue:
    source_kind: SourceKind
    source_id: str
    rule_id: str
    score: int
    rank: int
    title: str
    rationale: str
    severity: str
    bureau: str | None
    creditor_name: str | None
    account_number_masked: str | None
    match_key: str | None
    factors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CaseLitigationStrengthResult:
    case_id: uuid.UUID
    summary: dict[str, int | float]
    issues: tuple[ScoredIssue, ...]


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _base_score(rule_id: str) -> int:
    if rule_id in _RULE_BASE_SCORES:
        return _RULE_BASE_SCORES[rule_id]
    # Prefix heuristics for unknown rules
    lowered = rule_id.lower()
    if "dofd" in lowered or "impossible" in lowered or "before_open" in lowered:
        return 90
    if "mismatch" in lowered:
        return 88
    if "obsolete" in lowered:
        return 90
    if "balance" in lowered:
        return 75
    if "missing" in lowered:
        return 70
    return _DEFAULT_SCORE


def _severity_bonus(severity: str) -> int:
    if severity == "high":
        return 5
    if severity == "medium":
        return 2
    return 0


def _rationale(rule_id: str, score: int, factors: tuple[str, ...]) -> str:
    base = f"Heuristic score {score}/100 for `{rule_id}`."
    if factors:
        return f"{base} Factors: {'; '.join(factors)}."
    return base


def score_case_litigation_strength(
    *,
    case_id: uuid.UUID,
    metro2_documents: list[dict[str, Any]],
    fcra_documents: list[dict[str, Any]],
    discrepancies: list[dict[str, Any]],
    chronology_events: list[dict[str, Any]],
) -> CaseLitigationStrengthResult:
    raw: list[tuple[int, ScoredIssue]] = []

    for source_kind, documents in (("metro2", metro2_documents), ("fcra", fcra_documents)):
        for document in documents:
            bureau = document.get("bureau") if isinstance(document.get("bureau"), str) else None
            document_id = document.get("document_id")
            findings = document.get("findings")
            if not isinstance(findings, list):
                continue
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                rule_id = str(finding.get("rule_id") or "unknown")
                severity = str(finding.get("severity") or "low")
                tradeline_index = finding.get("tradeline_index")
                index = tradeline_index if isinstance(tradeline_index, int) else 0
                creditor = finding.get("creditor_name")
                masked = finding.get("account_number_masked")
                factors = [f"severity:{severity}", f"source:{source_kind}"]
                score = _clamp_score(_base_score(rule_id) + _severity_bonus(severity))
                source_id = f"{source_kind}:{bureau or 'unknown'}:{rule_id}#{index}"
                if isinstance(document_id, uuid.UUID):
                    source_id = f"{source_id}@{document_id}"
                issue = ScoredIssue(
                    source_kind=source_kind,  # type: ignore[arg-type]
                    source_id=source_id,
                    rule_id=rule_id,
                    score=score,
                    rank=0,
                    title=str(finding.get("title") or rule_id),
                    rationale=_rationale(rule_id, score, tuple(factors)),
                    severity=severity,
                    bureau=bureau,
                    creditor_name=creditor if isinstance(creditor, str) else None,
                    account_number_masked=masked if isinstance(masked, str) else None,
                    match_key=None,
                    factors=tuple(factors),
                )
                raw.append((score, issue))

    for item in discrepancies:
        if not isinstance(item, dict):
            continue
        types = item.get("discrepancy_types")
        type_list = [str(t) for t in types] if isinstance(types, list) else ["mismatch"]
        match_key = item.get("match_key")
        creditor = item.get("creditor_name")
        masked = item.get("account_number_masked")
        for dtype in type_list:
            rule_id = f"cross_bureau.{dtype}"
            factors = [f"discrepancy:{dtype}", "source:cross_bureau"]
            # Multi-bureau consistency boost
            bureaus = item.get("bureaus_reporting")
            if isinstance(bureaus, list) and len(bureaus) >= 2:
                factors.append("multi_bureau")
            score = _clamp_score(
                _base_score(rule_id) + (3 if isinstance(bureaus, list) and len(bureaus) >= 2 else 0)
            )
            source_id = f"cross_bureau:{match_key or 'unknown'}:{dtype}"
            issue = ScoredIssue(
                source_kind="cross_bureau",
                source_id=source_id,
                rule_id=rule_id,
                score=score,
                rank=0,
                title=str(item.get("classification_label") or f"Cross-bureau {dtype}"),
                rationale=_rationale(rule_id, score, tuple(factors)),
                severity="high" if score >= 85 else "medium" if score >= 70 else "low",
                bureau=None,
                creditor_name=creditor if isinstance(creditor, str) else None,
                account_number_masked=masked if isinstance(masked, str) else None,
                match_key=match_key if isinstance(match_key, str) else None,
                factors=tuple(factors),
            )
            raw.append((score, issue))

    for event in chronology_events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("event_type") or "field_changed")
        rule_id = f"chronology.{event_type}"
        severity = str(event.get("severity") or "low")
        factors = [f"event:{event_type}", f"severity:{severity}", "source:chronology"]
        score = _clamp_score(_base_score(rule_id) + _severity_bonus(severity))
        match_key = event.get("match_key")
        bureau = event.get("bureau")
        source_id = (
            f"chronology:{bureau or 'unknown'}:{match_key or 'unknown'}:"
            f"{event_type}:{event.get('to_document_id') or 'na'}"
        )
        issue = ScoredIssue(
            source_kind="chronology",
            source_id=source_id,
            rule_id=rule_id,
            score=score,
            rank=0,
            title=str(event.get("summary") or event_type),
            rationale=_rationale(rule_id, score, tuple(factors)),
            severity=severity,
            bureau=bureau if isinstance(bureau, str) else None,
            creditor_name=event.get("creditor_name")
            if isinstance(event.get("creditor_name"), str)
            else None,
            account_number_masked=event.get("account_number_masked")
            if isinstance(event.get("account_number_masked"), str)
            else None,
            match_key=match_key if isinstance(match_key, str) else None,
            factors=tuple(factors),
        )
        raw.append((score, issue))

    raw.sort(key=lambda pair: (-pair[0], pair[1].source_id))
    ranked: list[ScoredIssue] = []
    for index, (score, issue) in enumerate(raw, start=1):
        ranked.append(
            ScoredIssue(
                source_kind=issue.source_kind,
                source_id=issue.source_id,
                rule_id=issue.rule_id,
                score=score,
                rank=index,
                title=issue.title,
                rationale=issue.rationale,
                severity=issue.severity,
                bureau=issue.bureau,
                creditor_name=issue.creditor_name,
                account_number_masked=issue.account_number_masked,
                match_key=issue.match_key,
                factors=issue.factors,
            )
        )

    scores = [item.score for item in ranked]
    summary: dict[str, int | float] = {
        "issues_scored": len(ranked),
        "high_priority": sum(1 for item in ranked if item.score >= 85),
        "medium_priority": sum(1 for item in ranked if 70 <= item.score < 85),
        "low_priority": sum(1 for item in ranked if item.score < 70),
        "top_score": max(scores) if scores else 0,
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0.0,
    }
    return CaseLitigationStrengthResult(
        case_id=case_id,
        summary=summary,
        issues=tuple(ranked),
    )
