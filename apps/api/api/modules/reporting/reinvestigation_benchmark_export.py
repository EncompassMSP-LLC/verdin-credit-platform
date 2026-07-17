"""CSV export for org-internal reinvestigation outcome benchmarks (aggregate rates only)."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Literal

from api.modules.reporting.schemas import (
    ReinvestigationOutcomeAnalytics,
    ReinvestigationOutcomeBenchmarkBureauBreakdown,
    ReinvestigationOutcomeBenchmarkRecipientBreakdown,
    ReinvestigationOutcomeBenchmarksResponse,
    ReinvestigationOutcomeRateDeltas,
)

ReinvestigationBenchmarkExportFormat = Literal["csv"]

_MEDIA_TYPES: dict[ReinvestigationBenchmarkExportFormat, str] = {
    "csv": "text/csv; charset=utf-8",
}


def export_filename() -> str:
    return "reinvestigation-outcome-benchmarks.csv"


def export_media_type(export_format: ReinvestigationBenchmarkExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def _rate_row(
    breakdown_type: str,
    breakdown_key: str,
    baseline: ReinvestigationOutcomeAnalytics,
    recent: ReinvestigationOutcomeAnalytics,
    deltas: ReinvestigationOutcomeRateDeltas,
) -> list[str | int | float]:
    return [
        breakdown_type,
        breakdown_key,
        baseline.total_responses,
        recent.total_responses,
        baseline.deletion_rate,
        recent.deletion_rate,
        deltas.deletion_rate,
        baseline.favorable_rate,
        recent.favorable_rate,
        deltas.favorable_rate,
        baseline.verification_rate,
        recent.verification_rate,
        deltas.verification_rate,
        baseline.correction_rate,
        recent.correction_rate,
        deltas.correction_rate,
        baseline.no_response_rate,
        recent.no_response_rate,
        deltas.no_response_rate,
    ]


def build_reinvestigation_benchmark_csv(
    benchmarks: ReinvestigationOutcomeBenchmarksResponse,
) -> str:
    """Serialize benchmarks to CSV with org aggregate and optional breakdown rows (no PII)."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "generated_at",
            benchmarks.generated_at.isoformat(),
            "scope",
            benchmarks.scope,
            "bureau_filter",
            benchmarks.bureau or "",
            "group_by",
            benchmarks.group_by or "",
            "baseline_start",
            benchmarks.baseline_period.start.isoformat(),
            "baseline_end",
            benchmarks.baseline_period.end.isoformat(),
            "baseline_days",
            benchmarks.baseline_period.window_days,
            "recent_start",
            benchmarks.recent_period.start.isoformat(),
            "recent_end",
            benchmarks.recent_period.end.isoformat(),
            "recent_days",
            benchmarks.recent_period.window_days,
        ]
    )
    writer.writerow([])
    writer.writerow(
        [
            "breakdown_type",
            "breakdown_key",
            "baseline_responses",
            "recent_responses",
            "baseline_deletion_rate",
            "recent_deletion_rate",
            "deletion_rate_delta",
            "baseline_favorable_rate",
            "recent_favorable_rate",
            "favorable_rate_delta",
            "baseline_verification_rate",
            "recent_verification_rate",
            "verification_rate_delta",
            "baseline_correction_rate",
            "recent_correction_rate",
            "correction_rate_delta",
            "baseline_no_response_rate",
            "recent_no_response_rate",
            "no_response_rate_delta",
        ]
    )
    writer.writerow(
        _rate_row(
            "organization",
            benchmarks.scope,
            benchmarks.baseline,
            benchmarks.recent,
            benchmarks.rate_deltas,
        )
    )
    for bureau_item in benchmarks.by_bureau:
        writer.writerow(_bureau_row(bureau_item))
    for recipient_item in benchmarks.by_recipient:
        writer.writerow(_recipient_row(recipient_item))
    return buffer.getvalue()


def _bureau_row(item: ReinvestigationOutcomeBenchmarkBureauBreakdown) -> list[str | int | float]:
    return _rate_row("bureau", item.bureau, item.baseline, item.recent, item.rate_deltas)


def _recipient_row(
    item: ReinvestigationOutcomeBenchmarkRecipientBreakdown,
) -> list[str | int | float]:
    return _rate_row("recipient", item.recipient, item.baseline, item.recent, item.rate_deltas)
