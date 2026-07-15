"""Reinvestigation outcome analytics (Phase 11).

Pure aggregation over recorded dispute-response outcomes: per-outcome counts,
favorable / deletion / verification rates, and time-to-response statistics. No
database access — the reporting repository supplies rows so this stays
unit-testable and free of live bureau contact.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from statistics import median

# The six recorded dispute-response outcomes (mirrors DisputeResponseOutcome).
OUTCOME_KEYS = ("deleted", "verified", "updated", "corrected", "no_response", "rejected")

# Favorable = the disputed tradeline was removed or fixed for the consumer.
_FAVORABLE_OUTCOMES = frozenset({"deleted", "corrected"})


@dataclass(frozen=True)
class ReinvestigationOutcomeRow:
    """A single recorded response, reduced to what the analytics need."""

    outcome: str
    days_to_response: int | None


@dataclass(frozen=True)
class ReinvestigationOutcomeAnalytics:
    total_responses: int
    counts: dict[str, int]
    deletion_rate: float
    verification_rate: float
    correction_rate: float
    favorable_rate: float
    no_response_rate: float
    avg_days_to_response: float | None
    median_days_to_response: float | None
    measured_response_count: int


def _rate(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def compute_reinvestigation_outcome_analytics(
    rows: Sequence[ReinvestigationOutcomeRow],
) -> ReinvestigationOutcomeAnalytics:
    """Aggregate recorded response outcomes into per-org reinvestigation trends.

    Rates are fractions of the total recorded responses. Time-to-response stats
    only consider substantive responses (a recorded ``no_response`` has no
    meaningful elapsed time) with a known elapsed duration.
    """
    counts = dict.fromkeys(OUTCOME_KEYS, 0)
    durations: list[int] = []
    for row in rows:
        if row.outcome in counts:
            counts[row.outcome] += 1
        if row.days_to_response is not None and row.outcome != "no_response":
            durations.append(row.days_to_response)

    total = sum(counts.values())
    favorable = counts["deleted"] + counts["corrected"]
    avg = round(sum(durations) / len(durations), 1) if durations else None
    med = round(float(median(durations)), 1) if durations else None

    return ReinvestigationOutcomeAnalytics(
        total_responses=total,
        counts=counts,
        deletion_rate=_rate(counts["deleted"], total),
        verification_rate=_rate(counts["verified"], total),
        correction_rate=_rate(counts["corrected"], total),
        favorable_rate=_rate(favorable, total),
        no_response_rate=_rate(counts["no_response"], total),
        avg_days_to_response=avg,
        median_days_to_response=med,
        measured_response_count=len(durations),
    )
