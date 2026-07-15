"""Plain-text export of the litigation-readiness evidence packet (Phase 12 slice 5).

Renders an already-assembled :class:`AccountLitigationPacket` into a human-readable
text document for a **licensed attorney to review**. This is a pure formatter — it
performs no assembly, no scoring, no I/O, and no network calls.

Guardrails: the export is a manual attorney handoff. The platform never files suit,
drafts pleadings, transmits the document anywhere, or contacts a court/bureau. The
packet's disclaimer is reproduced prominently at the top of every export.
"""

from __future__ import annotations

import re
from typing import Literal

from api.modules.accounts.schemas import (
    AccountLitigationPacket,
    LitigationPacketLetter,
    LitigationPacketResponse,
)

LitigationPacketExportFormat = Literal["text"]

_MEDIA_TYPES: dict[LitigationPacketExportFormat, str] = {
    "text": "text/plain; charset=utf-8",
}


def export_media_type(export_format: LitigationPacketExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def export_filename(
    packet: AccountLitigationPacket, export_format: LitigationPacketExportFormat
) -> str:
    short_id = str(packet.account_id).split("-", 1)[0]
    extension = "txt"
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


def build_litigation_packet_export(
    packet: AccountLitigationPacket,
    export_format: LitigationPacketExportFormat,
) -> tuple[bytes, str, str]:
    filename = export_filename(packet, export_format)
    media_type = export_media_type(export_format)
    content = build_litigation_packet_text(packet).encode("utf-8")
    return content, filename, media_type


def sanitize_content_disposition_filename(filename: str) -> str:
    safe = re.sub(r"[^\w.\-]", "_", filename)
    return safe or "litigation-packet.txt"
