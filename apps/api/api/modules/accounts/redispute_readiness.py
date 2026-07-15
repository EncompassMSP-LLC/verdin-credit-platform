"""Advisory re-dispute / escalation readiness (Phase 10 slice 4).

Pure, side-effect-free scoring that turns the §611 reinvestigation clock state,
the most recent recorded response outcome, the dispute round, and the account's
investigative strength into an *advisory* next-step recommendation.

Guardrails: this never files anything, never contacts a bureau, and never
auto-escalates. It only suggests what a human investigator might do next.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from api.modules.accounts.reinvestigation import ReinvestigationClockState

RedisputeAction = Literal[
    "wait",
    "prepare_initial",
    "redispute",
    "escalate_cfpb",
    "escalate_attorney",
    "resolved",
]
RedisputePriority = Literal["high", "medium", "low"]

# Recorded response outcomes that represent a real bureau/furnisher reply.
RESOLVED_OUTCOMES = frozenset({"deleted", "corrected"})

# risk_score at/above this suggests a strong enough claim to consult an attorney.
_ATTORNEY_STRENGTH_THRESHOLD = 80


@dataclass(frozen=True)
class RedisputeRecommendation:
    action: RedisputeAction
    priority: RedisputePriority
    reason: str


def compute_redispute_readiness(
    *,
    clock_state: ReinvestigationClockState,
    latest_outcome: str | None,
    dispute_round: int,
    risk_score: int | None,
) -> RedisputeRecommendation:
    """Recommend an advisory next step for a tradeline's reinvestigation."""
    if clock_state == "not_sent":
        return RedisputeRecommendation(
            "prepare_initial",
            "medium",
            "No dispute has been mailed yet. Prepare the initial §611 dispute.",
        )
    if clock_state in ("awaiting", "due_soon"):
        return RedisputeRecommendation(
            "wait",
            "low",
            "The 30-day reinvestigation window is still open. Await the bureau response.",
        )
    if clock_state == "overdue":
        return RedisputeRecommendation(
            "redispute",
            "high",
            "The bureau did not respond within the 30-day §611 window. Re-dispute and "
            "cite the missed reinvestigation deadline.",
        )

    # clock_state == "responded": branch on the recorded outcome.
    outcome = (latest_outcome or "").lower()
    if outcome in RESOLVED_OUTCOMES:
        return RedisputeRecommendation(
            "resolved",
            "low",
            "The tradeline was deleted or corrected. No further dispute action needed.",
        )
    if outcome == "updated":
        return RedisputeRecommendation(
            "redispute",
            "medium",
            "The bureau updated the tradeline but did not fully resolve it. Re-dispute the "
            "remaining inaccuracies.",
        )
    if outcome == "rejected":
        return RedisputeRecommendation(
            "escalate_cfpb",
            "high",
            "The dispute was rejected as frivolous. Escalate with a CFPB complaint documenting "
            "the good-faith basis.",
        )
    if outcome == "verified":
        if risk_score is not None and risk_score >= _ATTORNEY_STRENGTH_THRESHOLD:
            return RedisputeRecommendation(
                "escalate_attorney",
                "high",
                "The bureau verified a high-strength disputed item. Consider an attorney consult "
                "(FCRA §611/§623 willful-noncompliance theory).",
            )
        if dispute_round >= 2:
            return RedisputeRecommendation(
                "escalate_cfpb",
                "high",
                "The item was verified across multiple rounds. Escalate with a CFPB complaint and "
                "request the method of verification.",
            )
        return RedisputeRecommendation(
            "redispute",
            "medium",
            "The bureau verified the item. Re-dispute with a method-of-verification (MOV) request "
            "and any new evidence.",
        )

    # Responded but with an unrecognized / unspecified outcome.
    return RedisputeRecommendation(
        "redispute",
        "medium",
        "A response was recorded. Review the outcome and re-dispute if inaccuracies remain.",
    )
