"""Predictive analytics helpers — historical outcome aggregate scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from api.core.feature_flags import FeatureFlag, is_feature_enabled

_RESOLVED_DISPUTE_STATUSES = frozenset({"corrected", "deleted"})


@dataclass(frozen=True)
class PredictiveAnalyticsStatus:
    enabled: bool
    ready: bool
    blockers: tuple[str, ...]


def get_predictive_analytics_status() -> PredictiveAnalyticsStatus:
    enabled = is_feature_enabled(FeatureFlag.ENABLE_PREDICTIVE_ANALYTICS)
    blockers: list[str] = []
    if not enabled:
        blockers.append("ENABLE_PREDICTIVE_ANALYTICS is false")
    return PredictiveAnalyticsStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        blockers=tuple(blockers),
    )


def compute_outcome_score(
    *,
    total_cases: int,
    cases_closed_90d: int,
    disputed_accounts: int,
    accounts_dispute_resolved: int,
    dispute_letters_sent: int,
) -> int:
    score = 0
    if total_cases > 0:
        closure_rate = min(cases_closed_90d / total_cases, 1.0)
        score += int(closure_rate * 40)
    if disputed_accounts > 0:
        resolution_rate = min(accounts_dispute_resolved / disputed_accounts, 1.0)
        score += int(resolution_rate * 40)
    if dispute_letters_sent > 0:
        score += 20
    return min(score, 100)


def build_predictive_outcomes(
    *,
    cases_by_status: dict[str, int],
    accounts_by_dispute_status: dict[str, int],
    dispute_letters_by_status: dict[str, int],
    cases_closed_30d: int,
    cases_closed_90d: int,
    accounts_dispute_resolved: int,
    dispute_letters_sent: int,
    last_refreshed_at: datetime | None = None,
) -> dict[str, Any]:
    total_cases = sum(cases_by_status.values())
    disputed_accounts = sum(
        count for status, count in accounts_by_dispute_status.items() if status != "not_started"
    )

    case_closure_rate_90d: float | None = None
    if total_cases > 0:
        case_closure_rate_90d = round((cases_closed_90d / total_cases) * 100, 2)

    dispute_resolution_rate: float | None = None
    if disputed_accounts > 0:
        dispute_resolution_rate = round(
            (accounts_dispute_resolved / disputed_accounts) * 100,
            2,
        )

    return {
        "cases_by_status": cases_by_status,
        "accounts_by_dispute_status": accounts_by_dispute_status,
        "dispute_letters_by_status": dispute_letters_by_status,
        "total_cases": total_cases,
        "disputed_accounts": disputed_accounts,
        "cases_closed_30d": cases_closed_30d,
        "cases_closed_90d": cases_closed_90d,
        "accounts_dispute_resolved": accounts_dispute_resolved,
        "dispute_letters_sent": dispute_letters_sent,
        "case_closure_rate_90d": case_closure_rate_90d,
        "dispute_resolution_rate": dispute_resolution_rate,
        "outcome_score": compute_outcome_score(
            total_cases=total_cases,
            cases_closed_90d=cases_closed_90d,
            disputed_accounts=disputed_accounts,
            accounts_dispute_resolved=accounts_dispute_resolved,
            dispute_letters_sent=dispute_letters_sent,
        ),
        "last_refreshed_at": last_refreshed_at,
    }


def count_resolved_dispute_accounts(accounts_by_dispute_status: dict[str, int]) -> int:
    return sum(
        count
        for status, count in accounts_by_dispute_status.items()
        if status in _RESOLVED_DISPUTE_STATUSES
    )


def count_disputed_accounts(accounts_by_dispute_status: dict[str, int]) -> int:
    return sum(
        count for status, count in accounts_by_dispute_status.items() if status != "not_started"
    )
