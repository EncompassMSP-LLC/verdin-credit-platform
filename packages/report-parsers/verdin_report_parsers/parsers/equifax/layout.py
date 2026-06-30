"""Equifax report layout detection and section segmentation."""

from __future__ import annotations

import re
from dataclasses import dataclass

_EQUIFAX_BRANDING = re.compile(r"\bequifax\b", re.I)
_REPORT_HEADER = re.compile(r"equifax\s+(consumer\s+)?credit\s+(file|report)", re.I)

_SECTION_MARKERS: tuple[tuple[str, re.Pattern[str], float], ...] = (
    ("layout.consumer_information", re.compile(r"\bconsumer\s+information\b", re.I), 0.15),
    ("layout.tradelines", re.compile(r"\btradelines\b", re.I), 0.15),
    ("layout.credit_inquiries", re.compile(r"\bcredit\s+inquiries\b", re.I), 0.10),
    (
        "layout.public_record_information",
        re.compile(r"\bpublic\s+record\s+information\b", re.I),
        0.10,
    ),
    ("layout.collection_accounts", re.compile(r"\bcollection\s+accounts\b", re.I), 0.10),
    ("layout.account_summary", re.compile(r"\baccount\s+summary\b", re.I), 0.05),
)

_SECTION_HEADERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("consumer_information", re.compile(r"^CONSUMER INFORMATION\s*$", re.I | re.M)),
    ("tradelines", re.compile(r"^TRADELINES\s*$", re.I | re.M)),
    ("credit_inquiries", re.compile(r"^CREDIT INQUIRIES\s*$", re.I | re.M)),
    (
        "public_record_information",
        re.compile(r"^PUBLIC RECORD INFORMATION\s*$", re.I | re.M),
    ),
    ("collection_accounts", re.compile(r"^COLLECTION ACCOUNTS\s*$", re.I | re.M)),
    ("account_summary", re.compile(r"^ACCOUNT SUMMARY\s*$", re.I | re.M)),
)

_BRANDING_WEIGHT = 0.20
_HEADER_WEIGHT = 0.15


@dataclass(frozen=True, slots=True)
class LayoutScore:
    confidence: float
    signals: dict[str, float]


def score_layout(text: str) -> LayoutScore:
    """Return deterministic layout confidence from Equifax report heuristics."""
    searchable = text.lower()
    if not _EQUIFAX_BRANDING.search(searchable):
        return LayoutScore(confidence=0.0, signals={})

    signals: dict[str, float] = {"layout.branding": _BRANDING_WEIGHT}
    total = _BRANDING_WEIGHT

    if _REPORT_HEADER.search(searchable):
        signals["layout.report_header"] = _HEADER_WEIGHT
        total += _HEADER_WEIGHT

    for signal_name, pattern, weight in _SECTION_MARKERS:
        if pattern.search(searchable):
            signals[signal_name] = weight
            total += weight

    return LayoutScore(confidence=min(total, 1.0), signals=signals)


def split_sections(text: str) -> dict[str, str]:
    """Split OCR text into Equifax section bodies keyed by section name."""
    matches: list[tuple[int, str]] = []
    for section_name, pattern in _SECTION_HEADERS:
        for match in pattern.finditer(text):
            matches.append((match.start(), section_name))

    if not matches:
        return {}

    matches.sort(key=lambda item: item[0])
    sections: dict[str, str] = {}
    for index, (start, section_name) in enumerate(matches):
        header_end = text.find("\n", start)
        body_start = start if header_end == -1 else header_end + 1
        body_end = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        sections[section_name] = text[body_start:body_end].strip()

    return sections
