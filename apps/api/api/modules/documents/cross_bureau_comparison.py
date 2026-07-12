"""Cross-bureau tradeline discrepancy detection for a case."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any, Literal

BUREAUS: tuple[str, ...] = ("experian", "equifax", "transunion")

DiscrepancyType = Literal[
    "consistent",
    "missing_from_bureau",
    "balance_mismatch",
    "status_mismatch",
    "past_due_mismatch",
    "dofd_mismatch",
]

Classification = Literal[
    "consistent",
    "cross_bureau_reporting_difference",
    "balance_inconsistency",
    "status_inconsistency",
    "reporting_inconsistency",
]

WorkflowTier = Literal["none", "investigation", "dispute"]

CauseLikelihood = Literal["most_likely", "possible", "less_likely"]

CLASSIFICATION_LABELS: dict[Classification, str] = {
    "consistent": "Consistent Across Bureaus",
    "cross_bureau_reporting_difference": "Cross-Bureau Reporting Difference",
    "balance_inconsistency": "Balance Reporting Inconsistency",
    "status_inconsistency": "Status Reporting Inconsistency",
    "reporting_inconsistency": "Multi-Field Reporting Inconsistency",
}

_STOP_WORDS = frozenset(
    {
        "inc",
        "llc",
        "corp",
        "ltd",
        "co",
        "company",
        "the",
        "na",
    }
)


@dataclass(frozen=True, slots=True)
class BureauTradelineSnapshot:
    bureau: str
    document_id: uuid.UUID
    creditor_name: str
    account_number_masked: str | None
    balance: float | None
    past_due_amount: float | None
    payment_status: str | None
    account_status: str | None
    account_type: str | None
    high_credit: float | None
    credit_limit: float | None
    open_date: str | None
    date_closed: str | None
    date_first_delinquency: str | None
    date_reported: str | None


@dataclass(frozen=True, slots=True)
class FieldDiff:
    field: str
    previous: str | float | None
    current: str | float | None


@dataclass(frozen=True, slots=True)
class PossibleCause:
    label: str
    likelihood: CauseLikelihood


@dataclass(frozen=True, slots=True)
class CrossBureauDiscrepancy:
    match_key: str
    creditor_name: str
    account_number_masked: str | None
    discrepancy_types: tuple[DiscrepancyType, ...]
    classification: Classification
    classification_label: str
    confidence_score: int
    workflow_tier: WorkflowTier
    bureaus_reporting: tuple[str, ...]
    bureaus_missing: tuple[str, ...]
    bureau_snapshots: tuple[BureauTradelineSnapshot, ...]
    field_diffs: tuple[FieldDiff, ...]
    possible_causes: tuple[PossibleCause, ...]
    recommended_next_step: str
    recommended_action: str
    requires_investigation: bool
    dispute_ready: bool
    is_actionable: bool


@dataclass(frozen=True, slots=True)
class CrossBureauComparisonResult:
    case_id: uuid.UUID
    reports_compared: tuple[str, ...]
    document_ids_by_bureau: dict[str, uuid.UUID]
    summary: dict[str, int]
    discrepancies: tuple[CrossBureauDiscrepancy, ...]


def normalize_creditor(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    tokens = [token for token in cleaned.split() if token and token not in _STOP_WORDS]
    return "".join(tokens)


def account_suffix(account_number_masked: str | None) -> str:
    if not account_number_masked:
        return ""
    digits = re.sub(r"\D", "", account_number_masked)
    return digits[-4:] if len(digits) >= 4 else digits


def tradeline_match_key(creditor_name: str, account_number_masked: str | None) -> str:
    creditor = normalize_creditor(creditor_name)
    suffix = account_suffix(account_number_masked)
    if creditor and suffix:
        return f"{creditor}:{suffix}"
    return creditor or "unknown"


def _float_or_none(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").replace("$", ""))
        except ValueError:
            return None
    return None


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _normalize_status(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.lower()
    if "charge" in normalized and "off" in normalized:
        return "charge_off"
    if "collection" in normalized:
        return "collection"
    if "current" in normalized or "pays as agreed" in normalized:
        return "current"
    if "late" in normalized or "past due" in normalized:
        return "late"
    return re.sub(r"[^a-z0-9 ]", " ", normalized).strip()


_CROSS_BUREAU_COMPARE_FIELDS: tuple[str, ...] = (
    "balance",
    "past_due_amount",
    "payment_status",
    "account_status",
    "high_credit",
    "credit_limit",
    "open_date",
    "date_closed",
    "date_first_delinquency",
    "date_reported",
)


def _cross_bureau_field_diffs(
    snapshots: tuple[BureauTradelineSnapshot, ...],
) -> tuple[FieldDiff, ...]:
    if len(snapshots) < 2:
        return ()
    diffs: list[FieldDiff] = []
    baseline = snapshots[0]
    for field_name in _CROSS_BUREAU_COMPARE_FIELDS:
        values = {getattr(snapshot, field_name) for snapshot in snapshots}
        values.discard(None)
        values.discard("")
        if len(values) > 1:
            for snapshot in snapshots[1:]:
                previous = getattr(baseline, field_name)
                current = getattr(snapshot, field_name)
                if previous != current:
                    diffs.append(
                        FieldDiff(
                            field=f"{field_name}:{baseline.bureau}->{snapshot.bureau}",
                            previous=previous,
                            current=current,
                        )
                    )
    return tuple(diffs)


def _snapshot_from_account(
    *,
    bureau: str,
    document_id: uuid.UUID,
    account: dict[str, Any],
) -> BureauTradelineSnapshot | None:
    creditor_name = _string_or_none(account.get("creditor_name"))
    if not creditor_name:
        return None
    return BureauTradelineSnapshot(
        bureau=bureau,
        document_id=document_id,
        creditor_name=creditor_name,
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        balance=_float_or_none(account.get("balance")),
        past_due_amount=_float_or_none(account.get("past_due_amount")),
        payment_status=_string_or_none(account.get("payment_status")),
        account_status=_string_or_none(account.get("account_status")),
        account_type=_string_or_none(account.get("account_type")),
        high_credit=_float_or_none(account.get("high_credit")),
        credit_limit=_float_or_none(account.get("credit_limit")),
        open_date=_string_or_none(account.get("open_date")),
        date_closed=_string_or_none(account.get("date_closed")),
        date_first_delinquency=_string_or_none(account.get("date_first_delinquency")),
        date_reported=_string_or_none(account.get("date_reported")),
    )


def _has_strong_match_key(match_key: str) -> bool:
    return ":" in match_key and match_key not in {"unknown", ":unknown"}


def _classify_discrepancy(
    discrepancy_types: tuple[DiscrepancyType, ...],
) -> tuple[Classification, WorkflowTier]:
    if discrepancy_types == ("consistent",):
        return "consistent", "none"

    has_missing = "missing_from_bureau" in discrepancy_types
    has_balance = "balance_mismatch" in discrepancy_types
    has_status = "status_mismatch" in discrepancy_types
    has_past_due = "past_due_mismatch" in discrepancy_types
    has_dofd = "dofd_mismatch" in discrepancy_types

    field_mismatch_count = sum(
        1 for flag in (has_balance, has_status, has_past_due, has_dofd) if flag
    )
    if field_mismatch_count >= 2:
        return "reporting_inconsistency", "dispute"
    if has_balance or has_past_due:
        return "balance_inconsistency", "dispute"
    if has_status or has_dofd:
        return "status_inconsistency", "dispute"
    if has_missing:
        return "cross_bureau_reporting_difference", "investigation"
    return "reporting_inconsistency", "investigation"


def _confidence_score(
    *,
    classification: Classification,
    discrepancy_types: tuple[DiscrepancyType, ...],
    match_key: str,
    missing_bureaus: tuple[str, ...],
    reports_compared_count: int,
    snapshots: tuple[BureauTradelineSnapshot, ...],
) -> int:
    if classification == "consistent":
        return 100

    score = 45

    if _has_strong_match_key(match_key):
        score += 28
    elif match_key not in {"", "unknown"}:
        score += 12

    if reports_compared_count >= 3:
        score += 10
    elif reports_compared_count == 2:
        score += 5

    if "balance_mismatch" in discrepancy_types:
        balances = [snapshot.balance for snapshot in snapshots if snapshot.balance is not None]
        if len(balances) > 1:
            spread = max(balances) - min(balances)
            average = sum(balances) / len(balances)
            if average > 0 and spread / average > 0.05:
                score += 18
            else:
                score += 10

    if "status_mismatch" in discrepancy_types:
        score += 14

    if "past_due_mismatch" in discrepancy_types:
        score += 12

    if "dofd_mismatch" in discrepancy_types:
        score += 16

    if "missing_from_bureau" in discrepancy_types:
        if len(missing_bureaus) >= 2:
            score += 6
        else:
            score += 3

    if classification == "cross_bureau_reporting_difference":
        score = min(score, 88)

    return min(100, max(0, score))


def _possible_causes(
    *,
    classification: Classification,
    match_key: str,
    missing_bureaus: tuple[str, ...],
) -> tuple[PossibleCause, ...]:
    if classification == "consistent":
        return ()

    if classification == "cross_bureau_reporting_difference":
        causes: list[PossibleCause] = [
            PossibleCause(
                label="Creditor reports only to selected bureaus",
                likelihood="most_likely",
            ),
            PossibleCause(
                label="Reporting delay between credit bureaus",
                likelihood="possible",
            ),
        ]
        if not _has_strong_match_key(match_key):
            causes.append(
                PossibleCause(
                    label="Tradeline matching issue (creditor name or account number differs)",
                    likelihood="possible",
                )
            )
        causes.append(
            PossibleCause(
                label="Potential reporting inconsistency",
                likelihood="less_likely" if _has_strong_match_key(match_key) else "possible",
            )
        )
        return tuple(causes)

    if classification == "balance_inconsistency":
        return (
            PossibleCause(
                label="Furnisher reported different balances to each bureau",
                likelihood="most_likely",
            ),
            PossibleCause(
                label="One bureau report is stale relative to another",
                likelihood="possible",
            ),
            PossibleCause(
                label="Parsed balance mismatch from report formatting",
                likelihood="less_likely",
            ),
        )

    if classification == "status_inconsistency":
        return (
            PossibleCause(
                label="Payment status coded differently across bureaus",
                likelihood="most_likely",
            ),
            PossibleCause(
                label="Reporting lag after a status change",
                likelihood="possible",
            ),
            PossibleCause(
                label="Potential inaccurate status reporting",
                likelihood="possible",
            ),
        )

    return (
        PossibleCause(
            label="Multiple reporting fields disagree across bureaus",
            likelihood="most_likely",
        ),
        PossibleCause(
            label="Mixed reporting delays and furnisher inconsistencies",
            likelihood="possible",
        ),
        PossibleCause(
            label="Tradeline matching grouped unrelated accounts",
            likelihood="less_likely",
        ),
    )


def _format_bureau_list(bureaus: tuple[str, ...]) -> str:
    return ", ".join(bureau.replace("_", " ").title() for bureau in bureaus)


def _recommended_next_step(
    *,
    classification: Classification,
    creditor_name: str,
    bureaus_missing: tuple[str, ...],
) -> str:
    if classification == "consistent":
        return "No further cross-bureau review needed."

    if classification == "cross_bureau_reporting_difference":
        missing = _format_bureau_list(bureaus_missing)
        return (
            f"Verify whether {creditor_name} reports to all compared bureaus and compare report "
            f"dates before considering a dispute. Tradeline absent from: {missing}."
        )

    if classification == "balance_inconsistency":
        return (
            f"Compare balances and report dates for {creditor_name} across bureaus. "
            "Dispute only if the difference reflects inaccurate reporting."
        )

    if classification == "status_inconsistency":
        return (
            f"Review payment status codes for {creditor_name} on each bureau. "
            "Confirm whether the statuses describe the same account condition."
        )

    return f"Review all reporting fields for {creditor_name} across bureaus before preparing a dispute."


def _recommended_action(
    *,
    classification: Classification,
    recommended_next_step: str,
    workflow_tier: WorkflowTier,
) -> str:
    if workflow_tier == "none":
        return recommended_next_step
    if workflow_tier == "investigation":
        return recommended_next_step
    return f"{recommended_next_step} If verified inaccurate, prepare a bureau dispute."


def compare_cross_bureau_reports(
    *,
    case_id: uuid.UUID,
    reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, object]]],
) -> CrossBureauComparisonResult:
    """Compare the latest parsed report per bureau and surface tradeline discrepancies."""
    grouped: dict[str, list[BureauTradelineSnapshot]] = {}

    for bureau, (document_id, parsed_report) in reports_by_bureau.items():
        accounts = parsed_report.get("accounts")
        if not isinstance(accounts, list):
            continue
        for account in accounts:
            if not isinstance(account, dict):
                continue
            snapshot = _snapshot_from_account(
                bureau=bureau,
                document_id=document_id,
                account=account,
            )
            if snapshot is None:
                continue
            key = tradeline_match_key(snapshot.creditor_name, snapshot.account_number_masked)
            grouped.setdefault(key, []).append(snapshot)

    available_bureaus = tuple(sorted(reports_by_bureau))
    document_ids_by_bureau = {
        bureau: document_id for bureau, (document_id, _) in reports_by_bureau.items()
    }
    discrepancies: list[CrossBureauDiscrepancy] = []

    for match_key, snapshots in sorted(grouped.items()):
        reporting = {snapshot.bureau for snapshot in snapshots}
        missing_bureaus = tuple(bureau for bureau in available_bureaus if bureau not in reporting)
        types: list[DiscrepancyType] = []

        if missing_bureaus:
            types.append("missing_from_bureau")

        balances = {snapshot.balance for snapshot in snapshots if snapshot.balance is not None}
        if len(balances) > 1:
            types.append("balance_mismatch")

        statuses = {
            _normalize_status(snapshot.payment_status or snapshot.account_status)
            for snapshot in snapshots
            if snapshot.payment_status or snapshot.account_status
        }
        statuses.discard("")
        if len(statuses) > 1:
            types.append("status_mismatch")

        past_dues = {
            snapshot.past_due_amount
            for snapshot in snapshots
            if snapshot.past_due_amount is not None
        }
        if len(past_dues) > 1:
            types.append("past_due_mismatch")

        dofds = {
            (snapshot.date_first_delinquency or "").strip().lower()
            for snapshot in snapshots
            if snapshot.date_first_delinquency
        }
        dofds.discard("")
        if len(dofds) > 1:
            types.append("dofd_mismatch")

        if not types:
            types.append("consistent")

        discrepancy_types = tuple(types)
        classification, workflow_tier = _classify_discrepancy(discrepancy_types)
        classification_label = CLASSIFICATION_LABELS[classification]

        creditor_name = snapshots[0].creditor_name
        account_number_masked = next(
            (
                snapshot.account_number_masked
                for snapshot in snapshots
                if snapshot.account_number_masked
            ),
            snapshots[0].account_number_masked,
        )
        bureau_snapshots = tuple(sorted(snapshots, key=lambda item: item.bureau))
        bureaus_reporting = tuple(sorted(reporting))
        field_diffs = _cross_bureau_field_diffs(bureau_snapshots)

        confidence_score = _confidence_score(
            classification=classification,
            discrepancy_types=discrepancy_types,
            match_key=match_key,
            missing_bureaus=missing_bureaus,
            reports_compared_count=len(available_bureaus),
            snapshots=bureau_snapshots,
        )
        possible_causes = _possible_causes(
            classification=classification,
            match_key=match_key,
            missing_bureaus=missing_bureaus,
        )
        recommended_next_step = _recommended_next_step(
            classification=classification,
            creditor_name=creditor_name,
            bureaus_missing=missing_bureaus,
        )
        recommended_action = _recommended_action(
            classification=classification,
            recommended_next_step=recommended_next_step,
            workflow_tier=workflow_tier,
        )

        requires_investigation = workflow_tier == "investigation"
        dispute_ready = workflow_tier == "dispute"
        is_actionable = workflow_tier != "none"

        discrepancies.append(
            CrossBureauDiscrepancy(
                match_key=match_key,
                creditor_name=creditor_name,
                account_number_masked=account_number_masked,
                discrepancy_types=discrepancy_types,
                classification=classification,
                classification_label=classification_label,
                confidence_score=confidence_score,
                workflow_tier=workflow_tier,
                bureaus_reporting=bureaus_reporting,
                bureaus_missing=missing_bureaus,
                bureau_snapshots=bureau_snapshots,
                field_diffs=field_diffs,
                possible_causes=possible_causes,
                recommended_next_step=recommended_next_step,
                recommended_action=recommended_action,
                requires_investigation=requires_investigation,
                dispute_ready=dispute_ready,
                is_actionable=is_actionable,
            )
        )

    summary = {
        "total_tradelines": len(discrepancies),
        "actionable": sum(1 for item in discrepancies if item.is_actionable),
        "investigation_needed": sum(1 for item in discrepancies if item.requires_investigation),
        "dispute_ready": sum(1 for item in discrepancies if item.dispute_ready),
        "consistent": sum(1 for item in discrepancies if item.discrepancy_types == ("consistent",)),
        "missing_from_bureau": sum(
            1 for item in discrepancies if "missing_from_bureau" in item.discrepancy_types
        ),
        "balance_mismatch": sum(
            1 for item in discrepancies if "balance_mismatch" in item.discrepancy_types
        ),
        "status_mismatch": sum(
            1 for item in discrepancies if "status_mismatch" in item.discrepancy_types
        ),
        "past_due_mismatch": sum(
            1 for item in discrepancies if "past_due_mismatch" in item.discrepancy_types
        ),
        "dofd_mismatch": sum(
            1 for item in discrepancies if "dofd_mismatch" in item.discrepancy_types
        ),
    }

    return CrossBureauComparisonResult(
        case_id=case_id,
        reports_compared=available_bureaus,
        document_ids_by_bureau=document_ids_by_bureau,
        summary=summary,
        discrepancies=tuple(discrepancies),
    )
