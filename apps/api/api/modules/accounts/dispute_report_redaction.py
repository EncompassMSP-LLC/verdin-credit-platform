"""Build per-dispute credit report excerpts with other tradelines redacted."""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from typing import Any

# Fallback band when we cannot find the next account header on the page.
_TRADELINE_BLOCK_PADDING = 110.0
_PAGE_MARGIN = 4.0
# Gap left above the next creditor header so labels stay readable.
_NEXT_HEADER_GAP = 6.0


@dataclass(frozen=True, slots=True)
class RedactedTradelineExcerpt:
    pdf_bytes: bytes
    page_numbers: tuple[int, ...]
    redacted_creditor_count: int
    used_full_report_fallback: bool
    scanned_page_numbers: tuple[int, ...] | None = None


def locate_tradeline_pages(
    pdf_bytes: bytes,
    *,
    target_creditor: str,
    target_account_masked: str | None = None,
) -> tuple[int, ...] | None:
    """Return 1-based PDF page numbers that appear to mention the tradeline.

    Returns None when the file is not a PDF or the page scan cannot run.
    Returns an empty tuple when the PDF opens but no page matches.
    """
    if not pdf_bytes.startswith(b"%PDF"):
        return None

    target_tokens = _creditor_tokens(target_creditor)
    if not target_tokens and not target_account_masked:
        return None

    try:
        import pdfplumber
    except ImportError:
        return None

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            page_numbers: list[int] = []
            for index, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                if _page_matches_target(
                    page_text,
                    target_creditor=target_creditor,
                    target_tokens=target_tokens,
                    target_account_masked=target_account_masked,
                ):
                    page_numbers.append(index + 1)
            return tuple(page_numbers)
    except Exception:
        return None


def build_redacted_tradeline_excerpt(
    pdf_bytes: bytes,
    *,
    target_creditor: str,
    target_account_masked: str | None,
    other_creditors: tuple[str, ...],
    known_page_numbers: tuple[int, ...] | None = None,
) -> RedactedTradelineExcerpt | None:
    if not pdf_bytes.startswith(b"%PDF"):
        return None

    try:
        import pdfplumber
    except ImportError:
        return _fallback_full_report(pdf_bytes)

    target_tokens = _creditor_tokens(target_creditor)
    if not target_tokens:
        return _fallback_full_report(pdf_bytes)

    other_names = tuple(
        name
        for name in dict.fromkeys(other_creditors)
        if name and not _creditors_match(name, target_creditor)
    )

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            matching_pages: list[tuple[int, Any]] = []
            scanned_page_numbers: tuple[int, ...] | None = None
            if known_page_numbers is not None:
                if not known_page_numbers:
                    return _fallback_full_report(pdf_bytes)
                selected = _finalize_tradeline_pages(
                    known_page_numbers,
                    pdf=pdf,
                    target_creditor=target_creditor,
                    target_tokens=target_tokens,
                    target_account_masked=target_account_masked,
                )
                for page_number in selected:
                    index = page_number - 1
                    if 0 <= index < len(pdf.pages):
                        matching_pages.append((index, pdf.pages[index]))
            else:
                for index, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    if _page_matches_target(
                        page_text,
                        target_creditor=target_creditor,
                        target_tokens=target_tokens,
                        target_account_masked=target_account_masked,
                    ):
                        matching_pages.append((index, page))
                selected = _finalize_tradeline_pages(
                    tuple(index + 1 for index, _ in matching_pages),
                    pdf=pdf,
                    target_creditor=target_creditor,
                    target_tokens=target_tokens,
                    target_account_masked=target_account_masked,
                )
                matching_pages = [
                    (page_number - 1, pdf.pages[page_number - 1])
                    for page_number in selected
                    if 0 <= page_number - 1 < len(pdf.pages)
                ]
                scanned_page_numbers = selected

            if not matching_pages:
                return _fallback_full_report(
                    pdf_bytes,
                    scanned_page_numbers=scanned_page_numbers,
                )

            writer_buffer = BytesIO()
            from pypdf import PdfReader, PdfWriter

            writer = PdfWriter()
            reader = PdfReader(BytesIO(pdf_bytes))
            redacted_creditor_count = 0
            page_numbers: list[int] = []

            for page_index, page in matching_pages:
                page_number = page_index + 1
                page_numbers.append(page_number)
                redact_rects = _collect_redaction_rects(
                    page,
                    other_creditors=other_names,
                    target_creditor=target_creditor,
                )
                redacted_creditor_count += len(redact_rects)

                base_page = reader.pages[page_index]
                if redact_rects:
                    overlay = _build_redaction_overlay(
                        page_width=float(page.width),
                        page_height=float(page.height),
                        rects=redact_rects,
                    )
                    overlay_reader = PdfReader(BytesIO(overlay))
                    base_page.merge_page(overlay_reader.pages[0])
                writer.add_page(base_page)

            writer.write(writer_buffer)
            return RedactedTradelineExcerpt(
                pdf_bytes=writer_buffer.getvalue(),
                page_numbers=tuple(page_numbers),
                redacted_creditor_count=redacted_creditor_count,
                used_full_report_fallback=False,
                scanned_page_numbers=scanned_page_numbers,
            )
    except Exception:
        return _fallback_full_report(pdf_bytes)


def _fallback_full_report(
    pdf_bytes: bytes,
    *,
    scanned_page_numbers: tuple[int, ...] | None = None,
) -> RedactedTradelineExcerpt:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(pdf_bytes))
    return RedactedTradelineExcerpt(
        pdf_bytes=pdf_bytes,
        page_numbers=tuple(range(1, len(reader.pages) + 1)),
        redacted_creditor_count=0,
        used_full_report_fallback=True,
        scanned_page_numbers=scanned_page_numbers,
    )


def _page_matches_target(
    page_text: str,
    *,
    target_creditor: str,
    target_tokens: tuple[str, ...],
    target_account_masked: str | None,
) -> bool:
    normalized = _normalize_text(page_text)
    if _normalize_text(target_creditor) in normalized:
        return True
    if sum(1 for token in target_tokens if token in normalized) >= min(2, len(target_tokens)):
        return True
    if target_account_masked:
        digits = re.sub(r"\D", "", target_account_masked)
        if len(digits) >= 4 and digits[-4:] in re.sub(r"\D", "", page_text):
            return True
    return False


def _cluster_primary_pages(page_numbers: tuple[int, ...] | list[int]) -> list[int]:
    """Keep the longest near-contiguous page run; drop distant false positives."""
    sorted_pages = sorted({int(page) for page in page_numbers if int(page) > 0})
    if not sorted_pages:
        return []

    groups: list[list[int]] = [[sorted_pages[0]]]
    for page in sorted_pages[1:]:
        if page - groups[-1][-1] <= 1:
            groups[-1].append(page)
        else:
            groups.append([page])

    # Longest cluster wins; earliest page breaks ties (tradeline detail usually first).
    return max(groups, key=lambda group: (len(group), -group[0]))


def _finalize_tradeline_pages(
    page_numbers: tuple[int, ...] | list[int],
    *,
    pdf: Any,
    target_creditor: str,
    target_tokens: tuple[str, ...],
    target_account_masked: str | None,
) -> tuple[int, ...]:
    clustered = _cluster_primary_pages(page_numbers)
    if not clustered:
        return ()

    # Include an immediate continuation page when the tradeline spills onto the next sheet.
    next_page = clustered[-1] + 1
    if next_page not in clustered and next_page <= len(pdf.pages):
        page_text = pdf.pages[next_page - 1].extract_text() or ""
        if _page_matches_target(
            page_text,
            target_creditor=target_creditor,
            target_tokens=target_tokens,
            target_account_masked=target_account_masked,
        ):
            clustered.append(next_page)

    return tuple(clustered)


def _collect_redaction_rects(
    page: Any,
    *,
    other_creditors: tuple[str, ...],
    target_creditor: str,
) -> list[dict[str, float]]:
    """Black out non-target tradelines on a page.

    Experian (and similar) pages often end one account and start the next on the
    same sheet. A short padding under the other creditor name leaves payment
    history / contact blocks visible. Redact from each other-creditor header to
    the next header (or page bottom).
    """
    page_width = float(page.width)
    page_height = float(page.height)

    header_tops: list[float] = []
    for creditor in other_creditors:
        if _creditors_match(creditor, target_creditor):
            continue
        for query in _creditor_search_queries(creditor):
            for hit in page.search(query, case=False):
                header_tops.append(max(0.0, float(hit["top"]) - 4.0))

    if not header_tops:
        return []

    unique_tops = sorted(set(round(top, 1) for top in header_tops))
    rects: list[dict[str, float]] = []
    for index, top in enumerate(unique_tops):
        if index + 1 < len(unique_tops):
            bottom = max(top + _TRADELINE_BLOCK_PADDING, unique_tops[index + 1] - _NEXT_HEADER_GAP)
        else:
            bottom = page_height - _PAGE_MARGIN
        bottom = min(page_height - _PAGE_MARGIN, max(top + 1.0, bottom))
        rects.append(
            {
                "x0": _PAGE_MARGIN,
                "top": top,
                "x1": page_width - _PAGE_MARGIN,
                "bottom": bottom,
            }
        )

    return _merge_overlapping_rects(rects)


def _build_redaction_overlay(
    *,
    page_width: float,
    page_height: float,
    rects: list[dict[str, float]],
) -> bytes:
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    pdf.setFillColorRGB(0, 0, 0)
    for rect in rects:
        x = rect["x0"]
        width = rect["x1"] - rect["x0"]
        y = page_height - rect["bottom"]
        height = rect["bottom"] - rect["top"]
        pdf.rect(x, y, width, height, fill=1, stroke=0)
    pdf.save()
    return buffer.getvalue()


def _merge_overlapping_rects(rects: list[dict[str, float]]) -> list[dict[str, float]]:
    if not rects:
        return []

    sorted_rects = sorted(rects, key=lambda rect: (rect["top"], rect["x0"]))
    merged: list[dict[str, float]] = [sorted_rects[0]]
    for rect in sorted_rects[1:]:
        last = merged[-1]
        if rect["top"] <= last["bottom"] + 8:
            last["top"] = min(last["top"], rect["top"])
            last["bottom"] = max(last["bottom"], rect["bottom"])
            last["x0"] = min(last["x0"], rect["x0"])
            last["x1"] = max(last["x1"], rect["x1"])
        else:
            merged.append(rect)
    return merged


def _creditor_search_queries(creditor: str) -> tuple[str, ...]:
    normalized = creditor.strip()
    if not normalized:
        return ()
    queries = [normalized]
    if len(normalized) > 24:
        queries.append(normalized[:24])
    tokens = [token for token in _creditor_tokens(creditor) if len(token) >= 5]
    if len(tokens) >= 2:
        queries.append(" ".join(tokens[:2]))
    return tuple(dict.fromkeys(queries))


def _creditor_tokens(value: str) -> tuple[str, ...]:
    return tuple(
        token
        for token in re.split(r"[^a-z0-9]+", _normalize_text(value))
        if len(token) >= 3 and token not in {"inc", "llc", "bank", "corp", "the", "and"}
    )


def _creditors_match(left: str, right: str) -> bool:
    left_norm = _normalize_text(left)
    right_norm = _normalize_text(right)
    if not left_norm or not right_norm:
        return False
    if left_norm in right_norm or right_norm in left_norm:
        return True
    left_tokens = set(_creditor_tokens(left))
    right_tokens = set(_creditor_tokens(right))
    if not left_tokens or not right_tokens:
        return False
    overlap = left_tokens & right_tokens
    return len(overlap) >= min(2, len(left_tokens), len(right_tokens))


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def parsed_creditor_names(parsed_report: dict[str, object] | None) -> tuple[str, ...]:
    if not isinstance(parsed_report, dict):
        return ()
    accounts = parsed_report.get("accounts")
    if not isinstance(accounts, list):
        return ()
    names: list[str] = []
    for account in accounts:
        if not isinstance(account, dict):
            continue
        creditor = account.get("creditor_name")
        if isinstance(creditor, str) and creditor.strip():
            names.append(creditor.strip())
    return tuple(names)
