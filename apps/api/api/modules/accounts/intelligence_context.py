"""Cross-bureau context helpers for account intelligence."""

from __future__ import annotations

import uuid
from typing import Any

from api.modules.accounts.intelligence_calibration import DiscrepancyScoringContext
from api.modules.accounts.models import Account
from api.modules.documents.cross_bureau_comparison import (
    CrossBureauComparisonResult,
    CrossBureauDiscrepancy,
    compare_cross_bureau_reports,
    tradeline_match_key,
)


def discrepancy_context_from_item(item: CrossBureauDiscrepancy) -> DiscrepancyScoringContext:
    return DiscrepancyScoringContext(
        match_key=item.match_key,
        classification=item.classification,
        confidence_score=item.confidence_score,
        dispute_ready=item.dispute_ready,
        requires_investigation=item.requires_investigation,
        discrepancy_types=item.discrepancy_types,
        recommended_action=item.recommended_action,
    )


def build_discrepancy_context_map(
    discrepancies: tuple[CrossBureauDiscrepancy, ...],
) -> dict[str, DiscrepancyScoringContext]:
    return {item.match_key: discrepancy_context_from_item(item) for item in discrepancies}


def compare_case_reports(
    *,
    case_id: uuid.UUID,
    reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, object]]],
) -> CrossBureauComparisonResult:
    return compare_cross_bureau_reports(
        case_id=case_id,
        reports_by_bureau=reports_by_bureau,
    )


def discrepancy_context_for_account(
    account: Account,
    context_map: dict[str, DiscrepancyScoringContext],
) -> DiscrepancyScoringContext | None:
    match_key = tradeline_match_key(account.creditor_name, account.account_number_masked)
    return context_map.get(match_key)


def cross_bureau_summary_payload(result_summary: dict[str, Any]) -> dict[str, int]:
    return {
        "actionable_discrepancies": int(result_summary.get("actionable", 0)),
        "dispute_ready_discrepancies": int(result_summary.get("dispute_ready", 0)),
        "investigation_needed": int(result_summary.get("investigation_needed", 0)),
        "consistent_tradelines": int(result_summary.get("consistent", 0)),
        "total_tradelines": int(result_summary.get("total_tradelines", 0)),
    }
