"""Render dispute-strategy checklist packets as staff-mediated markdown exports."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal

_FOOTER = (
    "---\n"
    "Staff-mediated export only. Does not file with CFPB or transmit to counsel. "
    "Use checklist packet.zip for best-effort exhibit bundling (identity, proof of "
    "address, credit reports, bureau responses, and optional dispute letters as text "
    "or PDF via letter_format; opt-in mail-packet PDFs require signed consents), "
    "or mail-packet / report-excerpt downloads for dispute correspondence.\n"
)

_CATEGORY_ORDER: tuple[str, ...] = ("correspondence", "evidence", "chronology", "filing")


def checklist_export_filename(
    kind: Literal["cfpb", "attorney"],
    case_id: uuid.UUID,
    *,
    export_format: Literal["md", "pdf"] = "md",
) -> str:
    short = str(case_id).replace("-", "")[:8]
    extension = "pdf" if export_format == "pdf" else "md"
    return f"{kind}-checklist-{short}.{extension}"


def _item_line(item: Any) -> str:
    required = "required" if bool(getattr(item, "required", False)) else "optional"
    status = getattr(item, "completion_status", None) or "unknown"
    source = getattr(item, "completion_source", None) or "computed"
    staff_suffix = " (staff)" if source == "staff" else ""
    title = getattr(item, "title", "") or ""
    detail = getattr(item, "detail", "") or ""
    note = getattr(item, "override_note", None) if source == "staff" else None
    lines = [f"- [{required}] **{status}**{staff_suffix} — {title}"]
    if detail:
        lines.append(f"  - {detail}")
    if note:
        lines.append(f"  - Staff note: {note}")
    return "\n".join(lines)


def _render_account_section(account: Any, *, include_escalation: bool) -> str:
    creditor = getattr(account, "creditor_name", None) or "Unknown creditor"
    masked = getattr(account, "account_number_masked", None)
    title = f"{creditor}" + (f" · {masked}" if masked else "")
    score = getattr(account, "top_score", 0)
    lines = [
        f"## Account: {title} (top {score}/100)",
        f"- Key: `{getattr(account, 'account_key', '')}`",
        f"- Bureau: {getattr(account, 'bureau', None) or '—'}",
        f"- Match key: {getattr(account, 'match_key', None) or '—'}",
    ]
    rules = list(getattr(account, "primary_rule_ids", []) or [])
    lines.append(f"- Rules: {', '.join(f'`{rule}`' for rule in rules) if rules else '—'}")
    if include_escalation:
        flagged = bool(getattr(account, "attorney_escalation", False))
        lines.append(f"- Escalation: {'yes' if flagged else 'no'}")
    lines.append("")

    items: Sequence[Any] = tuple(getattr(account, "items", ()) or ())
    by_category: dict[str, list[Any]] = {category: [] for category in _CATEGORY_ORDER}
    for item in items:
        category = getattr(item, "category", "filing")
        by_category.setdefault(category, []).append(item)

    for category in _CATEGORY_ORDER:
        category_items = by_category.get(category) or []
        if not category_items:
            continue
        lines.append(f"### {category.title()}")
        for item in category_items:
            lines.append(_item_line(item))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_summary(summary: Any, *, include_escalation: bool) -> list[str]:
    lines = [
        "## Summary",
        f"- Accounts listed: {getattr(summary, 'accounts_listed', 0)}",
        (
            f"- Required / optional: {getattr(summary, 'required_items', 0)} / "
            f"{getattr(summary, 'optional_items', 0)}"
        ),
        (
            f"- Present / missing / unknown: {getattr(summary, 'items_present', 0)} / "
            f"{getattr(summary, 'items_missing', 0)} / {getattr(summary, 'items_unknown', 0)}"
        ),
    ]
    if include_escalation:
        lines.append(f"- Escalation-flagged: {getattr(summary, 'escalation_flagged', 0)}")
    lines.append("")
    return lines


def render_cfpb_checklist_markdown(checklist: Any) -> str:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# CFPB escalation checklist",
        f"Case ID: {getattr(checklist, 'case_id', '')}",
        f"Generated: {generated}",
        "",
        f"> {getattr(checklist, 'disclaimer', '')}",
        "",
    ]
    lines.extend(_render_summary(getattr(checklist, "summary", None), include_escalation=False))
    accounts = list(getattr(checklist, "accounts", []) or [])
    if not accounts:
        lines.append("No accounts listed for CFPB escalation.")
        lines.append("")
    else:
        for account in accounts:
            lines.append(_render_account_section(account, include_escalation=False))
    lines.append(_FOOTER)
    return "\n".join(lines)


def render_attorney_checklist_markdown(checklist: Any) -> str:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Attorney-preserve checklist",
        f"Case ID: {getattr(checklist, 'case_id', '')}",
        f"Generated: {generated}",
        "",
        f"> {getattr(checklist, 'disclaimer', '')}",
        "",
    ]
    lines.extend(_render_summary(getattr(checklist, "summary", None), include_escalation=True))
    accounts = list(getattr(checklist, "accounts", []) or [])
    if not accounts:
        lines.append("No accounts listed for attorney preserve.")
        lines.append("")
    else:
        for account in accounts:
            lines.append(_render_account_section(account, include_escalation=True))
    lines.append(_FOOTER)
    return "\n".join(lines)


def _wrap_pdf_line(text: str, *, max_chars: int = 95) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return [""]
    if len(cleaned) <= max_chars:
        return [cleaned]
    words = cleaned.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines or [""]


def _build_checklist_pdf_lines(
    checklist: Any,
    *,
    title: str,
    include_escalation: bool,
    empty_message: str,
) -> list[str]:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        title,
        f"Case ID: {getattr(checklist, 'case_id', '')}",
        f"Generated: {generated}",
        "",
        str(getattr(checklist, "disclaimer", "") or ""),
        "",
    ]
    summary = getattr(checklist, "summary", None)
    lines.extend(
        line.lstrip("# ").lstrip("- ")
        for line in _render_summary(summary, include_escalation=include_escalation)
        if line != ""
    )
    lines.append("")
    accounts = list(getattr(checklist, "accounts", []) or [])
    if not accounts:
        lines.append(empty_message)
    else:
        for account in accounts:
            section = _render_account_section(account, include_escalation=include_escalation)
            for raw in section.splitlines():
                cleaned = raw.replace("**", "").replace("`", "").lstrip("# ").replace("- [", "[")
                lines.append(cleaned)
            lines.append("")
    lines.append("Staff-mediated export only. Does not file with CFPB or transmit to counsel.")
    return lines


def render_checklist_pdf(
    checklist: Any,
    *,
    title: str,
    include_escalation: bool,
    empty_message: str,
) -> bytes:
    from io import BytesIO

    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    page_width, page_height = letter_page_size
    margin = 54
    line_height = 13
    y = page_height - margin
    pdf.setTitle(title)

    def new_page() -> None:
        nonlocal y
        pdf.showPage()
        y = page_height - margin

    for raw_line in _build_checklist_pdf_lines(
        checklist,
        title=title,
        include_escalation=include_escalation,
        empty_message=empty_message,
    ):
        font_name = (
            "Helvetica-Bold"
            if raw_line in {title} or raw_line.startswith("Account:")
            else "Helvetica"
        )
        font_size = 14 if raw_line == title else 10
        pdf.setFont(font_name, font_size)
        for segment in _wrap_pdf_line(raw_line, max_chars=100):
            if y < margin:
                new_page()
                pdf.setFont(font_name, font_size)
            if not segment:
                y -= line_height
                continue
            pdf.drawString(margin, y, segment[:120])
            y -= line_height

    pdf.save()
    return buffer.getvalue()


def render_cfpb_checklist_pdf(checklist: Any) -> bytes:
    return render_checklist_pdf(
        checklist,
        title="CFPB escalation checklist",
        include_escalation=False,
        empty_message="No accounts listed for CFPB escalation.",
    )


def render_attorney_checklist_pdf(checklist: Any) -> bytes:
    return render_checklist_pdf(
        checklist,
        title="Attorney-preserve checklist",
        include_escalation=True,
        empty_message="No accounts listed for attorney preserve.",
    )
