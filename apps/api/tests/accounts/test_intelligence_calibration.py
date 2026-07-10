"""Unit tests for calibrated account scoring."""

from api.modules.accounts.intelligence_calibration import (
    DiscrepancyScoringContext,
    calibrate_readiness_score,
    calibrate_risk_score,
)


def _context(**kwargs: object) -> DiscrepancyScoringContext:
    return DiscrepancyScoringContext(
        match_key=str(kwargs.get("match_key", "acme:1234")),
        classification=str(kwargs.get("classification", "balance_inconsistency")),
        confidence_score=int(kwargs.get("confidence_score", 80)),
        dispute_ready=bool(kwargs.get("dispute_ready", True)),
        requires_investigation=bool(kwargs.get("requires_investigation", False)),
        discrepancy_types=tuple(kwargs.get("discrepancy_types", ("balance_mismatch",))),  # type: ignore[arg-type]
        recommended_action=str(kwargs.get("recommended_action", "Prepare dispute")),
    )


def test_calibrate_risk_score_increases_for_discrepancy() -> None:
    base = 40
    calibrated = calibrate_risk_score(base, _context())
    assert calibrated > base


def test_calibrate_readiness_score_increases_when_dispute_ready() -> None:
    base = 60
    calibrated = calibrate_readiness_score(base, _context(dispute_ready=True))
    assert calibrated > base


def test_calibrate_readiness_score_decreases_when_investigation_required() -> None:
    base = 70
    calibrated = calibrate_readiness_score(
        base,
        _context(dispute_ready=False, requires_investigation=True),
    )
    assert calibrated < base
