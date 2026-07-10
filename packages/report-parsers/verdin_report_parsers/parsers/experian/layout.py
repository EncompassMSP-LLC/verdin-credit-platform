"""Experian report layout detection and section segmentation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from verdin_report_parsers.acr_layout import apply_competitor_penalty, split_sections as _split_sections

_EXPERIAN_BRANDING = re.compile(r"\bexperian\b", re.I)
_REPORT_HEADER = re.compile(r"experian\s+(consumer\s+)?credit\s+report", re.I)
_ACR_PORTAL = re.compile(r"usa\.experian\.com|annual credit report\s*-\s*experian", re.I)
_ACR_DATE_GENERATED = re.compile(r"\bdate generated\b", re.I)

_SECTION_MARKERS: tuple[tuple[str, re.Pattern[str], float], ...] = (
    ("layout.personal_information", re.compile(r"\bpersonal\s+information\b", re.I), 0.15),
    ("layout.accounts", re.compile(r"\baccounts\b", re.I), 0.15),
    ("layout.inquiries", re.compile(r"\b(?:hard\s+)?inquiries\b", re.I), 0.10),
    ("layout.public_records", re.compile(r"\bpublic\s+records\b", re.I), 0.10),
    ("layout.collections", re.compile(r"\bcollections\b", re.I), 0.10),
    ("layout.credit_summary", re.compile(r"\bcredit\s+summary\b", re.I), 0.05),
)

_SECTION_HEADERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("personal_information", re.compile(r"^PERSONAL INFORMATION\s*$", re.I | re.M)),
    ("accounts", re.compile(r"^ACCOUNTS\s*$", re.I | re.M)),
    ("inquiries", re.compile(r"^INQUIRIES\s*$", re.I | re.M)),
    ("public_records", re.compile(r"^PUBLIC RECORDS\s*$", re.I | re.M)),
    ("collections", re.compile(r"^COLLECTIONS\s*$", re.I | re.M)),
    ("credit_summary", re.compile(r"^CREDIT SUMMARY\s*$", re.I | re.M)),
    # Annual Credit Report portal (title-case headers)
    ("personal_information", re.compile(r"^Personal Information\s*$", re.I | re.M)),
    ("accounts", re.compile(r"^Accounts\s*$", re.I | re.M)),
    ("hard_inquiries", re.compile(r"^Hard Inquiries\s*$", re.I | re.M)),
    ("soft_inquiries", re.compile(r"^Soft Inquiries\s*$", re.I | re.M)),
    ("public_records", re.compile(r"^Public Records(?:\s+Information)?\s*$", re.I | re.M)),
)

_BRANDING_WEIGHT = 0.20
_HEADER_WEIGHT = 0.15
_ACR_PORTAL_WEIGHT = 0.20


@dataclass(frozen=True, slots=True)
class LayoutScore:
    confidence: float
    signals: dict[str, float]


def is_acr_layout(text: str) -> bool:
    searchable = text.lower()
    return bool(_ACR_PORTAL.search(searchable) or _ACR_DATE_GENERATED.search(searchable))


def score_layout(text: str) -> LayoutScore:
    """Return deterministic layout confidence from Experian report heuristics."""
    searchable = text.lower()
    if not _EXPERIAN_BRANDING.search(searchable):
        return LayoutScore(confidence=0.0, signals={})

    signals: dict[str, float] = {"layout.branding": _BRANDING_WEIGHT}
    total = _BRANDING_WEIGHT

    if _REPORT_HEADER.search(searchable):
        signals["layout.report_header"] = _HEADER_WEIGHT
        total += _HEADER_WEIGHT

    if _ACR_PORTAL.search(searchable) or _ACR_DATE_GENERATED.search(searchable):
        signals["layout.acr_portal"] = _ACR_PORTAL_WEIGHT
        total += _ACR_PORTAL_WEIGHT

    for signal_name, pattern, weight in _SECTION_MARKERS:
        if pattern.search(searchable):
            signals[signal_name] = weight
            total += weight

    confidence = apply_competitor_penalty("experian", min(total, 1.0), text)
    return LayoutScore(confidence=confidence, signals=signals)


def split_sections(text: str) -> dict[str, str]:
    """Split OCR text into Experian section bodies keyed by section name."""
    return _split_sections(text, _SECTION_HEADERS)
