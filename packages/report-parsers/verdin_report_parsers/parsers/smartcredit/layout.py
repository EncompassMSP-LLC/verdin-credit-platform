"""SmartCredit monitoring / tri-merge credit report layout detection."""

from __future__ import annotations

import re
from dataclasses import dataclass

from verdin_report_parsers.acr_layout import split_sections as _split_sections

_SMARTCREDIT_BRANDING = re.compile(
    r"\bsmart\s*credit\b|smartcredit\.com|credit\s+report\s*-\s*smart\s*credit",
    re.I,
)
_PORTAL_URL = re.compile(
    r"(?:www\.|member\.|app\.)?smartcredit\.com(?:/[\w./-]*)?",
    re.I,
)
_TRI_BUREAU_HEADER = re.compile(
    r"\btrans\s*union\b.+\bexperian\b.+\bequifax\b"
    r"|\bexperian\b.+\btrans\s*union\b.+\bequifax\b"
    r"|\bequifax\b.+\bexperian\b.+\btrans\s*union\b",
    re.I | re.S,
)
_REPORT_HEADER = re.compile(
    r"credit\s+report\s*-\s*smart\s*credit|3[- ]bureau\s+credit\s+report|"
    r"smart\s*credit\s+(?:3[- ]bureau|tri[- ]merge)\s+report",
    re.I,
)

_SECTION_MARKERS: tuple[tuple[str, re.Pattern[str], float], ...] = (
    ("layout.personal_information", re.compile(r"\bpersonal\s+information\b", re.I), 0.12),
    ("layout.credit_summary", re.compile(r"\bcredit\s+summary\b", re.I), 0.08),
    (
        "layout.accounts",
        re.compile(r"\b(?:account\s+history|accounts|tradelines)\b", re.I),
        0.15,
    ),
    ("layout.inquiries", re.compile(r"\binquiries\b", re.I), 0.10),
    ("layout.public_records", re.compile(r"\bpublic\s+records\b", re.I), 0.08),
    ("layout.collections", re.compile(r"\bcollections?\b", re.I), 0.08),
)

_SECTION_HEADERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("personal_information", re.compile(r"^Personal Information\s*$", re.I | re.M)),
    ("credit_summary", re.compile(r"^Credit Summary\s*$", re.I | re.M)),
    ("accounts", re.compile(r"^(?:Account History|Accounts|Tradelines)\s*$", re.I | re.M)),
    ("inquiries", re.compile(r"^(?:Inquiries|Credit Inquiries)\s*$", re.I | re.M)),
    ("public_records", re.compile(r"^Public Records\s*$", re.I | re.M)),
    ("collections", re.compile(r"^Collections?\s*$", re.I | re.M)),
    ("personal_information", re.compile(r"^PERSONAL INFORMATION\s*$", re.I | re.M)),
    ("accounts", re.compile(r"^(?:ACCOUNT HISTORY|ACCOUNTS)\s*$", re.I | re.M)),
    ("inquiries", re.compile(r"^INQUIRIES\s*$", re.I | re.M)),
    ("public_records", re.compile(r"^PUBLIC RECORDS\s*$", re.I | re.M)),
    ("collections", re.compile(r"^COLLECTIONS?\s*$", re.I | re.M)),
)

_BRANDING_WEIGHT = 0.35
_PORTAL_WEIGHT = 0.20
_TRI_BUREAU_WEIGHT = 0.15
_HEADER_WEIGHT = 0.10


@dataclass(frozen=True, slots=True)
class LayoutScore:
    confidence: float
    signals: dict[str, float]


def is_smartcredit_layout(text: str) -> bool:
    return bool(_SMARTCREDIT_BRANDING.search(text))


def score_layout(text: str) -> LayoutScore:
    """Return deterministic layout confidence for SmartCredit monitoring reports."""
    if not _SMARTCREDIT_BRANDING.search(text):
        return LayoutScore(confidence=0.0, signals={})

    signals: dict[str, float] = {"layout.branding": _BRANDING_WEIGHT}
    total = _BRANDING_WEIGHT

    if _PORTAL_URL.search(text):
        signals["layout.portal_url"] = _PORTAL_WEIGHT
        total += _PORTAL_WEIGHT

    if _REPORT_HEADER.search(text):
        signals["layout.report_header"] = _HEADER_WEIGHT
        total += _HEADER_WEIGHT

    if _TRI_BUREAU_HEADER.search(text):
        signals["layout.tri_bureau"] = _TRI_BUREAU_WEIGHT
        total += _TRI_BUREAU_WEIGHT

    searchable = text.lower()
    for signal_name, pattern, weight in _SECTION_MARKERS:
        if pattern.search(searchable):
            signals[signal_name] = weight
            total += weight

    return LayoutScore(confidence=min(total, 1.0), signals=signals)


def split_sections(text: str) -> dict[str, str]:
    return _split_sections(text, _SECTION_HEADERS)
