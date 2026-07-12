"""Deterministic FCRA statutory checklist rules for parsed tradelines (Phase 3 scaffold).

These rules flag potential Fair Credit Reporting Act accuracy / obsolescence issues
for investigator review. They are heuristics tied to commonly cited FCRA provisions
(e.g. §§ 605, 607, 623) — not legal advice or a complete statutory audit.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

Severity = Literal["low", "medium", "high"]

_OBSOLESCENCE_YEARS = 7
_OBSOLESCENCE_DAYS = int(_OBSOLESCENCE_YEARS * 365.25)


@dataclass(frozen=True, slots=True)
class FcraFinding:
    rule_id: str
    severity: Severity
    title: str
    description: str
    fcra_sections: tuple[str, ...]
    tradeline_index: int
    creditor_name: str | None
    account_number_masked: str | None
    fields: tuple[str, ...]
    observed: dict[str, Any]


@dataclass(frozen=True, slots=True)
class FcraEvaluationResult:
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None
    as_of_date: str | None
    summary: dict[str, int]
    findings: tuple[FcraFinding, ...]


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


def _parse_date(value: object) -> datetime | None:
    raw = _string_or_none(value)
    if not raw:
        return None
    if "T" in raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            raw = raw.split("T", 1)[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw[:10] if fmt == "%Y-%m-%d" else raw, fmt)
        except ValueError:
            continue
    return None


def _status_blob(account: dict[str, Any]) -> str:
    parts = [
        _string_or_none(account.get("account_status")) or "",
        _string_or_none(account.get("payment_status")) or "",
        _string_or_none(account.get("account_type")) or "",
        _string_or_none(account.get("remarks")) or "",
    ]
    return " ".join(parts).lower()


def _looks_adverse(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    adverse_tokens = (
        "charge off",
        "charge-off",
        "collection",
        "delinquent",
        "past due",
        "late",
        "repossession",
        "foreclosure",
        "judgment",
        "settled",
        "profit and loss",
    )
    if any(token in blob for token in adverse_tokens):
        return True
    past_due = _float_or_none(account.get("past_due_amount"))
    return past_due is not None and past_due > 0


def _looks_collection(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    return "collection" in blob


def _looks_closed(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    return any(token in blob for token in ("closed", "paid", "transferred"))


def _resolve_as_of(parsed_report: dict[str, Any]) -> datetime | None:
    """Best-effort report as-of date for obsolescence / timeline checks."""
    candidates: list[datetime] = []
    accounts = parsed_report.get("accounts")
    if isinstance(accounts, list):
        for account in accounts:
            if not isinstance(account, dict):
                continue
            reported = _parse_date(account.get("date_reported"))
            if reported is not None:
                candidates.append(reported)
    if candidates:
        return max(candidates)

    metadata = parsed_report.get("metadata")
    if isinstance(metadata, dict):
        parsed_at = _parse_date(metadata.get("parsed_at"))
        if parsed_at is not None:
            return parsed_at
    return None


RuleFn = Callable[[int, dict[str, Any], datetime | None], FcraFinding | None]


def _rule_obsolete_adverse_info(
    index: int,
    account: dict[str, Any],
    as_of: datetime | None,
) -> FcraFinding | None:
    if as_of is None or not _looks_adverse(account):
        return None
    aging_date = _parse_date(account.get("date_first_delinquency")) or _parse_date(
        account.get("date_closed")
    )
    if aging_date is None:
        return None
    cutoff = as_of - timedelta(days=_OBSOLESCENCE_DAYS)
    if aging_date > cutoff:
        return None
    return FcraFinding(
        rule_id="fcra.obsolete_adverse_info",
        severity="high",
        title="Possible obsolete adverse information still reported",
        description=(
            f"Adverse tradeline appears older than approximately {_OBSOLESCENCE_YEARS} years "
            "from the report as-of date based on DOFD/date closed. FCRA §605 generally "
            "limits reporting of most obsolete adverse information."
        ),
        fcra_sections=("605",),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("date_first_delinquency", "date_closed", "account_status", "payment_status"),
        observed={
            "as_of_date": as_of.date().isoformat(),
            "aging_date": aging_date.date().isoformat(),
            "years_approx": round((as_of - aging_date).days / 365.25, 1),
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
        },
    )


def _rule_adverse_missing_dofd(
    index: int,
    account: dict[str, Any],
    _as_of: datetime | None,
) -> FcraFinding | None:
    if not _looks_adverse(account):
        return None
    if _string_or_none(account.get("date_first_delinquency")):
        return None
    return FcraFinding(
        rule_id="fcra.adverse_missing_dofd",
        severity="high",
        title="Adverse account missing date of first delinquency",
        description=(
            "Account appears adverse (delinquent, charged off, collection, or past due) "
            "but DOFD is missing. DOFD is central to FCRA §605 obsolescence timing and "
            "furnisher accuracy under §623."
        ),
        fcra_sections=("605", "623"),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "past_due_amount", "date_first_delinquency"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "past_due_amount": account.get("past_due_amount"),
            "date_first_delinquency": account.get("date_first_delinquency"),
        },
    )


def _rule_collection_missing_original_creditor(
    index: int,
    account: dict[str, Any],
    _as_of: datetime | None,
) -> FcraFinding | None:
    if not _looks_collection(account):
        return None
    if _string_or_none(account.get("original_creditor")):
        return None
    return FcraFinding(
        rule_id="fcra.collection_missing_original_creditor",
        severity="medium",
        title="Collection account missing original creditor",
        description=(
            "Tradeline appears to be a collection but original creditor is not present. "
            "Incomplete identification can impair consumer dispute rights and accuracy "
            "review under FCRA §623."
        ),
        fcra_sections=("623",),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "original_creditor"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "original_creditor": account.get("original_creditor"),
        },
    )


def _rule_past_due_exceeds_balance(
    index: int,
    account: dict[str, Any],
    _as_of: datetime | None,
) -> FcraFinding | None:
    balance = _float_or_none(account.get("balance"))
    past_due = _float_or_none(account.get("past_due_amount"))
    if balance is None or past_due is None:
        return None
    if past_due <= 0 or past_due <= balance:
        return None
    return FcraFinding(
        rule_id="fcra.past_due_exceeds_balance",
        severity="high",
        title="Past-due amount exceeds reported balance",
        description=(
            "Past-due amount is greater than the reported balance. That combination is "
            "often materially inconsistent and may implicate accuracy duties under "
            "FCRA §§ 607 and 623."
        ),
        fcra_sections=("607", "623"),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("balance", "past_due_amount"),
        observed={"balance": balance, "past_due_amount": past_due},
    )


def _rule_open_date_after_as_of(
    index: int,
    account: dict[str, Any],
    as_of: datetime | None,
) -> FcraFinding | None:
    if as_of is None:
        return None
    opened = _parse_date(account.get("open_date"))
    if opened is None or opened.date() <= as_of.date():
        return None
    return FcraFinding(
        rule_id="fcra.open_date_after_as_of",
        severity="high",
        title="Open date is after the report as-of date",
        description=(
            "The account open date is later than the report as-of date, which is an "
            "impossible timeline and may indicate inaccurate reporting under FCRA §607."
        ),
        fcra_sections=("607",),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("open_date",),
        observed={
            "open_date": account.get("open_date"),
            "as_of_date": as_of.date().isoformat(),
        },
    )


def _rule_dofd_after_as_of(
    index: int,
    account: dict[str, Any],
    as_of: datetime | None,
) -> FcraFinding | None:
    if as_of is None:
        return None
    dofd = _parse_date(account.get("date_first_delinquency"))
    if dofd is None or dofd.date() <= as_of.date():
        return None
    return FcraFinding(
        rule_id="fcra.dofd_after_as_of",
        severity="high",
        title="Date of first delinquency is after the report as-of date",
        description=(
            "DOFD is later than the report as-of date. That timeline is impossible and "
            "undermines reliable obsolescence analysis under FCRA §605."
        ),
        fcra_sections=("605", "607"),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("date_first_delinquency",),
        observed={
            "date_first_delinquency": account.get("date_first_delinquency"),
            "as_of_date": as_of.date().isoformat(),
        },
    )


def _rule_closed_missing_date_closed(
    index: int,
    account: dict[str, Any],
    _as_of: datetime | None,
) -> FcraFinding | None:
    if not _looks_closed(account):
        return None
    if _string_or_none(account.get("date_closed")):
        return None
    blob = _status_blob(account)
    if not any(token in blob for token in ("closed", "paid", "transferred")):
        return None
    return FcraFinding(
        rule_id="fcra.closed_missing_date_closed",
        severity="medium",
        title="Closed/paid account missing date closed",
        description=(
            "Status indicates closed, paid, or transferred without a date closed. "
            "Incomplete date fields can impair accuracy and completeness review under "
            "FCRA §623."
        ),
        fcra_sections=("623",),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "date_closed"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "date_closed": account.get("date_closed"),
        },
    )


def _rule_sold_transferred_still_balance(
    index: int,
    account: dict[str, Any],
    _as_of: datetime | None,
) -> FcraFinding | None:
    blob = _status_blob(account)
    if not any(token in blob for token in ("sold", "transferred", "transfer")):
        return None
    balance = _float_or_none(account.get("balance"))
    if balance is None or balance <= 0:
        return None
    return FcraFinding(
        rule_id="fcra.sold_transferred_still_balance",
        severity="medium",
        title="Sold/transferred account still shows a balance",
        description=(
            "Remarks or status indicate the account was sold or transferred, but a "
            "positive balance remains. Dual reporting of the same debt can be "
            "materially misleading under FCRA accuracy requirements."
        ),
        fcra_sections=("623", "607"),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "remarks", "balance"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "remarks": account.get("remarks"),
            "balance": balance,
        },
    )


FCRA_RULES: tuple[RuleFn, ...] = (
    _rule_obsolete_adverse_info,
    _rule_adverse_missing_dofd,
    _rule_collection_missing_original_creditor,
    _rule_past_due_exceeds_balance,
    _rule_open_date_after_as_of,
    _rule_dofd_after_as_of,
    _rule_closed_missing_date_closed,
    _rule_sold_transferred_still_balance,
)


def evaluate_tradelines(
    *,
    document_id: uuid.UUID,
    bureau: str,
    parsed_report: dict[str, Any],
) -> FcraEvaluationResult:
    as_of = _resolve_as_of(parsed_report)
    accounts = parsed_report.get("accounts")
    findings: list[FcraFinding] = []
    if isinstance(accounts, list):
        for index, account in enumerate(accounts):
            if not isinstance(account, dict):
                continue
            if not _string_or_none(account.get("creditor_name")):
                continue
            for rule in FCRA_RULES:
                finding = rule(index, account, as_of)
                if finding is not None:
                    findings.append(finding)

    summary = {
        "total": len(findings),
        "high": sum(1 for item in findings if item.severity == "high"),
        "medium": sum(1 for item in findings if item.severity == "medium"),
        "low": sum(1 for item in findings if item.severity == "low"),
        "tradelines_evaluated": (
            len([a for a in accounts if isinstance(a, dict)]) if isinstance(accounts, list) else 0
        ),
    }
    schema_version = parsed_report.get("schema_version")
    return FcraEvaluationResult(
        document_id=document_id,
        bureau=bureau,
        schema_version=schema_version if isinstance(schema_version, str) else None,
        as_of_date=as_of.date().isoformat() if as_of is not None else None,
        summary=summary,
        findings=tuple(findings),
    )
