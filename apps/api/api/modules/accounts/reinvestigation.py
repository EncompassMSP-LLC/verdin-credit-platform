"""FCRA §611 reinvestigation clock (Phase 10).

Pure, side-effect-free helpers that compute the reinvestigation deadline for a
sent dispute and classify its state (awaiting / due-soon / overdue / responded).
Kept separate from the service so it can be unit-tested without a database and
reused by the case reinvestigation read model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

# FCRA §611 gives a CRA 30 days to complete a reinvestigation (extendable to 45
# in some cases). We track the base 30-day window; escalation is advisory.
CRA_REINVESTIGATION_DAYS = 30
DUE_SOON_WINDOW_DAYS = 7

ReinvestigationClockState = Literal[
    "not_sent",
    "awaiting",
    "due_soon",
    "overdue",
    "responded",
]


@dataclass(frozen=True)
class ReinvestigationClock:
    state: ReinvestigationClockState
    deadline: date | None
    days_remaining: int | None


def compute_reinvestigation_clock(
    *,
    last_dispute_date: date | None,
    today: date,
    response_recorded: bool,
    response_days: int = CRA_REINVESTIGATION_DAYS,
    due_soon_days: int = DUE_SOON_WINDOW_DAYS,
) -> ReinvestigationClock:
    """Classify the §611 reinvestigation window for a single tradeline.

    - ``responded``: a bureau/furnisher response has been recorded.
    - ``not_sent``: no dispute has been mailed yet (no ``last_dispute_date``).
    - ``overdue``: the 30-day window has elapsed with no recorded response.
    - ``due_soon``: within ``due_soon_days`` of the deadline.
    - ``awaiting``: sent, deadline still comfortably ahead.
    """
    deadline = last_dispute_date + timedelta(days=response_days) if last_dispute_date else None
    days_remaining = (deadline - today).days if deadline is not None else None

    if response_recorded:
        return ReinvestigationClock("responded", deadline, days_remaining)
    if last_dispute_date is None or deadline is None or days_remaining is None:
        return ReinvestigationClock("not_sent", None, None)
    if days_remaining < 0:
        return ReinvestigationClock("overdue", deadline, days_remaining)
    if days_remaining <= due_soon_days:
        return ReinvestigationClock("due_soon", deadline, days_remaining)
    return ReinvestigationClock("awaiting", deadline, days_remaining)
