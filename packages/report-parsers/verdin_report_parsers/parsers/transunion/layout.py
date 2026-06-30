"""TransUnion report layout detection and section segmentation."""

from __future__ import annotations

import re
from dataclasses import dataclass

_TRANSUNION_BRANDING = re.compile(r"\btrans\s*union\b|\btransunion\b", re.I)
_REPORT_HEADER = re.compile(
    r"trans\s*union\s+(consumer\s+)?credit\s+(report|disclosure)",
    re.I,
)

_SECTION_MARKERS: tuple[tuple[str, re.Pattern[str], float], ...] = (
    ("layout.personal_information", re.compile(r"\bpersonal\s+information\b", re.I), 0.15),
    ("layout.accounts", re.compile(r"\baccounts\b", re.I), 0.15),
    ("layout.inquiries", re.compile(r"\binquiries\b", re.I), 0.10),
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
)

_BRANDING_WEIGHT = 0.20
_HEADER_WEIGHT = 0.15


@dataclass(frozen=True, slots=True)
class LayoutScore:
    confidence: float
    signals: dict[str, float]


def score_layout(text: str) -> LayoutScore:
    """Return deterministic layout confidence from TransUnion report heuristics."""
    searchable = text.lower()
    if not _TRANSUNION_BRANDING.search(searchable):
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
    """Split OCR text into TransUnion section bodies keyed by section name."""
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
