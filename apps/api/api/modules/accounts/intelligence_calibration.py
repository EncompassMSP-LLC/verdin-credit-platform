"""Calibrated account scoring using cross-bureau discrepancy signals."""

from __future__ import annotations

from dataclasses import dataclass


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


@dataclass(frozen=True, slots=True)
class DiscrepancyScoringContext:
    match_key: str
    classification: str
    confidence_score: int
    dispute_ready: bool
    requires_investigation: bool
    discrepancy_types: tuple[str, ...]
    recommended_action: str


def calibrate_risk_score(heuristic_score: int, context: DiscrepancyScoringContext) -> int:
    if context.classification == "consistent":
        return heuristic_score

    bonus = min(25, context.confidence_score // 4)
    if "missing_from_bureau" in context.discrepancy_types:
        bonus += 10
    if "balance_mismatch" in context.discrepancy_types:
        bonus += 8
    if "status_mismatch" in context.discrepancy_types:
        bonus += 6
    return _clamp_score(heuristic_score + bonus)


def calibrate_readiness_score(heuristic_score: int, context: DiscrepancyScoringContext) -> int:
    adjusted = heuristic_score
    if context.dispute_ready:
        adjusted += min(15, context.confidence_score // 5)
    if context.requires_investigation:
        adjusted -= 10
    if context.classification != "consistent":
        adjusted += min(8, context.confidence_score // 8)
    return _clamp_score(adjusted)


def calibrate_scores(
    heuristic_risk: int,
    heuristic_readiness: int,
    context: DiscrepancyScoringContext | None,
) -> tuple[int, int]:
    if context is None:
        return heuristic_risk, heuristic_readiness
    return (
        calibrate_risk_score(heuristic_risk, context),
        calibrate_readiness_score(heuristic_readiness, context),
    )
