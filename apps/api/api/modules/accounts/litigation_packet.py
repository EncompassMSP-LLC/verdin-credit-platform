"""Litigation-readiness evidence assessment (Phase 11 slice 5).

Pure, side-effect-free scoring that grades a tradeline's reinvestigation trail
into an advisory FCRA §611/§623 willful-noncompliance readiness assessment for a
**human attorney handoff**.

Guardrails: this never files anything, never contacts a bureau, never drafts a
legal pleading, and never transmits to a court or attorney. It only assembles
and grades evidence a person will review before deciding whether to litigate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from api.modules.accounts.reinvestigation import ReinvestigationClockState

LitigationStrength = Literal["strong", "moderate", "weak", "not_ready"]

# risk_score at/above this marks a well-documented dispute (strong claim signal).
_HIGH_STRENGTH_THRESHOLD = 80

# Recorded outcomes that mean the tradeline was fixed — no litigation basis.
_RESOLVED_OUTCOMES = frozenset({"deleted", "corrected"})


@dataclass(frozen=True)
class LitigationReadinessInputs:
    clock_state: ReinvestigationClockState
    latest_outcome: str | None
    dispute_round: int
    risk_score: int | None
    sent_letter_count: int
    response_count: int


@dataclass(frozen=True)
class LitigationReadiness:
    eligible: bool
    strength: LitigationStrength
    score: int
    indicators: list[str] = field(default_factory=list)
    summary: str = ""


def build_litigation_readiness(inputs: LitigationReadinessInputs) -> LitigationReadiness:
    """Grade a tradeline's willful-noncompliance evidence for attorney handoff.

    Returns an advisory assessment: a 0–100 ``score``, a ``strength`` band, the
    ``indicators`` that contributed, and a plain-language ``summary``. Higher
    scores reflect stronger §611/§623 willful-noncompliance signals (missed
    reinvestigation deadlines, verification of well-documented disputes, and
    repeated rounds without resolution).
    """
    outcome = (inputs.latest_outcome or "").lower()

    if outcome in _RESOLVED_OUTCOMES:
        return LitigationReadiness(
            eligible=False,
            strength="not_ready",
            score=0,
            indicators=[],
            summary="The tradeline was deleted or corrected. No litigation basis exists.",
        )

    indicators: list[str] = []
    score = 0

    if inputs.clock_state == "overdue":
        indicators.append(
            "CRA missed the §611 reinvestigation deadline without a recorded response "
            "(potential statutory violation)."
        )
        score += 30

    if outcome == "verified":
        indicators.append("Bureau verified the disputed tradeline as accurate.")
        score += 20
        if inputs.risk_score is not None and inputs.risk_score >= _HIGH_STRENGTH_THRESHOLD:
            indicators.append(
                "A well-documented, high-strength dispute was verified anyway "
                "(supports a willful-noncompliance theory)."
            )
            score += 30
        if inputs.dispute_round >= 2 or inputs.sent_letter_count >= 2:
            indicators.append(
                "The item was verified across multiple dispute rounds "
                "(pattern of inadequate reinvestigation)."
            )
            score += 25
    elif outcome == "rejected":
        indicators.append(
            "The dispute was rejected as frivolous without a substantive reinvestigation."
        )
        score += 25

    if inputs.sent_letter_count >= 3:
        indicators.append(
            "Three or more dispute rounds were mailed without resolution "
            "(reinforces a pattern of noncompliance)."
        )
        score += 10

    score = min(score, 100)

    if score >= 60:
        strength: LitigationStrength = "strong"
    elif score >= 30:
        strength = "moderate"
    elif score > 0:
        strength = "weak"
    else:
        strength = "not_ready"

    eligible = strength in ("strong", "moderate")

    if not indicators:
        summary = (
            "No willful-noncompliance indicators yet. Continue the standard "
            "reinvestigation workflow before considering litigation."
        )
    elif eligible:
        summary = (
            "Willful-noncompliance indicators are present. Assemble the evidence "
            "trail and hand off to an attorney for review — the platform never files."
        )
    else:
        summary = (
            "Early willful-noncompliance signals are present but the claim is not yet "
            "strong. Continue building the reinvestigation record."
        )

    return LitigationReadiness(
        eligible=eligible,
        strength=strength,
        score=score,
        indicators=indicators,
        summary=summary,
    )
