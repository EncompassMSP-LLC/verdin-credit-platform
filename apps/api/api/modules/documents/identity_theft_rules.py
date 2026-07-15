"""Identity Theft Detection & Recovery Engine (Phase 8 / Compliance Intelligence).

Detects report-level fraud-alert / freeze / victim-statement indicators and
tradeline-level warning signs. Findings are investigator aids — never auto-label
an account as identity theft or generate a sworn claim without consumer confirmation.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

Severity = Literal["low", "medium", "high"]
DetectionSource = Literal[
    "REPORT_TEXT",
    "TRADELINE_HEURISTIC",
    "CONSUMER_CONFIRMATION",
    "PERSONAL_INFO",
]
IssueType = Literal["IDENTITY_THEFT_INDICATOR", "CONFIRMED_IDENTITY_THEFT_CLAIM"]
RequiredAction = Literal[
    "CONSUMER_REVIEW",
    "OPEN_IDENTITY_THEFT_CASE",
    "PREPARE_605B",
    "CONTINUE_ORDINARY_DISPUTE",
]
LegalPath = Literal["FCRA_605B"]
EvidenceStatus = Literal["present", "missing", "unknown"]

CONSUMER_CONFIRMATION_OPTIONS: tuple[str, ...] = (
    "recognize",
    "need_more_info",
    "inaccurate_reporting",
    "identity_theft",
    "mixed_file",
    "authorized_user",
    "unsure",
)

CONSUMER_ATTESTATION_TEXT = (
    "I affirm that I did not open, authorize, use, or benefit from this account, "
    "and that the information I provided is truthful to the best of my knowledge."
)

IDENTITY_THEFT_BANNER_TITLE = "Identity-Theft Protection Indicator Detected"
IDENTITY_THEFT_BANNER_BODY = (
    "This report contains a fraud alert, freeze, victim statement, or identity-theft "
    "block. Review the Identity Theft Case Center before sending ordinary credit disputes."
)

# Report-level phrase / code patterns (case-insensitive substring match).
_REPORT_INDICATOR_PATTERNS: tuple[tuple[str, str, float], ...] = (
    ("fraud alert", "identity_theft.report.fraud_alert", 0.98),
    ("initial security alert", "identity_theft.report.initial_security_alert", 0.98),
    ("initial fraud alert", "identity_theft.report.initial_fraud_alert", 0.98),
    ("extended fraud alert", "identity_theft.report.extended_fraud_alert", 0.99),
    ("active duty alert", "identity_theft.report.active_duty_alert", 0.97),
    ("active-duty alert", "identity_theft.report.active_duty_alert", 0.97),
    ("security freeze", "identity_theft.report.security_freeze", 0.97),
    ("credit freeze", "identity_theft.report.credit_freeze", 0.97),
    ("file blocked due to identity theft", "identity_theft.report.file_blocked", 0.99),
    ("identity theft victim statement", "identity_theft.report.victim_statement", 0.99),
    ("identity theft block", "identity_theft.report.identity_theft_block", 0.99),
    ("address discrepancy", "identity_theft.report.address_discrepancy", 0.90),
    ("lost or stolen social security", "identity_theft.report.lost_stolen_ssn", 0.95),
    ("stolen social security number", "identity_theft.report.lost_stolen_ssn", 0.95),
)

_VICTIM_STATEMENT_HINTS = (
    "identity theft",
    "victim of fraud",
    "fraudulent accounts",
    "did not open",
    "unauthorized account",
)

_PLAUSIBLE_BORROWING_AGE_YEARS = 18
_INQUIRY_BURST_DAYS = 30
_INQUIRY_BURST_MIN_COUNT = 4

# Mixed-file / personal-info variation detection (Phase 9). Advisory signals only —
# never auto-labels an account as identity theft. Ordinary §611 disputes stay
# available (mixed_file is an unlock choice), so these findings do not lock disputes.
_ADDRESS_VARIATION_THRESHOLD = 5
_NAME_FIELD_HINTS = ("name", "also known", "aka", "alias")
_SSN_FIELD_HINTS = ("ssn", "social security", "social_security")
_DOB_FIELD_HINTS = ("birth", "dob")
_ADDRESS_FIELD_HINTS = ("address",)


@dataclass(frozen=True, slots=True)
class IdentityTheftFinding:
    rule_id: str
    severity: Severity
    title: str
    description: str
    detection_source: DetectionSource
    issue_type: IssueType
    confidence: float
    consumer_confirmed: bool
    legal_path: LegalPath | None
    ordinary_dispute_locked: bool
    required_action: RequiredAction
    tradeline_index: int | None
    creditor_name: str | None
    account_number_masked: str | None
    fields: tuple[str, ...]
    observed: dict[str, Any]


@dataclass(frozen=True, slots=True)
class IdentityTheftEvaluationResult:
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None
    as_of_date: str | None
    banner_active: bool
    banner_title: str | None
    banner_body: str | None
    ordinary_dispute_locked: bool
    summary: dict[str, int]
    findings: tuple[IdentityTheftFinding, ...]
    protections_detected: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class Fcra605bItem:
    item_id: str
    label: str
    required: bool
    status: EvidenceStatus


@dataclass(frozen=True, slots=True)
class Fcra605bReadiness:
    remedy_type: str
    not_ordinary_dispute: bool
    packet_readiness: int
    items: tuple[Fcra605bItem, ...]
    missing_evidence: tuple[str, ...]


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
            return datetime.strptime(raw[:10] if fmt.startswith("%Y") else raw, fmt)
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


def _flatten_report_text(parsed_report: dict[str, Any]) -> str:
    chunks: list[str] = []

    def _walk(value: object) -> None:
        if isinstance(value, str):
            if value.strip():
                chunks.append(value)
            return
        if isinstance(value, dict):
            for nested in value.values():
                _walk(nested)
            return
        if isinstance(value, list):
            for nested in value:
                _walk(nested)

    _walk(parsed_report)
    return " ".join(chunks).lower()


def _resolve_as_of(parsed_report: dict[str, Any]) -> datetime | None:
    for key in ("as_of_date", "report_date", "date_pulled"):
        parsed = _parse_date(parsed_report.get(key))
        if parsed is not None:
            return parsed
    accounts = parsed_report.get("accounts")
    if isinstance(accounts, list):
        dates: list[datetime] = [
            d
            for a in accounts
            if isinstance(a, dict)
            for d in [_parse_date(a.get("date_reported"))]
            if d is not None
        ]
        if dates:
            return max(dates)
    return None


def _consumer_dob(parsed_report: dict[str, Any]) -> datetime | None:
    consumer = parsed_report.get("consumer")
    if isinstance(consumer, dict):
        dob = _parse_date(consumer.get("date_of_birth"))
        if dob is not None:
            return dob
    personal = parsed_report.get("personal_information")
    if isinstance(personal, list):
        for item in personal:
            if not isinstance(item, dict):
                continue
            name = (_string_or_none(item.get("field_name")) or "").lower()
            if "birth" in name or name in {"dob", "date_of_birth"}:
                return _parse_date(item.get("value"))
    return None


def _indicator_finding(
    *,
    rule_id: str,
    title: str,
    description: str,
    confidence: float,
    severity: Severity = "high",
    detection_source: DetectionSource = "REPORT_TEXT",
    tradeline_index: int | None = None,
    creditor_name: str | None = None,
    account_number_masked: str | None = None,
    fields: tuple[str, ...] = (),
    observed: dict[str, Any] | None = None,
) -> IdentityTheftFinding:
    return IdentityTheftFinding(
        rule_id=rule_id,
        severity=severity,
        title=title,
        description=description,
        detection_source=detection_source,
        issue_type="IDENTITY_THEFT_INDICATOR",
        confidence=confidence,
        consumer_confirmed=False,
        legal_path=None,
        ordinary_dispute_locked=True,
        required_action="CONSUMER_REVIEW",
        tradeline_index=tradeline_index,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
        fields=fields,
        observed=observed or {},
    )


def _detect_report_level_indicators(
    report_text: str,
) -> tuple[list[IdentityTheftFinding], list[dict[str, Any]]]:
    findings: list[IdentityTheftFinding] = []
    protections: list[dict[str, Any]] = []
    matched_rule_ids: set[str] = set()

    for phrase, rule_id, confidence in _REPORT_INDICATOR_PATTERNS:
        if phrase not in report_text or rule_id in matched_rule_ids:
            continue
        matched_rule_ids.add(rule_id)
        findings.append(
            _indicator_finding(
                rule_id=rule_id,
                title="Identity-theft protection indicator on report",
                description=(
                    f"Report text matches protective indicator phrase “{phrase}”. "
                    "Fraud alerts and freezes are protective tools, not proof that every "
                    "negative account is fraudulent. Obtain consumer review before "
                    "ordinary disputes."
                ),
                confidence=confidence,
                fields=("report_text",),
                observed={"matched_phrase": phrase},
            )
        )
        if "fraud alert" in phrase or "security alert" in phrase:
            kind = "extended_fraud_alert" if "extended" in phrase else "initial_fraud_alert"
            if "active" in phrase:
                kind = "active_duty_alert"
            protections.append(
                {
                    "protection_type": kind,
                    "status": "active",
                    "source": "report_detected",
                    "matched_phrase": phrase,
                }
            )
        if "freeze" in phrase:
            protections.append(
                {
                    "protection_type": "credit_freeze",
                    "status": "frozen",
                    "source": "report_detected",
                    "matched_phrase": phrase,
                }
            )

    if any(hint in report_text for hint in _VICTIM_STATEMENT_HINTS) and (
        "consumer statement" in report_text or "victim statement" in report_text
    ):
        rule_id = "identity_theft.report.consumer_fraud_statement"
        if rule_id not in matched_rule_ids:
            findings.append(
                _indicator_finding(
                    rule_id=rule_id,
                    title="Consumer statement referencing fraud or identity theft",
                    description=(
                        "A consumer statement appears to reference fraud or identity theft. "
                        "Review the Identity Theft Case Center before ordinary disputes."
                    ),
                    confidence=0.92,
                    fields=("consumer_statement",),
                    observed={"hints": [h for h in _VICTIM_STATEMENT_HINTS if h in report_text]},
                )
            )

    return findings, protections


TradelineRuleFn = Callable[
    [int, dict[str, Any], dict[str, Any], datetime | None],
    IdentityTheftFinding | None,
]


def _rule_consumer_denied_account(
    index: int,
    account: dict[str, Any],
    _parsed: dict[str, Any],
    _as_of: datetime | None,
) -> IdentityTheftFinding | None:
    blob = _status_blob(account)
    tokens = (
        "did not open",
        "i did not open",
        "not my account",
        "do not recognize",
        "never opened",
        "unauthorized",
        "fraudulent account",
        "identity theft",
    )
    hit = next((t for t in tokens if t in blob), None)
    if hit is None:
        return None
    return _indicator_finding(
        rule_id="identity_theft.tradeline.consumer_denies_account",
        title="Tradeline remarks suggest consumer did not open the account",
        description=(
            "Remarks or status text include language consistent with “I did not open "
            "this account” or unauthorized use. Require consumer confirmation before "
            "treating this as identity theft or generating a sworn claim."
        ),
        confidence=0.88,
        detection_source="TRADELINE_HEURISTIC",
        severity="high",
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("remarks", "account_status", "payment_status"),
        observed={"matched_token": hit, "blob_excerpt": blob[:200]},
    )


def _rule_unknown_creditor_collection(
    index: int,
    account: dict[str, Any],
    _parsed: dict[str, Any],
    _as_of: datetime | None,
) -> IdentityTheftFinding | None:
    blob = _status_blob(account)
    creditor = (_string_or_none(account.get("creditor_name")) or "").lower()
    if "collection" not in blob and "collection" not in creditor:
        return None
    unknown_tokens = ("unknown", "unrecognized", "not listed", "undisclosed")
    if not any(token in blob or token in creditor for token in unknown_tokens):
        # Soft signal: collection without original creditor
        if _string_or_none(account.get("original_creditor")):
            return None
        return _indicator_finding(
            rule_id="identity_theft.tradeline.unfamiliar_collection",
            title="Collection without identified original creditor",
            description=(
                "An unfamiliar collection or debt can be an identity-theft indicator, "
                "but guidance recommends contacting the creditor and investigating "
                "rather than assuming fraud. Flag for consumer review."
            ),
            confidence=0.62,
            detection_source="TRADELINE_HEURISTIC",
            severity="medium",
            tradeline_index=index,
            creditor_name=_string_or_none(account.get("creditor_name")),
            account_number_masked=_string_or_none(account.get("account_number_masked")),
            fields=("creditor_name", "original_creditor", "account_status"),
            observed={
                "original_creditor": account.get("original_creditor"),
                "account_status": account.get("account_status"),
            },
        )
    return _indicator_finding(
        rule_id="identity_theft.tradeline.unknown_creditor",
        title="Unknown or unrecognized creditor / collector",
        description=(
            "Creditor or remarks suggest an unknown lender or collection agency. "
            "Require consumer confirmation; do not auto-label as identity theft."
        ),
        confidence=0.75,
        detection_source="TRADELINE_HEURISTIC",
        severity="medium",
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("creditor_name", "remarks"),
        observed={"creditor_name": account.get("creditor_name")},
    )


def _rule_open_before_plausible_age(
    index: int,
    account: dict[str, Any],
    parsed: dict[str, Any],
    _as_of: datetime | None,
) -> IdentityTheftFinding | None:
    dob = _consumer_dob(parsed)
    open_date = _parse_date(account.get("open_date"))
    if dob is None or open_date is None:
        return None
    age_years = (open_date - dob).days / 365.25
    if age_years >= _PLAUSIBLE_BORROWING_AGE_YEARS:
        return None
    return _indicator_finding(
        rule_id="identity_theft.tradeline.open_before_plausible_age",
        title="Account opened before plausible borrowing age",
        description=(
            "Open date precedes a plausible borrowing age based on the consumer’s "
            "date of birth. This may indicate identity theft or a mixed file — "
            "confirm with the consumer before any sworn claim."
        ),
        confidence=0.85,
        detection_source="TRADELINE_HEURISTIC",
        severity="high",
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("open_date", "date_of_birth"),
        observed={
            "open_date": account.get("open_date"),
            "approximate_age_at_open": round(age_years, 1),
        },
    )


def _rule_history_before_open(
    index: int,
    account: dict[str, Any],
    _parsed: dict[str, Any],
    _as_of: datetime | None,
) -> IdentityTheftFinding | None:
    open_date = _parse_date(account.get("open_date"))
    history = _string_or_none(account.get("payment_history"))
    dofd = _parse_date(account.get("date_first_delinquency"))
    if open_date is None:
        return None
    if dofd is not None and dofd < open_date:
        return _indicator_finding(
            rule_id="identity_theft.tradeline.history_before_open",
            title="Account history begins before reported opening date",
            description=(
                "Date of first delinquency precedes the reported open date. "
                "Possible identity-theft or mixed-file indicator — requires consumer review."
            ),
            confidence=0.90,
            detection_source="TRADELINE_HEURISTIC",
            severity="high",
            tradeline_index=index,
            creditor_name=_string_or_none(account.get("creditor_name")),
            account_number_masked=_string_or_none(account.get("account_number_masked")),
            fields=("open_date", "date_first_delinquency"),
            observed={
                "open_date": account.get("open_date"),
                "date_first_delinquency": account.get("date_first_delinquency"),
            },
        )
    if history and re.search(r"\b(19|20)\d{2}\b", history):
        # Soft: historical year tokens older than open year in free text
        open_year = open_date.year
        years = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", history)]
        older = [y for y in years if y < open_year]
        if older:
            return _indicator_finding(
                rule_id="identity_theft.tradeline.history_year_before_open",
                title="Payment history references years before open date",
                description=(
                    "Payment history text includes calendar years before the reported "
                    "open date. Flag for investigator and consumer review."
                ),
                confidence=0.70,
                detection_source="TRADELINE_HEURISTIC",
                severity="medium",
                tradeline_index=index,
                creditor_name=_string_or_none(account.get("creditor_name")),
                account_number_masked=_string_or_none(account.get("account_number_masked")),
                fields=("open_date", "payment_history"),
                observed={"open_year": open_year, "older_years": older[:5]},
            )
    return None


def _rule_authorized_user_as_individual(
    index: int,
    account: dict[str, Any],
    _parsed: dict[str, Any],
    _as_of: datetime | None,
) -> IdentityTheftFinding | None:
    blob = _status_blob(account)
    account_type = (_string_or_none(account.get("account_type")) or "").lower()
    is_au = "authorized user" in blob or "authorized user" in account_type or "au" == account_type
    individual = any(
        token in blob for token in ("individual", "responsible", "primary borrower", "joint")
    )
    if not is_au or not individual:
        return None
    return _indicator_finding(
        rule_id="identity_theft.tradeline.authorized_user_misreported",
        title="Authorized-user status may be shown as individual responsibility",
        description=(
            "Account appears to mix authorized-user status with individual/joint "
            "responsibility language. Confirm consumer role before ordinary disputes "
            "or identity-theft claims."
        ),
        confidence=0.72,
        detection_source="TRADELINE_HEURISTIC",
        severity="medium",
        tradeline_index=index,
        creditor_name=_string_or_none(account.get("creditor_name")),
        account_number_masked=_string_or_none(account.get("account_number_masked")),
        fields=("account_type", "remarks", "account_status"),
        observed={
            "account_type": account.get("account_type"),
            "remarks": account.get("remarks"),
        },
    )


TRADELINE_RULES: tuple[TradelineRuleFn, ...] = (
    _rule_consumer_denied_account,
    _rule_unknown_creditor_collection,
    _rule_open_before_plausible_age,
    _rule_history_before_open,
    _rule_authorized_user_as_individual,
)


def _detect_inquiry_burst(parsed_report: dict[str, Any]) -> IdentityTheftFinding | None:
    inquiries = parsed_report.get("inquiries")
    if not isinstance(inquiries, list):
        return None
    dates: list[datetime] = []
    for item in inquiries:
        if not isinstance(item, dict):
            continue
        parsed = _parse_date(item.get("inquiry_date"))
        if parsed is not None:
            dates.append(parsed)
    if len(dates) < _INQUIRY_BURST_MIN_COUNT:
        return None
    dates.sort()
    for i in range(len(dates)):
        window = [d for d in dates if 0 <= (d - dates[i]).days <= _INQUIRY_BURST_DAYS]
        if len(window) >= _INQUIRY_BURST_MIN_COUNT:
            return _indicator_finding(
                rule_id="identity_theft.report.inquiry_burst",
                title="Multiple inquiries within a short period",
                description=(
                    f"{len(window)} inquiries fall within {_INQUIRY_BURST_DAYS} days. "
                    "This can indicate stolen credentials or a data breach — review "
                    "with the consumer before ordinary dispute letters."
                ),
                confidence=0.78,
                detection_source="TRADELINE_HEURISTIC",
                severity="medium",
                fields=("inquiries",),
                observed={
                    "inquiries_in_window": len(window),
                    "window_days": _INQUIRY_BURST_DAYS,
                    "window_start": dates[i].date().isoformat(),
                },
            )
    return None


def _personal_info_finding(
    *,
    rule_id: str,
    title: str,
    description: str,
    confidence: float,
    severity: Severity,
    fields: tuple[str, ...],
    observed: dict[str, Any],
) -> IdentityTheftFinding:
    """Advisory mixed-file / personal-info variation finding.

    Never locks ordinary disputes and never auto-labels the account as identity
    theft — a mixed file is investigated and confirmed by a human.
    """
    return IdentityTheftFinding(
        rule_id=rule_id,
        severity=severity,
        title=title,
        description=description,
        detection_source="PERSONAL_INFO",
        issue_type="IDENTITY_THEFT_INDICATOR",
        confidence=confidence,
        consumer_confirmed=False,
        legal_path=None,
        ordinary_dispute_locked=False,
        required_action="CONSUMER_REVIEW",
        tradeline_index=None,
        creditor_name=None,
        account_number_masked=None,
        fields=fields,
        observed=observed,
    )


def _normalize_ssn(value: object) -> str | None:
    raw = _string_or_none(value)
    if raw is None:
        return None
    if any(ch in raw for ch in ("x", "X", "*", "#")):
        return None
    digits = re.sub(r"\D", "", raw)
    return digits if len(digits) == 9 else None


def _normalize_name(value: object) -> str | None:
    raw = _string_or_none(value)
    if raw is None:
        return None
    cleaned = re.sub(r"[^a-z ]", " ", raw.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def _surname(name: str) -> str | None:
    tokens = name.split()
    return tokens[-1] if tokens else None


def _normalize_address(value: object) -> str | None:
    if isinstance(value, dict):
        parts = [
            _string_or_none(value.get(key))
            for key in ("line1", "street", "address", "city", "state", "postal_code", "zip")
        ]
        raw = " ".join(part for part in parts if part)
    else:
        raw = _string_or_none(value) or ""
    cleaned = re.sub(r"[^a-z0-9 ]", " ", raw.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def _collect_personal_info(
    parsed_report: dict[str, Any],
) -> tuple[set[str], set[str], set[str], set[str]]:
    """Return (names, ssns, dobs, addresses) normalized for variation detection."""
    names: set[str] = set()
    ssns: set[str] = set()
    dobs: set[str] = set()
    addresses: set[str] = set()

    def _classify(field_name: str, value: object) -> None:
        lowered = field_name.lower()
        if any(hint in lowered for hint in _SSN_FIELD_HINTS):
            ssn = _normalize_ssn(value)
            if ssn:
                ssns.add(ssn)
            return
        if any(hint in lowered for hint in _DOB_FIELD_HINTS):
            parsed = _parse_date(value)
            if parsed is not None:
                dobs.add(parsed.date().isoformat())
            return
        if any(hint in lowered for hint in _ADDRESS_FIELD_HINTS):
            address = _normalize_address(value)
            if address:
                addresses.add(address)
            return
        if any(hint in lowered for hint in _NAME_FIELD_HINTS):
            name = _normalize_name(value)
            if name:
                names.add(name)

    personal = parsed_report.get("personal_information")
    if isinstance(personal, list):
        for item in personal:
            if not isinstance(item, dict):
                continue
            field_name = _string_or_none(item.get("field_name"))
            if field_name is None:
                continue
            _classify(field_name, item.get("value"))

    consumer = parsed_report.get("consumer")
    if isinstance(consumer, dict):
        name = _normalize_name(consumer.get("name"))
        if name:
            names.add(name)
        for alias in consumer.get("aliases") or consumer.get("also_known_as") or []:
            alias_name = _normalize_name(alias)
            if alias_name:
                names.add(alias_name)
        ssn = _normalize_ssn(consumer.get("ssn") or consumer.get("social_security_number"))
        if ssn:
            ssns.add(ssn)
        dob = _parse_date(consumer.get("date_of_birth"))
        if dob is not None:
            dobs.add(dob.date().isoformat())
        for address in consumer.get("addresses") or []:
            normalized = _normalize_address(address)
            if normalized:
                addresses.add(normalized)

    for address in parsed_report.get("addresses") or []:
        normalized = _normalize_address(address)
        if normalized:
            addresses.add(normalized)

    return names, ssns, dobs, addresses


def _detect_personal_info_variations(
    parsed_report: dict[str, Any],
) -> list[IdentityTheftFinding]:
    names, ssns, dobs, addresses = _collect_personal_info(parsed_report)
    findings: list[IdentityTheftFinding] = []

    if len(ssns) >= 2:
        findings.append(
            _personal_info_finding(
                rule_id="identity_theft.personal_info.multiple_ssns",
                title="Multiple Social Security numbers on file",
                description=(
                    "This report lists more than one Social Security number. That can "
                    "indicate a mixed file (another person's data commingled) or identity "
                    "theft. This is an advisory signal — confirm with the consumer before "
                    "labeling any account."
                ),
                confidence=0.9,
                severity="high",
                fields=("personal_information", "ssn"),
                observed={"distinct_ssn_count": len(ssns)},
            )
        )

    if len(dobs) >= 2:
        findings.append(
            _personal_info_finding(
                rule_id="identity_theft.personal_info.multiple_dobs",
                title="Multiple dates of birth on file",
                description=(
                    "More than one date of birth appears on this report, a common "
                    "mixed-file indicator. Advisory only — verify identity data with the "
                    "consumer before disputing."
                ),
                confidence=0.85,
                severity="high",
                fields=("personal_information", "date_of_birth"),
                observed={"distinct_dob_count": len(dobs)},
            )
        )

    surnames = {surname for name in names if (surname := _surname(name)) is not None}
    if len(surnames) >= 2:
        findings.append(
            _personal_info_finding(
                rule_id="identity_theft.personal_info.name_variations",
                title="Name variations suggest a possible mixed file",
                description=(
                    "Multiple distinct surnames appear among the names on this report. "
                    "Nicknames and maiden names are common, but distinct surnames can "
                    "indicate a mixed file. Advisory only — confirm before disputing."
                ),
                confidence=0.7,
                severity="medium",
                fields=("personal_information", "name"),
                observed={
                    "distinct_name_count": len(names),
                    "distinct_surname_count": len(surnames),
                },
            )
        )

    if len(addresses) >= _ADDRESS_VARIATION_THRESHOLD:
        findings.append(
            _personal_info_finding(
                rule_id="identity_theft.personal_info.address_variations",
                title="Many address variations on file",
                description=(
                    f"{len(addresses)} distinct addresses appear on this report. Frequent "
                    "moves are legitimate, but a large number of addresses can indicate a "
                    "mixed file or identity theft. Advisory only — review with the consumer."
                ),
                confidence=0.6,
                severity="low",
                fields=("personal_information", "addresses"),
                observed={"distinct_address_count": len(addresses)},
            )
        )

    return findings


def evaluate_identity_theft(
    *,
    document_id: uuid.UUID,
    bureau: str,
    parsed_report: dict[str, Any],
) -> IdentityTheftEvaluationResult:
    """Evaluate report- and tradeline-level identity-theft indicators."""
    as_of = _resolve_as_of(parsed_report)
    report_text = _flatten_report_text(parsed_report)
    findings, protections = _detect_report_level_indicators(report_text)

    burst = _detect_inquiry_burst(parsed_report)
    if burst is not None:
        findings.append(burst)

    findings.extend(_detect_personal_info_variations(parsed_report))

    accounts = parsed_report.get("accounts")
    tradelines_evaluated = 0
    if isinstance(accounts, list):
        for index, account in enumerate(accounts):
            if not isinstance(account, dict):
                continue
            if not _string_or_none(account.get("creditor_name")):
                continue
            tradelines_evaluated += 1
            for rule in TRADELINE_RULES:
                finding = rule(index, account, parsed_report, as_of)
                if finding is not None:
                    findings.append(finding)

    report_level = any(f.detection_source == "REPORT_TEXT" for f in findings)
    banner_active = report_level or any(
        f.rule_id.startswith("identity_theft.report.") for f in findings
    )
    ordinary_locked = any(f.ordinary_dispute_locked for f in findings)

    summary = {
        "total": len(findings),
        "high": sum(1 for item in findings if item.severity == "high"),
        "medium": sum(1 for item in findings if item.severity == "medium"),
        "low": sum(1 for item in findings if item.severity == "low"),
        "tradelines_evaluated": tradelines_evaluated,
        "report_level_indicators": sum(
            1 for item in findings if item.detection_source == "REPORT_TEXT"
        ),
        "tradeline_indicators": sum(
            1 for item in findings if item.detection_source == "TRADELINE_HEURISTIC"
        ),
        "personal_info_indicators": sum(
            1 for item in findings if item.detection_source == "PERSONAL_INFO"
        ),
        "ordinary_dispute_locked_count": sum(
            1 for item in findings if item.ordinary_dispute_locked
        ),
    }
    schema_version = parsed_report.get("schema_version")
    return IdentityTheftEvaluationResult(
        document_id=document_id,
        bureau=bureau,
        schema_version=schema_version if isinstance(schema_version, str) else None,
        as_of_date=as_of.date().isoformat() if as_of is not None else None,
        banner_active=banner_active,
        banner_title=IDENTITY_THEFT_BANNER_TITLE if banner_active else None,
        banner_body=IDENTITY_THEFT_BANNER_BODY if banner_active else None,
        ordinary_dispute_locked=ordinary_locked,
        summary=summary,
        findings=tuple(findings),
        protections_detected=tuple(protections),
    )


# Alias for consistency with metro2/fcra evaluate_tradelines naming in service wiring.
evaluate_tradelines = evaluate_identity_theft


def classification_payload(finding: IdentityTheftFinding) -> dict[str, Any]:
    """Product-facing classification object (pre- or post-confirmation)."""
    payload: dict[str, Any] = {
        "issueType": finding.issue_type,
        "detectionSource": finding.detection_source,
        "confidence": finding.confidence,
        "consumerConfirmed": finding.consumer_confirmed,
        "legalPath": finding.legal_path,
        "ordinaryDisputeLocked": finding.ordinary_dispute_locked,
        "requiredAction": finding.required_action,
    }
    return payload


def confirmed_identity_theft_classification(
    *,
    packet_readiness: int,
    missing_evidence: list[str],
) -> dict[str, Any]:
    return {
        "issueType": "CONFIRMED_IDENTITY_THEFT_CLAIM",
        "consumerConfirmed": True,
        "legalPath": "FCRA_605B",
        "packetReadiness": packet_readiness,
        "missingEvidence": missing_evidence,
        "ordinaryDisputeLocked": True,
        "requiredAction": "PREPARE_605B",
    }


def assess_fcra_605b_readiness(
    *,
    has_proof_of_identity: bool | None = None,
    has_identity_theft_report: bool | None = None,
    has_identified_fraudulent_info: bool | None = None,
    has_consumer_statement: bool | None = None,
    has_proof_of_address: bool | None = None,
    has_supporting_creditor_records: bool | None = None,
) -> Fcra605bReadiness:
    """Assess FCRA §605B block packet readiness (separate from §611 disputes)."""

    def _status(value: bool | None, *, required: bool) -> EvidenceStatus:
        if value is True:
            return "present"
        if value is False:
            return "missing"
        return "unknown" if required else "unknown"

    items = (
        Fcra605bItem(
            item_id="PROOF_OF_IDENTITY",
            label="Proof of identity",
            required=True,
            status=_status(has_proof_of_identity, required=True),
        ),
        Fcra605bItem(
            item_id="FTC_IDENTITY_THEFT_REPORT",
            label="Identity Theft Report",
            required=True,
            status=_status(has_identity_theft_report, required=True),
        ),
        Fcra605bItem(
            item_id="IDENTIFIED_FRAUDULENT_TRADELINES",
            label="Identified fraudulent tradelines",
            required=True,
            status=_status(has_identified_fraudulent_info, required=True),
        ),
        Fcra605bItem(
            item_id="CONSUMER_STATEMENT",
            label="Consumer statement",
            required=True,
            status=_status(has_consumer_statement, required=True),
        ),
        Fcra605bItem(
            item_id="PROOF_OF_ADDRESS",
            label="Proof of address",
            required=False,
            status=_status(has_proof_of_address, required=False),
        ),
        Fcra605bItem(
            item_id="SUPPORTING_CREDITOR_RECORDS",
            label="Supporting creditor records",
            required=False,
            status=_status(has_supporting_creditor_records, required=False),
        ),
    )
    required = [item for item in items if item.required]
    optional = [item for item in items if not item.required]
    required_present = sum(1 for item in required if item.status == "present")
    optional_present = sum(1 for item in optional if item.status == "present")
    # Required items dominate readiness; optional items fill remainder.
    base = int((required_present / max(len(required), 1)) * 80)
    bonus = int((optional_present / max(len(optional), 1)) * 20)
    packet_readiness = min(100, base + bonus)
    missing = tuple(
        item.item_id for item in items if item.status in {"missing", "unknown"} and item.required
    ) + tuple(item.item_id for item in items if item.status == "missing" and not item.required)
    return Fcra605bReadiness(
        remedy_type="FCRA §605B Identity-Theft Block",
        not_ordinary_dispute=True,
        packet_readiness=packet_readiness,
        items=items,
        missing_evidence=missing,
    )


DEFAULT_EVIDENCE_CHECKLIST: tuple[dict[str, str], ...] = (
    {"item_id": "GOVERNMENT_ID", "label": "Government-issued identification"},
    {"item_id": "PROOF_OF_ADDRESS", "label": "Proof of current address"},
    {"item_id": "FTC_IDENTITY_THEFT_REPORT", "label": "FTC Identity Theft Report"},
    {"item_id": "POLICE_REPORT", "label": "Police report, if obtained or required"},
    {
        "item_id": "CREDIT_REPORT_PAGES",
        "label": "Credit-report pages showing fraudulent information",
    },
    {"item_id": "ACCOUNT_STATEMENTS", "label": "Account statements or collection letters"},
    {"item_id": "AFFIDAVITS", "label": "Affidavits or creditor correspondence"},
    {"item_id": "PROOF_LIVED_ELSEWHERE", "label": "Proof the consumer lived elsewhere"},
    {"item_id": "SIGNATURE_EVIDENCE", "label": "Signature or transaction evidence"},
    {"item_id": "DATA_BREACH_NOTICE", "label": "Data-breach notification, when relevant"},
)

RECOVERY_WORKFLOW_STEPS: tuple[dict[str, str], ...] = (
    {"step": "1", "title": "Contact the companies where fraud occurred"},
    {"step": "2", "title": "Place a fraud alert or security freeze"},
    {"step": "3", "title": "Obtain and review all three credit reports"},
    {"step": "4", "title": "Complete an FTC Identity Theft Report"},
    {"step": "5", "title": "Identify each fraudulent tradeline and inquiry"},
    {"step": "6", "title": "Prepare blocking requests for the credit bureaus"},
    {"step": "7", "title": "Send notices to furnishers and collectors"},
    {"step": "8", "title": "Track responses and blocked items"},
    {
        "step": "9",
        "title": "Escalate unresolved reporting through complaints or legal review",
    },
)

PROTECTION_TRACKING_TYPES: tuple[str, ...] = (
    "initial_fraud_alert",
    "extended_fraud_alert",
    "active_duty_alert",
    "equifax_freeze",
    "experian_freeze",
    "transunion_freeze",
)
