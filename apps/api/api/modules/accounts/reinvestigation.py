"""FCRA §611 reinvestigation clock (Phase 10).

Pure, side-effect-free helpers that compute the reinvestigation deadline for a
sent dispute and classify its state (awaiting / due-soon / overdue / responded).
Kept separate from the service so it can be unit-tested without a database and
reused by the case reinvestigation read model.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

# FCRA §611(a)(1)(A) gives a CRA 30 days to complete a reinvestigation.
# §611(a)(1)(B) extends the window to 45 days when the consumer supplies
# additional relevant information during the initial 30-day period.
CRA_REINVESTIGATION_DAYS = 30
EXTENDED_REINVESTIGATION_DAYS = 45
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
    extended: bool = False


def compute_reinvestigation_clock(
    *,
    last_dispute_date: date | None,
    today: date,
    response_recorded: bool,
    extended: bool = False,
    response_days: int = CRA_REINVESTIGATION_DAYS,
    extended_days: int = EXTENDED_REINVESTIGATION_DAYS,
    due_soon_days: int = DUE_SOON_WINDOW_DAYS,
) -> ReinvestigationClock:
    """Classify the §611 reinvestigation window for a single tradeline.

    - ``responded``: a bureau/furnisher response has been recorded.
    - ``not_sent``: no dispute has been mailed yet (no ``last_dispute_date``).
    - ``overdue``: the reinvestigation window has elapsed with no recorded response.
    - ``due_soon``: within ``due_soon_days`` of the deadline.
    - ``awaiting``: sent, deadline still comfortably ahead.

    When ``extended`` is set the §611(a)(1)(B) 45-day window is used instead of
    the base 30-day window (the consumer supplied information mid-reinvestigation).
    """
    window_days = extended_days if extended else response_days
    deadline = last_dispute_date + timedelta(days=window_days) if last_dispute_date else None
    days_remaining = (deadline - today).days if deadline is not None else None

    if response_recorded:
        return ReinvestigationClock("responded", deadline, days_remaining, extended)
    if last_dispute_date is None or deadline is None or days_remaining is None:
        return ReinvestigationClock("not_sent", None, None, extended)
    if days_remaining < 0:
        return ReinvestigationClock("overdue", deadline, days_remaining, extended)
    if days_remaining <= due_soon_days:
        return ReinvestigationClock("due_soon", deadline, days_remaining, extended)
    return ReinvestigationClock("awaiting", deadline, days_remaining, extended)


def document_extends_window(
    *,
    clock_start_date: date | None,
    document_dates: Iterable[date],
    initial_window_days: int = CRA_REINVESTIGATION_DAYS,
) -> bool:
    """Whether a consumer document extends the §611 window to 45 days.

    §611(a)(1)(B) extends the reinvestigation window when the consumer supplies
    additional relevant information during the initial 30-day period. We treat any
    case/account document uploaded strictly after the clock start and on or before
    the initial deadline as that supplemental information. Purely a computed signal
    — never files anything or contacts a bureau.
    """
    if clock_start_date is None:
        return False
    window_end = clock_start_date + timedelta(days=initial_window_days)
    return any(clock_start_date < doc_date <= window_end for doc_date in document_dates)
