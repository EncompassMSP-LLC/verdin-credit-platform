"""Shared helpers for Annual Credit Report (ACR) portal layouts."""

from __future__ import annotations

import re

_COMPETITOR_MARKERS: dict[str, tuple[re.Pattern[str], ...]] = {
    "experian": (
        re.compile(r"\btrans\s*union\b|\btransunion\b", re.I),
        re.compile(r"\bequifax\b", re.I),
        re.compile(r"EFX-ACR", re.I),
        re.compile(r"annualcreditreport\.transunion\.com", re.I),
    ),
    "equifax": (
        re.compile(r"\btrans\s*union\b|\btransunion\b", re.I),
        re.compile(r"\bexperian\b", re.I),
        re.compile(r"usa\.experian\.com", re.I),
        re.compile(r"annualcreditreport\.transunion\.com", re.I),
    ),
    "transunion": (
        re.compile(r"\bequifax\b", re.I),
        re.compile(r"EFX-ACR", re.I),
        re.compile(r"\bexperian\b", re.I),
        re.compile(r"usa\.experian\.com", re.I),
    ),
}

_COMPETITOR_PENALTY = 0.35


_STRONG_OWN_MARKERS: dict[str, re.Pattern[str]] = {
    "experian": re.compile(r"usa\.experian\.com|\bdate generated\b", re.I),
    "equifax": re.compile(r"EFX-ACR|prepared for:", re.I),
    "transunion": re.compile(
        r"annualcreditreport\.transunion\.com|personal credit report for:",
        re.I,
    ),
}


def apply_competitor_penalty(bureau: str, confidence: float, text: str) -> float:
    """Reduce layout confidence when another bureau's portal markers dominate."""
    own_marker = _STRONG_OWN_MARKERS.get(bureau)
    if own_marker and own_marker.search(text):
        return confidence

    markers = _COMPETITOR_MARKERS.get(bureau, ())
    if any(marker.search(text) for marker in markers):
        return max(0.0, confidence - _COMPETITOR_PENALTY)
    return confidence


def split_sections(text: str, headers: tuple[tuple[str, re.Pattern[str]], ...]) -> dict[str, str]:
    """Split OCR text into section bodies using one or more header patterns per section."""
    matches: list[tuple[int, str]] = []
    for section_name, pattern in headers:
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
        body = text[body_start:body_end].strip()
        if section_name in sections:
            sections[section_name] = f"{sections[section_name]}\n\n{body}".strip()
        else:
            sections[section_name] = body

    return sections
