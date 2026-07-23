"""Deterministic Lending Readiness Score™ compose (Vol 22).

Advisory only — not FICO, not underwriting. No LLM. No bureau I/O.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from api.modules.accounts.intelligence import (
    CRITICAL_RISK_THRESHOLD,
    apply_account_intelligence,
    recommend_next_action,
)
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    DisputeStatus,
    PaymentStatus,
)

FORMULA_VERSION = "lrs.v1.0"
SCHEMA_VERSION = "lrs.v1"
SCORE_VERSION = "lrs.v1"

ADVISORY_DISCLAIMER = (
    "Lending Readiness Score™ is an advisory tool for organizing credit and "
    "documentation work toward a mortgage conversation. It is not a credit score "
    "from a consumer reporting agency, not an underwriting decision, and not a "
    "guarantee of loan approval or terms."
)

DIMENSION_WEIGHTS: dict[str, float] = {
    "payment_derogs": 0.25,
    "utilization": 0.15,
    "public_records": 0.15,
    "inquiries": 0.10,
    "cross_bureau": 0.10,
    "identity_integrity": 0.10,
    "documentation": 0.10,
    "remediation": 0.05,
}

DIMENSION_LABELS: dict[str, str] = {
    "payment_derogs": "Payment / derogs",
    "utilization": "Utilization",
    "public_records": "Public records / severe",
    "inquiries": "Inquiries / new credit",
    "cross_bureau": "Cross-bureau consistency",
    "identity_integrity": "Identity / file integrity",
    "documentation": "Documentation completeness",
    "remediation": "Dispute / remediation progress",
}

_SEVERE_STATUSES = {
    AccountStatus.COLLECTION,
    AccountStatus.CHARGE_OFF,
    AccountStatus.REPOSSESSION,
    AccountStatus.FORECLOSURE,
}
_SEVERE_PAYMENTS = {
    PaymentStatus.CHARGE_OFF,
    PaymentStatus.COLLECTION,
    PaymentStatus.REPOSSESSION,
    PaymentStatus.FORECLOSURE,
    PaymentStatus.LATE_90,
    PaymentStatus.LATE_120,
}


@dataclass(frozen=True)
class ComposedCreditAnalysis:
    borrower_readiness_score: int
    mortgage_readiness_score: int
    band: str
    reports_evaluated: int
    tradelines_evaluated: int
    inputs_hash: str
    formula_version: str
    score_version: str
    schema_version: str
    payload: dict[str, Any]


def _clamp(score: float) -> int:
    return max(0, min(100, int(round(score))))


def score_to_band(score: int) -> str:
    if score >= 85:
        return "lending_ready"
    if score >= 65:
        return "near_ready"
    if score >= 40:
        return "progressing"
    return "building"


def _mean(values: list[float], default: float) -> float:
    if not values:
        return default
    return sum(values) / len(values)


def _utilization_score(accounts: list[Account]) -> float:
    ratios: list[float] = []
    for account in accounts:
        limit = account.credit_limit
        balance = account.balance
        if limit is None or limit <= 0 or balance is None:
            continue
        ratio = float(balance / limit)
        if ratio >= 0.9:
            ratios.append(20.0)
        elif ratio >= 0.7:
            ratios.append(40.0)
        elif ratio >= 0.5:
            ratios.append(60.0)
        elif ratio >= 0.3:
            ratios.append(80.0)
        else:
            ratios.append(95.0)
    return _mean(ratios, 70.0)


def _payment_derogs_score(accounts: list[Account]) -> float:
    if not accounts:
        return 35.0
    scores: list[float] = []
    for account in accounts:
        risk = float(account.risk_score if account.risk_score is not None else 50)
        scores.append(max(0.0, 100.0 - risk))
        if account.account_status in _SEVERE_STATUSES or account.payment_status in _SEVERE_PAYMENTS:
            scores.append(25.0)
    return _mean(scores, 40.0)


def _public_records_score(accounts: list[Account]) -> float:
    severe = sum(
        1
        for a in accounts
        if a.account_status in _SEVERE_STATUSES or a.payment_status in _SEVERE_PAYMENTS
    )
    if severe == 0:
        return 75.0
    if severe == 1:
        return 45.0
    return 25.0


def _identity_integrity_score(accounts: list[Account]) -> float:
    if not accounts:
        return 40.0
    unknown = sum(1 for a in accounts if a.bureau == AccountBureau.UNKNOWN)
    evidence_needed = sum(1 for a in accounts if a.dispute_status == DisputeStatus.EVIDENCE_NEEDED)
    penalty = min(40.0, unknown * 8.0 + evidence_needed * 10.0)
    return max(20.0, 80.0 - penalty)


def _documentation_score(accounts: list[Account]) -> float:
    if not accounts:
        return 30.0
    return 70.0


def _remediation_score(accounts: list[Account]) -> float:
    if not accounts:
        return 30.0
    values = [float(a.readiness_score) for a in accounts if a.readiness_score is not None]
    return _mean(values, 40.0)


def _cross_bureau_score(accounts: list[Account]) -> float:
    bureaus = {a.bureau for a in accounts if a.bureau != AccountBureau.UNKNOWN}
    if len(bureaus) >= 3:
        return 85.0
    if len(bureaus) == 2:
        return 70.0
    if len(bureaus) == 1:
        return 55.0
    return 45.0


def _build_blockers(accounts: list[Account]) -> list[dict[str, str]]:
    ranked = sorted(
        accounts,
        key=lambda a: (
            -(a.risk_score or 0),
            a.dispute_status == DisputeStatus.EVIDENCE_NEEDED,
        ),
        reverse=False,
    )
    blockers: list[dict[str, str]] = []
    for account in ranked:
        risk = account.risk_score or 0
        severe = (
            account.account_status in _SEVERE_STATUSES
            or account.payment_status in _SEVERE_PAYMENTS
            or risk >= CRITICAL_RISK_THRESHOLD
            or account.dispute_status == DisputeStatus.EVIDENCE_NEEDED
        )
        if not severe:
            continue
        action = account.ai_recommended_next_action or recommend_next_action(account)
        blockers.append(
            {
                "id": str(account.id),
                "title": f"{account.creditor_name} ({account.bureau.value})",
                "impact": (
                    "High-risk or incomplete tradeline may delay lending readiness."
                    if risk >= CRITICAL_RISK_THRESHOLD
                    else "Needs staff-mediated remediation or evidence before packaging."
                ),
                "action": action,
            }
        )
        if len(blockers) >= 5:
            break
    if not accounts:
        blockers.append(
            {
                "id": "no-tradelines",
                "title": "No tradelines analyzed",
                "impact": "Upload and parse credit reports so readiness can be calculated.",
                "action": "Ask your advisor to import bureau reports for this case.",
            }
        )
    return blockers


def _account_snapshots(accounts: list[Account]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for account in accounts:
        rows.append(
            {
                "id": str(account.id),
                "creditor_label": account.creditor_name,
                "bureau": account.bureau.value,
                "readiness_score": account.readiness_score,
                "risk_score": account.risk_score,
                "dispute_status": account.dispute_status.value,
                "recommended_action": account.ai_recommended_next_action
                or recommend_next_action(account),
            }
        )
    return rows


def _inputs_hash(accounts: list[Account], overall: int) -> str:
    material = [
        {
            "id": str(a.id),
            "readiness": a.readiness_score,
            "risk": a.risk_score,
            "status": a.dispute_status.value,
            "bureau": a.bureau.value,
            "balance": str(a.balance) if isinstance(a.balance, Decimal) else a.balance,
            "limit": str(a.credit_limit) if isinstance(a.credit_limit, Decimal) else a.credit_limit,
        }
        for a in sorted(accounts, key=lambda x: str(x.id))
    ]
    raw = json.dumps({"accounts": material, "overall": overall, "formula": FORMULA_VERSION})
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def compose_credit_analysis(accounts: list[Account]) -> ComposedCreditAnalysis:
    """Compose advisory readiness from case tradelines (mutates accounts with intelligence)."""
    for account in accounts:
        apply_account_intelligence(account)

    dims = {
        "payment_derogs": _payment_derogs_score(accounts),
        "utilization": _utilization_score(accounts),
        "public_records": _public_records_score(accounts),
        "inquiries": 70.0,  # inquiry entity not modeled in v1
        "cross_bureau": _cross_bureau_score(accounts),
        "identity_integrity": _identity_integrity_score(accounts),
        "documentation": _documentation_score(accounts),
        "remediation": _remediation_score(accounts),
    }
    if not accounts:
        overall = 25
    else:
        overall = _clamp(sum(dims[key] * DIMENSION_WEIGHTS[key] for key in DIMENSION_WEIGHTS))
        # Partial bureau coverage soft penalty
        bureaus = {a.bureau for a in accounts if a.bureau != AccountBureau.UNKNOWN}
        if len(bureaus) < 3:
            overall = _clamp(overall - (3 - len(bureaus)) * 3)

    band = score_to_band(overall)
    dimensions = [
        {
            "key": key,
            "label": DIMENSION_LABELS[key],
            "score": _clamp(dims[key]),
            "weight": DIMENSION_WEIGHTS[key],
        }
        for key in DIMENSION_WEIGHTS
    ]
    payload = {
        "disclaimer": ADVISORY_DISCLAIMER,
        "dimensions": dimensions,
        "blockers": _build_blockers(accounts),
        "accounts": _account_snapshots(accounts),
        "trend": None,
        "partial_bureau_coverage": len(
            {a.bureau for a in accounts if a.bureau != AccountBureau.UNKNOWN}
        )
        < 3,
        "formula_version": FORMULA_VERSION,
        "score_version": SCORE_VERSION,
    }
    return ComposedCreditAnalysis(
        borrower_readiness_score=overall,
        mortgage_readiness_score=overall,
        band=band,
        reports_evaluated=len({a.bureau for a in accounts if a.bureau != AccountBureau.UNKNOWN}),
        tradelines_evaluated=len(accounts),
        inputs_hash=_inputs_hash(accounts, overall),
        formula_version=FORMULA_VERSION,
        score_version=SCORE_VERSION,
        schema_version=SCHEMA_VERSION,
        payload=payload,
    )
