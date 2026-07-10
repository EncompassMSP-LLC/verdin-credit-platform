"""PDF rendering for consent document templates."""

from __future__ import annotations

import re
from io import BytesIO

from api.modules.compliance.consent_templates.keys import LEGAL_REVIEW_NOTICE


def build_consent_pdf_bytes(
    *,
    title: str,
    body_text: str,
    signer_name: str | None = None,
    signed_at_label: str | None = None,
) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    page_width, page_height = letter_page_size
    margin = 54
    line_height = 13
    y = page_height - margin

    def new_page() -> None:
        nonlocal y
        pdf.showPage()
        y = page_height - margin

    def draw_wrapped(
        text: str,
        *,
        font_name: str = "Helvetica",
        font_size: int = 10,
        indent: int = 0,
    ) -> None:
        nonlocal y
        pdf.setFont(font_name, font_size)
        max_chars = max(40, int((page_width - (2 * margin) - indent) / (font_size * 0.5)))
        for line in _wrap_lines(text, max_chars=max_chars):
            if y < margin + line_height:
                new_page()
            if not line:
                y -= line_height
                continue
            pdf.drawString(margin + indent, y, line)
            y -= line_height

    draw_wrapped(LEGAL_REVIEW_NOTICE, font_name="Helvetica-BoldOblique", font_size=9)
    y -= line_height
    draw_wrapped(title, font_name="Helvetica-Bold", font_size=14)
    y -= line_height

    for paragraph in _paragraphs(body_text):
        if paragraph.isupper() and len(paragraph) < 120:
            y -= line_height // 2
            draw_wrapped(paragraph, font_name="Helvetica-Bold", font_size=11)
        else:
            draw_wrapped(paragraph)
        y -= line_height // 2

    if signer_name:
        y -= line_height
        if y < margin + (line_height * 4):
            new_page()
        draw_wrapped("ELECTRONIC SIGNATURE RECORD", font_name="Helvetica-Bold", font_size=11)
        draw_wrapped(f"Signer: {signer_name}")
        if signed_at_label:
            draw_wrapped(f"Signed at: {signed_at_label}")
        draw_wrapped(
            "The signer acknowledged this document electronically through the client portal."
        )

    pdf.save()
    return buffer.getvalue()


def _paragraphs(text: str) -> list[str]:
    chunks = re.split(r"\n\s*\n", text.strip())
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _wrap_lines(text: str, *, max_chars: int = 95) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        stripped = paragraph.strip()
        if not stripped:
            lines.append("")
            continue
        words = stripped.split()
        current = ""
        for word in words:
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
