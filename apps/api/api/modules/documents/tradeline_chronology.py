"""Multi-snapshot tradeline reporting chronology (Phase 4 scaffold).

Builds chronological histories for matched tradelines across stored parsed
credit reports for a case. Investigator aid for spotting re-aging, balance
rebounds, and status transitions over time — not a substitute for full
report-page evidence review.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from api.modules.documents.cross_bureau_comparison import tradeline_match_key

Severity = Literal["low", "medium", "high"]
EventType = Literal[
    "appeared",
    "disappeared",
    "balance_increased",
    "balance_decreased",
    "past_due_changed",
    "status_changed",
    "dofd_changed",
    "date_closed_changed",
    "field_changed",
]

_TRACKED_FIELDS: tuple[str, ...] = (
    "balance",
    "past_due_amount",
    "payment_status",
    "account_status",
    "date_first_delinquency",
    "date_closed",
    "remarks",
    "high_credit",
    "credit_limit",
)

_DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y")


@dataclass(frozen=True, slots=True)
class ReportSnapshotInput:
    document_id: uuid.UUID
    bureau: str
    parsed_at: datetime
    parsed_report: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ChronologySnapshot:
    document_id: uuid.UUID
    parsed_at: datetime
    as_of_date: str | None
    present: bool
    creditor_name: str | None
    account_number_masked: str | None
    balance: float | None
    past_due_amount: float | None
    account_status: str | None
    payment_status: str | None
    date_first_delinquency: str | None
    date_closed: str | None
    remarks: str | None
    high_credit: float | None
    credit_limit: float | None


@dataclass(frozen=True, slots=True)
class ChronologyEvent:
    event_type: EventType
    severity: Severity
    field: str | None
    from_document_id: uuid.UUID | None
    to_document_id: uuid.UUID
    from_parsed_at: datetime | None
    to_parsed_at: datetime
    previous: str | float | None
    current: str | float | None
    summary: str


@dataclass(frozen=True, slots=True)
class TradelineChronology:
    match_key: str
    bureau: str
    creditor_name: str | None
    account_number_masked: str | None
    snapshot_count: int
    event_count: int
    snapshots: tuple[ChronologySnapshot, ...]
    events: tuple[ChronologyEvent, ...]


@dataclass(frozen=True, slots=True)
class CaseTradelineChronologyResult:
    case_id: uuid.UUID
    reports_evaluated: int
    bureaus: tuple[str, ...]
    summary: dict[str, int]
    tradelines: tuple[TradelineChronology, ...]


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _float_or_none(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").replace("$", ""))
        except ValueError:
            return None
    return None


def _parse_date(value: object) -> datetime | None:
    raw = _string_or_none(value)
    if not raw:
        return None
    if "T" in raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            raw = raw.split("T", 1)[0]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw[:10] if fmt == "%Y-%m-%d" else raw, fmt)
        except ValueError:
            continue
    return None


def _resolve_as_of(account: dict[str, Any], report: dict[str, Any]) -> str | None:
    reported = _parse_date(account.get("date_reported"))
    if reported is not None:
        return reported.date().isoformat()
    metadata = report.get("metadata")
    if isinstance(metadata, dict):
        parsed_at = _parse_date(metadata.get("parsed_at"))
        if parsed_at is not None:
            return parsed_at.date().isoformat()
    return None


def _field_value(account: dict[str, Any] | None, field_name: str) -> str | float | None:
    if account is None:
        return None
    if field_name in {"balance", "past_due_amount", "high_credit", "credit_limit"}:
        return _float_or_none(account.get(field_name))
    return _string_or_none(account.get(field_name))


def _snapshot_from_account(
    *,
    document_id: uuid.UUID,
    parsed_at: datetime,
    report: dict[str, Any],
    account: dict[str, Any] | None,
) -> ChronologySnapshot:
    if account is None:
        return ChronologySnapshot(
            document_id=document_id,
            parsed_at=parsed_at,
            as_of_date=None,
            present=False,
            creditor_name=None,
            account_number_masked=None,
            balance=None,
            past_due_amount=None,
            account_status=None,
            payment_status=None,
            date_first_delinquency=None,
            date_closed=None,
            remarks=None,
            high_credit=None,
            credit_limit=None,
        )
    return ChronologySnapshot(
        document_id=document_id,
        parsed_at=parsed_at,
        as_of_date=_resolve_as_of(account, report),
        present=True,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        balance=_float_or_none(account.get("balance")),
        past_due_amount=_float_or_none(account.get("past_due_amount")),
        account_status=_string_or_none(account.get("account_status")),
        payment_status=_string_or_none(account.get("payment_status")),
        date_first_delinquency=_string_or_none(account.get("date_first_delinquency")),
        date_closed=_string_or_none(account.get("date_closed")),
        remarks=_string_or_none(account.get("remarks")),
        high_credit=_float_or_none(account.get("high_credit")),
        credit_limit=_float_or_none(account.get("credit_limit")),
    )


def _event_for_field_change(
    *,
    field: str,
    previous: str | float | None,
    current: str | float | None,
    from_document_id: uuid.UUID,
    to_document_id: uuid.UUID,
    from_parsed_at: datetime,
    to_parsed_at: datetime,
) -> ChronologyEvent:
    event_type: EventType = "field_changed"
    severity: Severity = "low"
    summary = f"{field} changed"

    if field == "balance":
        prev_f = previous if isinstance(previous, int | float) else None
        curr_f = current if isinstance(current, int | float) else None
        if prev_f is not None and curr_f is not None and curr_f > prev_f:
            event_type = "balance_increased"
            severity = "high"
            summary = f"Balance increased from {prev_f} to {curr_f}"
        elif prev_f is not None and curr_f is not None and curr_f < prev_f:
            event_type = "balance_decreased"
            severity = "medium"
            summary = f"Balance decreased from {prev_f} to {curr_f}"
        else:
            event_type = "field_changed"
            severity = "medium"
            summary = f"Balance changed from {previous} to {current}"
    elif field == "past_due_amount":
        event_type = "past_due_changed"
        severity = "medium"
        summary = f"Past due changed from {previous} to {current}"
    elif field in {"account_status", "payment_status"}:
        event_type = "status_changed"
        severity = "high"
        summary = f"{field.replace('_', ' ').title()} changed from {previous} to {current}"
    elif field == "date_first_delinquency":
        event_type = "dofd_changed"
        severity = "high"
        summary = f"DOFD changed from {previous} to {current}"
    elif field == "date_closed":
        event_type = "date_closed_changed"
        severity = "medium"
        summary = f"Date closed changed from {previous} to {current}"
    else:
        summary = f"{field} changed from {previous} to {current}"

    return ChronologyEvent(
        event_type=event_type,
        severity=severity,
        field=field,
        from_document_id=from_document_id,
        to_document_id=to_document_id,
        from_parsed_at=from_parsed_at,
        to_parsed_at=to_parsed_at,
        previous=previous,
        current=current,
        summary=summary,
    )


def _events_between(
    previous: ChronologySnapshot,
    current: ChronologySnapshot,
    previous_account: dict[str, Any] | None,
    current_account: dict[str, Any] | None,
) -> list[ChronologyEvent]:
    events: list[ChronologyEvent] = []
    if not previous.present and current.present:
        events.append(
            ChronologyEvent(
                event_type="appeared",
                severity="medium",
                field=None,
                from_document_id=previous.document_id,
                to_document_id=current.document_id,
                from_parsed_at=previous.parsed_at,
                to_parsed_at=current.parsed_at,
                previous=None,
                current=current.creditor_name,
                summary="Tradeline appeared on this bureau report",
            )
        )
        return events
    if previous.present and not current.present:
        events.append(
            ChronologyEvent(
                event_type="disappeared",
                severity="high",
                field=None,
                from_document_id=previous.document_id,
                to_document_id=current.document_id,
                from_parsed_at=previous.parsed_at,
                to_parsed_at=current.parsed_at,
                previous=previous.creditor_name,
                current=None,
                summary="Tradeline disappeared from this bureau report",
            )
        )
        return events
    if not previous.present or not current.present:
        return events

    for field in _TRACKED_FIELDS:
        prev_value = _field_value(previous_account, field)
        curr_value = _field_value(current_account, field)
        if prev_value != curr_value:
            events.append(
                _event_for_field_change(
                    field=field,
                    previous=prev_value,
                    current=curr_value,
                    from_document_id=previous.document_id,
                    to_document_id=current.document_id,
                    from_parsed_at=previous.parsed_at,
                    to_parsed_at=current.parsed_at,
                )
            )
    return events


def build_case_tradeline_chronology(
    *,
    case_id: uuid.UUID,
    reports: list[ReportSnapshotInput],
    bureau: str | None = None,
) -> CaseTradelineChronologyResult:
    filtered = [
        report for report in reports if bureau is None or report.bureau.lower() == bureau.lower()
    ]
    ordered = sorted(filtered, key=lambda item: (item.parsed_at, str(item.document_id)))

    reports_by_bureau: dict[str, list[ReportSnapshotInput]] = {}
    accounts_by_report: dict[uuid.UUID, dict[str, dict[str, Any]]] = {}
    all_keys: set[tuple[str, str]] = set()
    display_names: dict[tuple[str, str], tuple[str | None, str | None]] = {}

    for report in ordered:
        bureau_name = report.bureau.lower()
        reports_by_bureau.setdefault(bureau_name, []).append(report)
        keyed: dict[str, dict[str, Any]] = {}
        accounts_raw = report.parsed_report.get("accounts")
        accounts = accounts_raw if isinstance(accounts_raw, list) else []
        for account in accounts:
            if not isinstance(account, dict):
                continue
            creditor = _string_or_none(account.get("creditor_name"))
            if not creditor:
                continue
            key = tradeline_match_key(
                creditor,
                _string_or_none(account.get("account_number_masked")),
            )
            if not key or key == "unknown":
                continue
            keyed[key] = account
            all_keys.add((bureau_name, key))
            display_names[(bureau_name, key)] = (
                creditor,
                _string_or_none(account.get("account_number_masked")),
            )
        accounts_by_report[report.document_id] = keyed

    tradelines: list[TradelineChronology] = []
    for bureau_name, match_key in sorted(all_keys):
        bureau_reports = reports_by_bureau.get(bureau_name, [])
        points: list[tuple[ReportSnapshotInput, dict[str, Any] | None]] = []
        snapshots: list[ChronologySnapshot] = []
        events: list[ChronologyEvent] = []
        for report in bureau_reports:
            account = accounts_by_report.get(report.document_id, {}).get(match_key)
            points.append((report, account))
            snap = _snapshot_from_account(
                document_id=report.document_id,
                parsed_at=report.parsed_at,
                report=report.parsed_report,
                account=account,
            )
            snapshots.append(snap)
            if len(snapshots) > 1:
                prev_account = points[-2][1]
                events.extend(_events_between(snapshots[-2], snap, prev_account, account))

        if not any(item.present for item in snapshots):
            continue

        creditor_name, account_number = display_names.get((bureau_name, match_key), (None, None))
        for snap in reversed(snapshots):
            if snap.present:
                creditor_name = snap.creditor_name or creditor_name
                account_number = snap.account_number_masked or account_number
                break

        tradelines.append(
            TradelineChronology(
                match_key=match_key,
                bureau=bureau_name,
                creditor_name=creditor_name,
                account_number_masked=account_number,
                snapshot_count=sum(1 for item in snapshots if item.present),
                event_count=len(events),
                snapshots=tuple(snapshots),
                events=tuple(events),
            )
        )

    tradelines.sort(
        key=lambda item: (-item.event_count, item.creditor_name or "", item.bureau, item.match_key)
    )

    bureaus = tuple(sorted(reports_by_bureau))
    summary = {
        "tradelines": len(tradelines),
        "with_changes": sum(1 for item in tradelines if item.event_count > 0),
        "snapshots": sum(item.snapshot_count for item in tradelines),
        "events": sum(item.event_count for item in tradelines),
        "reports_evaluated": len(ordered),
    }
    return CaseTradelineChronologyResult(
        case_id=case_id,
        reports_evaluated=len(ordered),
        bureaus=bureaus,
        summary=summary,
        tradelines=tuple(tradelines),
    )
