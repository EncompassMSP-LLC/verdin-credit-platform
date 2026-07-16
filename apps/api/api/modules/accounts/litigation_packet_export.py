"""Export of the litigation-readiness evidence packet (Phase 12 / 13).

Renders an already-assembled :class:`AccountLitigationPacket` into a human-readable
text or PDF document for a **licensed attorney to review**. This is a pure
formatter — it performs no assembly, no scoring, no I/O, and no network calls.

Guardrails: the export is a manual attorney handoff. The platform never files suit,
drafts pleadings, transmits the document anywhere, or contacts a court/bureau. The
packet's disclaimer is reproduced prominently at the top of every export.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Literal

from api.modules.accounts.schemas import (
    AccountLitigationPacket,
    LitigationPacketLetter,
    LitigationPacketResponse,
)

LitigationPacketExportFormat = Literal["text", "pdf"]

_MEDIA_TYPES: dict[LitigationPacketExportFormat, str] = {
    "text": "text/plain; charset=utf-8",
    "pdf": "application/pdf",
}


def export_media_type(export_format: LitigationPacketExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def export_filename(
    packet: AccountLitigationPacket, export_format: LitigationPacketExportFormat
) -> str:
    short_id = str(packet.account_id).split("-", 1)[0]
    extension = "txt" if export_format == "text" else "pdf"
    return f"litigation-packet-{short_id}.{extension}"


def _bullet_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- (none)"]
    return [f"- {item}" for item in items]


def _format_date(value: object) -> str:
    if value is None:
        return "—"
    return str(value)


def build_litigation_packet_text(packet: AccountLitigationPacket) -> str:
    """Render the packet as a plain-text attorney-review document."""
    assessment = packet.assessment
    cross_bureau = packet.cross_bureau

    sections: list[str] = [
        "LITIGATION-READINESS EVIDENCE PACKET",
        "For licensed-attorney review only — not legal advice.",
        "",
        "DISCLAIMER",
        packet.disclaimer,
        "",
        "TRADELINE",
        f"- Creditor: {packet.creditor_name}",
        f"- Bureau: {packet.bureau}",
        f"- Dispute status: {packet.dispute_status}",
        f"- Dispute round: {packet.dispute_round}",
        f"- Risk score: {packet.risk_score if packet.risk_score is not None else '—'}",
        f"- Latest outcome: {packet.latest_outcome or '—'}",
        f"- Recommended next action (advisory): {packet.recommended_action}",
        f"- Generated at: {_format_date(packet.generated_at)}",
        "",
        "§611 REINVESTIGATION CLOCK",
        f"- State: {packet.clock_state}",
        f"- Deadline: {_format_date(packet.clock_deadline)}",
        f"- Extended 45-day window: {'yes' if packet.clock_extended else 'no'}",
        "",
        "WILLFUL-NONCOMPLIANCE ASSESSMENT (ADVISORY)",
        f"- Strength: {assessment.strength}",
        f"- Score: {assessment.score}/100",
        f"- Eligible for attorney handoff: {'yes' if assessment.eligible else 'no'}",
        f"- Summary: {assessment.summary}",
        "",
        "INDICATORS",
        *_bullet_lines(assessment.indicators),
        "",
        "CROSS-BUREAU DISCREPANCIES",
        (
            f"Compared bureaus: {', '.join(cross_bureau.compared_bureaus)}"
            if cross_bureau.compared_bureaus
            else "Compared bureaus: (none — no same-creditor tradelines at other bureaus)"
        ),
        *_bullet_lines([f"[{d.kind}] {d.detail}" for d in cross_bureau.discrepancies]),
        "",
        f"DISPUTE ROUNDS MAILED ({len(packet.letters)})",
        *_letter_lines(packet.letters),
        "",
        f"RECORDED RESPONSES ({len(packet.responses)})",
        *_response_lines(packet.responses),
    ]
    return "\n".join(sections).strip() + "\n"


def _letter_lines(letters: list[LitigationPacketLetter]) -> list[str]:
    if not letters:
        return ["- (none)"]
    return [
        f"- {letter.subject} [{letter.status}] to {letter.recipient_type}, "
        f"sent {_format_date(letter.sent_at)}"
        for letter in letters
    ]


def _response_lines(responses: list[LitigationPacketResponse]) -> list[str]:
    if not responses:
        return ["- (none)"]
    return [
        f"- {response.outcome} via {response.response_method} "
        f"on {_format_date(response.response_date)}"
        for response in responses
    ]


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


def build_litigation_packet_pdf_bytes(packet: AccountLitigationPacket) -> bytes:
    """Render the packet as a multi-page PDF using the same content as the text export."""
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    page_width, page_height = letter_page_size
    margin = 72
    line_height = 14
    y = page_height - margin
    text = build_litigation_packet_text(packet)

    def new_page() -> None:
        nonlocal y
        pdf.showPage()
        y = page_height - margin

    heading_markers = {
        "LITIGATION-READINESS EVIDENCE PACKET",
        "DISCLAIMER",
        "TRADELINE",
        "§611 REINVESTIGATION CLOCK",
        "WILLFUL-NONCOMPLIANCE ASSESSMENT (ADVISORY)",
        "INDICATORS",
        "CROSS-BUREAU DISCREPANCIES",
    }

    for raw_line in text.splitlines():
        is_heading = (
            raw_line in heading_markers
            or raw_line.startswith("DISPUTE ROUNDS MAILED")
            or raw_line.startswith("RECORDED RESPONSES")
        )
        font_name = "Helvetica-Bold" if is_heading else "Helvetica"
        font_size = 12 if raw_line == "LITIGATION-READINESS EVIDENCE PACKET" else 11
        pdf.setFont(font_name, font_size)
        for wrapped in _wrap_lines(raw_line if raw_line else " "):
            if y < margin:
                new_page()
                pdf.setFont(font_name, font_size)
            if not wrapped.strip():
                y -= line_height
                continue
            # reportlab Helvetica lacks §; substitute a plain label for PDF glyphs.
            draw_text = wrapped.replace("§", "Section ")
            pdf.drawString(margin, y, draw_text)
            y -= line_height

    pdf.save()
    return buffer.getvalue()


def build_litigation_packet_export(
    packet: AccountLitigationPacket,
    export_format: LitigationPacketExportFormat,
) -> tuple[bytes, str, str]:
    filename = export_filename(packet, export_format)
    media_type = export_media_type(export_format)
    if export_format == "text":
        content = build_litigation_packet_text(packet).encode("utf-8")
    else:
        content = build_litigation_packet_pdf_bytes(packet)
    return content, filename, media_type


def sanitize_content_disposition_filename(filename: str) -> str:
    safe = re.sub(r"[^\w.\-]", "_", filename)
    return safe or "litigation-packet.txt"
