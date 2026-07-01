"""Export helpers for persisted dispute letters."""

from __future__ import annotations

import re
from io import BytesIO
from typing import Literal

from api.modules.accounts.dispute_letter_models import DisputeLetter

DisputeLetterExportFormat = Literal["text", "pdf"]

_MEDIA_TYPES: dict[DisputeLetterExportFormat, str] = {
    "text": "text/plain; charset=utf-8",
    "pdf": "application/pdf",
}


def export_filename(dispute_letter: DisputeLetter, export_format: DisputeLetterExportFormat) -> str:
    short_id = str(dispute_letter.id).split("-", 1)[0]
    extension = "txt" if export_format == "text" else "pdf"
    return f"dispute-letter-{short_id}.{extension}"


def export_media_type(export_format: DisputeLetterExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def build_dispute_letter_plain_text(dispute_letter: DisputeLetter) -> str:
    sections: list[str] = [
        dispute_letter.subject,
        "",
        dispute_letter.body,
        "",
        "DISPUTED ITEMS",
        *_bullet_lines(dispute_letter.disputed_items),
        "",
        "REQUESTED ACTION",
        dispute_letter.requested_action,
        "",
        "EVIDENCE CHECKLIST",
        *_bullet_lines(dispute_letter.evidence_checklist),
        "",
        "COMPLIANCE NOTES",
        *_bullet_lines(dispute_letter.compliance_notes),
    ]
    return "\n".join(sections).strip() + "\n"


def build_dispute_letter_pdf_bytes(dispute_letter: DisputeLetter) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    page_width, page_height = letter_page_size
    margin = 72
    line_height = 14
    y = page_height - margin

    def new_page() -> None:
        nonlocal y
        pdf.showPage()
        y = page_height - margin

    def draw_wrapped(text: str, *, font_name: str = "Helvetica", font_size: int = 11) -> None:
        nonlocal y
        pdf.setFont(font_name, font_size)
        for line in _wrap_lines(text):
            if y < margin:
                new_page()
            if not line:
                y -= line_height
                continue
            pdf.drawString(margin, y, line)
            y -= line_height

    draw_wrapped(dispute_letter.subject, font_name="Helvetica-Bold", font_size=12)
    y -= line_height
    draw_wrapped(dispute_letter.body)
    y -= line_height

    for heading, items in (
        ("DISPUTED ITEMS", dispute_letter.disputed_items),
        ("REQUESTED ACTION", [dispute_letter.requested_action]),
        ("EVIDENCE CHECKLIST", dispute_letter.evidence_checklist),
        ("COMPLIANCE NOTES", dispute_letter.compliance_notes),
    ):
        y -= line_height
        draw_wrapped(heading, font_name="Helvetica-Bold", font_size=11)
        for item in items:
            draw_wrapped(f"- {item}")

    pdf.save()
    return buffer.getvalue()


def build_dispute_letter_export(
    dispute_letter: DisputeLetter,
    export_format: DisputeLetterExportFormat,
) -> tuple[bytes, str, str]:
    filename = export_filename(dispute_letter, export_format)
    media_type = export_media_type(export_format)
    if export_format == "text":
        content = build_dispute_letter_plain_text(dispute_letter).encode("utf-8")
    else:
        content = build_dispute_letter_pdf_bytes(dispute_letter)
    return content, filename, media_type


def _bullet_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- (none)"]
    return [f"- {item}" for item in items]


def _wrap_lines(text: str, *, max_chars: int = 90) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        stripped = paragraph.strip()
        if not stripped:
            lines.append("")
            continue
        current = ""
        for word in stripped.split():
            candidate = f"{current} {word}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def sanitize_content_disposition_filename(filename: str) -> str:
    safe = re.sub(r"[^\w.\-]", "_", filename)
    return safe or "dispute-letter.txt"
