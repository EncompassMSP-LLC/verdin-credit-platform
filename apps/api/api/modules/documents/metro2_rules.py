"""Deterministic Metro 2 consistency rules for parsed tradelines (Phase 2 scaffold).

These rules flag field-level inconsistencies that may indicate Metro 2 reporting
problems. They are heuristics for investigator review — not a substitute for a
full CDIA Metro 2 audit or legal advice.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

Severity = Literal["low", "medium", "high"]

_DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y")


@dataclass(frozen=True, slots=True)
class Metro2Finding:
    rule_id: str
    severity: Severity
    title: str
    description: str
    tradeline_index: int
    creditor_name: str | None
    account_number_masked: str | None
    fields: tuple[str, ...]
    observed: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Metro2EvaluationResult:
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None
    summary: dict[str, int]
    findings: tuple[Metro2Finding, ...]


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
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _status_blob(account: dict[str, Any]) -> str:
    parts = [
        _string_or_none(account.get("account_status")) or "",
        _string_or_none(account.get("payment_status")) or "",
    ]
    return " ".join(parts).lower()


def _looks_closed(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    return any(
        token in blob for token in ("closed", "paid", "charge off", "charge-off", "transferred")
    )


def _looks_current(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    return "current" in blob or "pays as agreed" in blob


RuleFn = Callable[[int, dict[str, Any]], Metro2Finding | None]


def _rule_closed_with_balance(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    balance = _float_or_none(account.get("balance"))
    if not _looks_closed(account) or balance is None or balance <= 0:
        return None
    return Metro2Finding(
        rule_id="metro2.closed_with_balance",
        severity="high",
        title="Closed or paid account still shows a balance",
        description=(
            "Account status indicates closed/paid/charge-off/transferred, but a positive "
            "balance is still reported. Metro 2 typically expects balance handling to "
            "align with the reported status."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "balance"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "balance": balance,
        },
    )


def _rule_past_due_without_dofd(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    past_due = _float_or_none(account.get("past_due_amount"))
    dofd = _string_or_none(account.get("date_first_delinquency"))
    if past_due is None or past_due <= 0 or dofd:
        return None
    return Metro2Finding(
        rule_id="metro2.past_due_without_dofd",
        severity="high",
        title="Past-due amount without date of first delinquency",
        description=(
            "A positive past-due amount is reported without a date of first delinquency "
            "(DOFD). DOFD is a critical Metro 2 / FCRA aging field for delinquent accounts."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("past_due_amount", "date_first_delinquency"),
        observed={"past_due_amount": past_due, "date_first_delinquency": dofd},
    )


def _rule_current_with_past_due(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    past_due = _float_or_none(account.get("past_due_amount"))
    if not _looks_current(account) or past_due is None or past_due <= 0:
        return None
    return Metro2Finding(
        rule_id="metro2.current_with_past_due",
        severity="high",
        title="Current status with past-due amount",
        description=(
            "Payment/account status appears current, but past-due amount is greater than "
            "zero. These fields are usually mutually inconsistent in Metro 2 reporting."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("payment_status", "account_status", "past_due_amount"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "past_due_amount": past_due,
        },
    )


def _rule_date_closed_before_open(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    opened = _parse_date(account.get("open_date"))
    closed = _parse_date(account.get("date_closed"))
    if opened is None or closed is None or closed >= opened:
        return None
    return Metro2Finding(
        rule_id="metro2.date_closed_before_open",
        severity="high",
        title="Date closed is before date opened",
        description=(
            "The reported date closed precedes the date opened, which is an impossible "
            "date sequence for a valid tradeline timeline."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("open_date", "date_closed"),
        observed={
            "open_date": account.get("open_date"),
            "date_closed": account.get("date_closed"),
        },
    )


def _rule_balance_exceeds_high_credit(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    balance = _float_or_none(account.get("balance"))
    high_credit = _float_or_none(account.get("high_credit"))
    if balance is None or high_credit is None or high_credit <= 0 or balance <= high_credit:
        return None
    return Metro2Finding(
        rule_id="metro2.balance_exceeds_high_credit",
        severity="medium",
        title="Balance exceeds high credit",
        description=(
            "Current balance is greater than reported high credit. High credit is typically "
            "the highest balance owed; this may indicate stale or inconsistent reporting."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("balance", "high_credit"),
        observed={"balance": balance, "high_credit": high_credit},
    )


def _rule_closed_missing_date_closed(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    if not _looks_closed(account):
        return None
    if _string_or_none(account.get("date_closed")):
        return None
    # Charge-off / collection often remain "open" reporting without a closed date —
    # only flag when status explicitly says closed/paid/transferred.
    blob = _status_blob(account)
    if not any(token in blob for token in ("closed", "paid", "transferred")):
        return None
    return Metro2Finding(
        rule_id="metro2.closed_missing_date_closed",
        severity="medium",
        title="Closed/paid status without date closed",
        description=(
            "Account status indicates closed, paid, or transferred, but date closed is "
            "missing from the parsed tradeline."
        ),
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


def _looks_charge_off(account: dict[str, Any]) -> bool:
    blob = _status_blob(account)
    return ("charge" in blob and "off" in blob) or "charge-off" in blob


def _rule_charge_off_zero_past_due(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    balance = _float_or_none(account.get("balance"))
    past_due = _float_or_none(account.get("past_due_amount"))
    if not _looks_charge_off(account):
        return None
    if balance is None or balance <= 0:
        return None
    if past_due is None or past_due != 0:
        return None
    return Metro2Finding(
        rule_id="metro2.charge_off_zero_past_due",
        severity="medium",
        title="Charge-off with balance but zero past due",
        description=(
            "Account is reported as charged off with a positive balance, but past due is "
            "zero. Metro 2 charge-off reporting often keeps past-due aligned with the "
            "outstanding amount unless the debt was otherwise resolved."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_status", "payment_status", "balance", "past_due_amount"),
        observed={
            "account_status": account.get("account_status"),
            "payment_status": account.get("payment_status"),
            "balance": balance,
            "past_due_amount": past_due,
        },
    )


def _rule_dofd_before_open(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    opened = _parse_date(account.get("open_date"))
    dofd = _parse_date(account.get("date_first_delinquency"))
    if opened is None or dofd is None or dofd >= opened:
        return None
    return Metro2Finding(
        rule_id="metro2.dofd_before_open",
        severity="high",
        title="Date of first delinquency precedes open date",
        description=(
            "DOFD is earlier than the account open date, which is an impossible timeline "
            "for a valid tradeline."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("open_date", "date_first_delinquency"),
        observed={
            "open_date": account.get("open_date"),
            "date_first_delinquency": account.get("date_first_delinquency"),
        },
    )


def _rule_open_with_date_closed(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    blob = _status_blob(account)
    date_closed = _string_or_none(account.get("date_closed"))
    if not date_closed:
        return None
    if _looks_closed(account):
        return None
    if "open" not in blob and "current" not in blob and "pays as agreed" not in blob:
        return None
    return Metro2Finding(
        rule_id="metro2.open_with_date_closed",
        severity="medium",
        title="Open/current status with a date closed",
        description=(
            "A date closed is present while status still appears open or current. "
            "These fields are usually mutually exclusive."
        ),
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


def _rule_zero_balance_with_past_due(index: int, account: dict[str, Any]) -> Metro2Finding | None:
    balance = _float_or_none(account.get("balance"))
    past_due = _float_or_none(account.get("past_due_amount"))
    if balance is None or balance != 0:
        return None
    if past_due is None or past_due <= 0:
        return None
    return Metro2Finding(
        rule_id="metro2.zero_balance_with_past_due",
        severity="medium",
        title="Zero balance with positive past due",
        description=(
            "Balance is zero while past-due amount is greater than zero. Past due is "
            "normally a component of the outstanding balance."
        ),
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("balance", "past_due_amount"),
        observed={"balance": balance, "past_due_amount": past_due},
    )


METRO2_RULES: tuple[RuleFn, ...] = (
    _rule_closed_with_balance,
    _rule_past_due_without_dofd,
    _rule_current_with_past_due,
    _rule_date_closed_before_open,
    _rule_balance_exceeds_high_credit,
    _rule_closed_missing_date_closed,
    _rule_charge_off_zero_past_due,
    _rule_dofd_before_open,
    _rule_open_with_date_closed,
    _rule_zero_balance_with_past_due,
)


def evaluate_tradelines(
    *,
    document_id: uuid.UUID,
    bureau: str,
    parsed_report: dict[str, Any],
) -> Metro2EvaluationResult:
    accounts = parsed_report.get("accounts")
    findings: list[Metro2Finding] = []
    if isinstance(accounts, list):
        for index, account in enumerate(accounts):
            if not isinstance(account, dict):
                continue
            if not _string_or_none(account.get("creditor_name")):
                continue
            for rule in METRO2_RULES:
                finding = rule(index, account)
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
    return Metro2EvaluationResult(
        document_id=document_id,
        bureau=bureau,
        schema_version=schema_version if isinstance(schema_version, str) else None,
        summary=summary,
        findings=tuple(findings),
    )
