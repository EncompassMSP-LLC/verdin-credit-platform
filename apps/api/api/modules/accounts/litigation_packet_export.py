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


def build_litigation_packet_pdf_bytes(packet: AccountLitigationPacket) -> bytes:
    """Render the packet as a structured multi-section PDF for attorney review."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter_page_size,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Litigation-readiness evidence packet",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LitigationTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a1a"),
    )
    subtitle_style = ParagraphStyle(
        "LitigationSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=13,
        spaceAfter=14,
        textColor=colors.HexColor("#444444"),
    )
    section_style = ParagraphStyle(
        "LitigationSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a1a"),
    )
    body_style = ParagraphStyle(
        "LitigationBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "LitigationBullet",
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=3,
    )

    def esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("§", "Section ")
        )

    def section_heading(title: str) -> Paragraph:
        return Paragraph(esc(title), section_style)

    def bullet_list(items: list[str]) -> ListFlowable:
        if not items:
            items = ["(none)"]
        return ListFlowable(
            [ListItem(Paragraph(esc(item), bullet_style), leftIndent=12) for item in items],
            bulletType="bullet",
            start=None,
            leftIndent=18,
        )

    assessment = packet.assessment
    cross_bureau = packet.cross_bureau
    story: list[object] = [
        Paragraph("LITIGATION-READINESS EVIDENCE PACKET", title_style),
        Paragraph("For licensed-attorney review only — not legal advice.", subtitle_style),
        section_heading("DISCLAIMER"),
        Paragraph(esc(packet.disclaimer), body_style),
        Spacer(1, 6),
        section_heading("TRADELINE"),
        bullet_list(
            [
                f"Creditor: {packet.creditor_name}",
                f"Bureau: {packet.bureau}",
                f"Dispute status: {packet.dispute_status}",
                f"Dispute round: {packet.dispute_round}",
                f"Risk score: {packet.risk_score if packet.risk_score is not None else '—'}",
                f"Latest outcome: {packet.latest_outcome or '—'}",
                f"Recommended next action (advisory): {packet.recommended_action}",
                f"Generated at: {_format_date(packet.generated_at)}",
            ]
        ),
        section_heading("SECTION 611 REINVESTIGATION CLOCK"),
        bullet_list(
            [
                f"State: {packet.clock_state}",
                f"Deadline: {_format_date(packet.clock_deadline)}",
                f"Extended 45-day window: {'yes' if packet.clock_extended else 'no'}",
            ]
        ),
        section_heading("WILLFUL-NONCOMPLIANCE ASSESSMENT (ADVISORY)"),
        bullet_list(
            [
                f"Strength: {assessment.strength}",
                f"Score: {assessment.score}/100",
                f"Eligible for attorney handoff: {'yes' if assessment.eligible else 'no'}",
                f"Summary: {assessment.summary}",
            ]
        ),
        section_heading("INDICATORS"),
        bullet_list(assessment.indicators),
        section_heading("CROSS-BUREAU DISCREPANCIES"),
        Paragraph(
            esc(
                f"Compared bureaus: {', '.join(cross_bureau.compared_bureaus)}"
                if cross_bureau.compared_bureaus
                else "Compared bureaus: (none — no same-creditor tradelines at other bureaus)"
            ),
            body_style,
        ),
        Spacer(1, 4),
        bullet_list([f"[{d.kind}] {d.detail}" for d in cross_bureau.discrepancies]),
        section_heading(f"DISPUTE ROUNDS MAILED ({len(packet.letters)})"),
        bullet_list(
            [
                f"{letter.subject} [{letter.status}] to {letter.recipient_type}, "
                f"sent {_format_date(letter.sent_at)}"
                for letter in packet.letters
            ]
        ),
        section_heading(f"RECORDED RESPONSES ({len(packet.responses)})"),
        bullet_list(
            [
                f"{response.outcome} via {response.response_method} "
                f"on {_format_date(response.response_date)}"
                for response in packet.responses
            ]
        ),
    ]
    doc.build(story)
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
