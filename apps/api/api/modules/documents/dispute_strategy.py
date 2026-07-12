"""Dispute strategy generator for compliance findings (Phase 7 scaffold).

Builds a multi-stage investigator plan grounded in ranked litigation-strength
issues. Staff-mediated aid only — not legal advice or automated filing.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

StageKind = Literal[
    "cra_dispute",
    "furnisher_dispute",
    "cfpb_escalation",
    "attorney_preserve",
]

_DISCLAIMER = (
    "Investigator planning aid only. Not legal advice. Does not file disputes "
    "or contact bureaus, furnishers, or regulators automatically."
)


@dataclass(frozen=True, slots=True)
class StrategyStage:
    stage_order: int
    stage_kind: StageKind
    title: str
    objective: str
    rationale: str
    issue_source_ids: tuple[str, ...]
    evidence_hints: tuple[str, ...]
    recommended: bool


@dataclass(frozen=True, slots=True)
class AccountDisputeStrategy:
    account_key: str
    creditor_name: str | None
    account_number_masked: str | None
    bureau: str | None
    match_key: str | None
    top_score: int
    issue_count: int
    primary_rule_ids: tuple[str, ...]
    summary: str
    stages: tuple[StrategyStage, ...]


@dataclass(frozen=True, slots=True)
class CaseDisputeStrategyResult:
    case_id: uuid.UUID
    disclaimer: str
    summary: dict[str, int]
    strategies: tuple[AccountDisputeStrategy, ...]


def _account_key(issue: dict[str, Any]) -> str:
    match_key = issue.get("match_key")
    if isinstance(match_key, str) and match_key.strip():
        return f"match:{match_key.strip().lower()}"
    creditor = str(issue.get("creditor_name") or "unknown").strip().lower()
    masked = str(issue.get("account_number_masked") or "unknown").strip().lower()
    bureau = str(issue.get("bureau") or "multi").strip().lower()
    return f"acct:{creditor}|{masked}|{bureau}"


def _issue_score(issue: dict[str, Any]) -> int:
    score = issue.get("score")
    return int(score) if isinstance(score, int | float) else 0


def _warrants_furnisher(issues: list[dict[str, Any]]) -> bool:
    for issue in issues:
        if _issue_score(issue) >= 70:
            return True
        rule_id = str(issue.get("rule_id") or "").lower()
        source = str(issue.get("source_kind") or "").lower()
        if source in {"cross_bureau", "metro2", "fcra"}:
            return True
        if any(token in rule_id for token in ("balance", "status", "dofd", "past_due", "furnish")):
            return True
    return False


def _warrants_cfpb(issues: list[dict[str, Any]]) -> bool:
    for issue in issues:
        score = _issue_score(issue)
        rule_id = str(issue.get("rule_id") or "").lower()
        if score >= 85:
            return True
        if "obsolete" in rule_id or "dofd_mismatch" in rule_id:
            return True
        if "impossible" in rule_id or "before_open" in rule_id:
            return True
    return False


def _warrants_attorney(issues: list[dict[str, Any]]) -> bool:
    high = sum(1 for issue in issues if _issue_score(issue) >= 85)
    if high >= 2:
        return True
    return any(_issue_score(issue) >= 90 for issue in issues)


def _source_ids(issues: list[dict[str, Any]], *, min_score: int = 0) -> tuple[str, ...]:
    ids: list[str] = []
    for issue in issues:
        if _issue_score(issue) < min_score:
            continue
        source_id = issue.get("source_id")
        if isinstance(source_id, str) and source_id:
            ids.append(source_id)
    return tuple(ids)


def _hints_for(
    source_ids: tuple[str, ...],
    evidence_hints_by_source_id: dict[str, list[str]],
) -> tuple[str, ...]:
    collected: list[str] = []
    seen: set[str] = set()
    for source_id in source_ids:
        for hint in evidence_hints_by_source_id.get(source_id, []):
            if hint not in seen:
                seen.add(hint)
                collected.append(hint)
    return tuple(collected)


def _build_stages(
    issues: list[dict[str, Any]],
    evidence_hints_by_source_id: dict[str, list[str]],
) -> tuple[StrategyStage, ...]:
    all_ids = _source_ids(issues)
    high_ids = _source_ids(issues, min_score=85)
    stages: list[StrategyStage] = []

    stages.append(
        StrategyStage(
            stage_order=1,
            stage_kind="cra_dispute",
            title="CRA dispute on documented discrepancies",
            objective=(
                "Dispute the ranked inaccuracies with each credit reporting agency "
                "that shows the issue, attaching report excerpts and identity exhibits."
            ),
            rationale="Start with bureau disputes grounded in documented Metro 2 / FCRA / cross-bureau facts.",
            issue_source_ids=all_ids,
            evidence_hints=_hints_for(all_ids, evidence_hints_by_source_id)
            or (
                "Attach bureau report PDF for each disputed bureau",
                "Include identity and proof-of-address exhibits",
            ),
            recommended=True,
        )
    )

    furnisher = _warrants_furnisher(issues)
    stages.append(
        StrategyStage(
            stage_order=2,
            stage_kind="furnisher_dispute",
            title="Furnisher direct dispute if unresolved",
            objective=(
                "If CRA investigation does not correct the reporting, dispute directly "
                "with the furnisher using the same factual findings."
            ),
            rationale=(
                "Furnisher escalation is recommended when strength scores are material "
                "or reporting inconsistencies implicate the data furnisher."
                if furnisher
                else "Optional follow-up if CRA results leave material inaccuracies unresolved."
            ),
            issue_source_ids=all_ids if furnisher else (),
            evidence_hints=_hints_for(all_ids, evidence_hints_by_source_id)
            if furnisher
            else ("Preserve CRA responses before furnisher outreach",),
            recommended=furnisher,
        )
    )

    cfpb = _warrants_cfpb(issues)
    stages.append(
        StrategyStage(
            stage_order=3,
            stage_kind="cfpb_escalation",
            title="CFPB escalation if warranted",
            objective=(
                "Escalate unresolved high-strength inaccuracies through CFPB complaint "
                "channels after documenting CRA/furnisher responses."
            ),
            rationale=(
                "High litigation-strength or statutory-oriented findings support considering regulator escalation."
                if cfpb
                else "Not recommended yet — reserve for unresolved high-strength issues."
            ),
            issue_source_ids=high_ids if cfpb else (),
            evidence_hints=(
                "Preserve dispute letters and bureau/furnisher responses",
                "Timeline of investigation dates",
            )
            if cfpb
            else (),
            recommended=cfpb,
        )
    )

    attorney = _warrants_attorney(issues)
    stages.append(
        StrategyStage(
            stage_order=4,
            stage_kind="attorney_preserve",
            title="Preserve documents for attorney consult",
            objective=(
                "Package ranked findings, evidence links, dispute correspondence, and "
                "chronology for attorney review — no unsupervised legal action."
            ),
            rationale=(
                "Multiple high-strength issues or near-ceiling scores warrant preserving a litigation-ready file."
                if attorney
                else "Always preserve the working file; escalate to attorney consult when strength rises."
            ),
            issue_source_ids=all_ids,
            evidence_hints=(
                "Export litigation strength ranking",
                "Retain evidence-linked report excerpts",
                "Retain dispute mail packets and responses",
            ),
            # Always recommend preservation as investigator hygiene.
            recommended=True,
        )
    )

    return tuple(stages)


def generate_case_dispute_strategy(
    *,
    case_id: uuid.UUID,
    scored_issues: list[dict[str, Any]],
    evidence_hints_by_source_id: dict[str, list[str]] | None = None,
) -> CaseDisputeStrategyResult:
    hints = evidence_hints_by_source_id or {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for issue in scored_issues:
        if not isinstance(issue, dict):
            continue
        if not isinstance(issue.get("source_id"), str):
            continue
        grouped.setdefault(_account_key(issue), []).append(issue)

    strategies: list[AccountDisputeStrategy] = []
    for account_key, issues in grouped.items():
        issues_sorted = sorted(issues, key=_issue_score, reverse=True)
        top = issues_sorted[0]
        top_score = _issue_score(top)
        primary_rules = tuple(
            str(issue.get("rule_id"))
            for issue in issues_sorted[:3]
            if isinstance(issue.get("rule_id"), str)
        )
        creditor = top.get("creditor_name") if isinstance(top.get("creditor_name"), str) else None
        masked = (
            top.get("account_number_masked")
            if isinstance(top.get("account_number_masked"), str)
            else None
        )
        bureau = top.get("bureau") if isinstance(top.get("bureau"), str) else None
        match_key = top.get("match_key") if isinstance(top.get("match_key"), str) else None
        stages = _build_stages(issues_sorted, hints)
        recommended_count = sum(1 for stage in stages if stage.recommended)
        account_summary = (
            f"{len(issues_sorted)} ranked issue(s); top score {top_score}/100; "
            f"{recommended_count} recommended stage(s)."
        )
        strategies.append(
            AccountDisputeStrategy(
                account_key=account_key,
                creditor_name=creditor,
                account_number_masked=masked,
                bureau=bureau,
                match_key=match_key,
                top_score=top_score,
                issue_count=len(issues_sorted),
                primary_rule_ids=primary_rules,
                summary=account_summary,
                stages=stages,
            )
        )

    strategies.sort(key=lambda item: (-item.top_score, item.account_key))
    case_summary = {
        "accounts_planned": len(strategies),
        "issues_covered": sum(item.issue_count for item in strategies),
        "high_strength_accounts": sum(1 for item in strategies if item.top_score >= 85),
        "cfpb_recommended": sum(
            1
            for item in strategies
            for stage in item.stages
            if stage.stage_kind == "cfpb_escalation" and stage.recommended
        ),
        "attorney_recommended": sum(
            1
            for item in strategies
            for stage in item.stages
            if stage.stage_kind == "attorney_preserve" and stage.recommended
        ),
    }
    return CaseDisputeStrategyResult(
        case_id=case_id,
        disclaimer=_DISCLAIMER,
        summary=case_summary,
        strategies=tuple(strategies),
    )


_PREPARABLE_STAGES: frozenset[StageKind] = frozenset({"cra_dispute", "furnisher_dispute"})


@dataclass(frozen=True, slots=True)
class StrategyPrepTarget:
    account_key: str
    match_key: str | None
    creditor_name: str
    account_number_masked: str | None
    bureau: str | None
    primary_rule_ids: tuple[str, ...]
    summary: str


def stage_recipient_type(stage_kind: StageKind) -> Literal["credit_bureau", "furnisher"]:
    if stage_kind == "furnisher_dispute":
        return "furnisher"
    if stage_kind == "cra_dispute":
        return "credit_bureau"
    raise ValueError(f"Stage `{stage_kind}` does not create dispute letters")


def _stage_matches(
    stages: Any,
    *,
    stage_kind: StageKind,
    recommended_only: bool,
) -> bool:
    for stage in stages or ():
        if isinstance(stage, dict):
            kind = stage.get("stage_kind")
            recommended = bool(stage.get("recommended"))
        else:
            kind = getattr(stage, "stage_kind", None)
            recommended = bool(getattr(stage, "recommended", False))
        if kind != stage_kind:
            continue
        if recommended_only and not recommended:
            continue
        return True
    return False


def select_accounts_for_stage(
    strategies: Sequence[Any],
    *,
    stage_kind: StageKind,
    account_keys: list[str] | None = None,
    recommended_only: bool = True,
) -> tuple[StrategyPrepTarget, ...]:
    """Return preparable strategy accounts for a CRA/furnisher stage."""
    if stage_kind not in _PREPARABLE_STAGES:
        return ()

    selected_keys = set(account_keys) if account_keys else None
    targets: list[StrategyPrepTarget] = []
    seen_keys: set[str] = set()

    for item in strategies:
        if isinstance(item, dict):
            account_key = item.get("account_key")
            match_key = item.get("match_key")
            creditor_name = item.get("creditor_name")
            account_number_masked = item.get("account_number_masked")
            bureau = item.get("bureau")
            primary_rule_ids = item.get("primary_rule_ids") or []
            summary = item.get("summary") or ""
            stages = item.get("stages") or []
        else:
            account_key = getattr(item, "account_key", None)
            match_key = getattr(item, "match_key", None)
            creditor_name = getattr(item, "creditor_name", None)
            account_number_masked = getattr(item, "account_number_masked", None)
            bureau = getattr(item, "bureau", None)
            primary_rule_ids = getattr(item, "primary_rule_ids", ()) or ()
            summary = getattr(item, "summary", "") or ""
            stages = getattr(item, "stages", ()) or ()

        if not isinstance(account_key, str) or account_key in seen_keys:
            continue
        if selected_keys is not None and account_key not in selected_keys:
            continue
        if not isinstance(creditor_name, str) or not creditor_name.strip():
            continue
        if not _stage_matches(stages, stage_kind=stage_kind, recommended_only=recommended_only):
            continue

        seen_keys.add(account_key)
        targets.append(
            StrategyPrepTarget(
                account_key=account_key,
                match_key=match_key if isinstance(match_key, str) and match_key.strip() else None,
                creditor_name=creditor_name.strip(),
                account_number_masked=account_number_masked
                if isinstance(account_number_masked, str)
                else None,
                bureau=bureau if isinstance(bureau, str) else None,
                primary_rule_ids=tuple(str(rule) for rule in primary_rule_ids),
                summary=str(summary),
            )
        )

    return tuple(targets)


def select_match_keys_for_stage(
    strategies: Sequence[Any],
    *,
    stage_kind: StageKind,
    account_keys: list[str] | None = None,
    recommended_only: bool = True,
) -> tuple[str, ...]:
    """Return discrepancy match_keys for accounts that warrant the stage."""
    targets = select_accounts_for_stage(
        strategies,
        stage_kind=stage_kind,
        account_keys=account_keys,
        recommended_only=recommended_only,
    )
    match_keys: list[str] = []
    seen: set[str] = set()
    for target in targets:
        if target.match_key is None or target.match_key in seen:
            continue
        seen.add(target.match_key)
        match_keys.append(target.match_key)
    return tuple(match_keys)
