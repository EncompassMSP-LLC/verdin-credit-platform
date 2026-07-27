"""Borrower-facing readiness report export (band-first; LRP-106).

Omits numeric overall scores from borrower downloads (FOUNDER-REVIEW P0-1).
Disclaimer leads every export. Never auto-transmitted.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Literal

from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_schemas import CreditAnalysisRunResponse

PortalReadinessExportFormat = Literal["text", "pdf"]

_MEDIA_TYPES: dict[PortalReadinessExportFormat, str] = {
    "text": "text/plain; charset=utf-8",
    "pdf": "application/pdf",
}

_BAND_LABELS = {
    "building": "Building",
    "progressing": "Progressing",
    "near_ready": "Near Ready",
    "lending_ready": "Lending Ready",
}


def portal_export_media_type(export_format: PortalReadinessExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def portal_export_filename(
    run: CreditAnalysisRunResponse, export_format: PortalReadinessExportFormat
) -> str:
    short_id = str(run.id).split("-", 1)[0]
    extension = "txt" if export_format == "text" else "pdf"
    return f"lending-readiness-report-{short_id}.{extension}"


def _qualitative_status(score: object) -> str:
    if isinstance(score, bool):
        return "Review with advisor"
    if not isinstance(score, int | float | str):
        return "Review with advisor"
    try:
        value = int(score)
    except (TypeError, ValueError):
        return "Review with advisor"
    if value >= 70:
        return "On track"
    if value >= 40:
        return "Needs attention"
    return "Priority"


def _band_label(band: str) -> str:
    return _BAND_LABELS.get(band, band.replace("_", " ").title())


def build_portal_readiness_text(run: CreditAnalysisRunResponse) -> str:
    payload = run.payload or {}
    disclaimer = payload.get("disclaimer") or ADVISORY_DISCLAIMER
    dimensions: list[dict[str, Any]] = payload.get("dimensions", [])
    blockers: list[dict[str, Any]] = payload.get("blockers", [])

    dim_lines = [
        f"- {d.get('label', d.get('key', '?'))}: {_qualitative_status(d.get('score'))}"
        for d in dimensions
    ] or ["- (none)"]
    blocker_lines = [
        f"- {b.get('title', '?')}: {b.get('impact', '')} → {b.get('action', '')}" for b in blockers
    ] or ["- (none)"]

    sections = [
        "LENDING READINESS REPORT",
        "Borrower advisory summary — not a FICO score or loan decision.",
        "",
        "DISCLAIMER",
        disclaimer,
        "",
        "READINESS BAND",
        f"- Band: {_band_label(run.band)}",
        f"- Generated at: {run.generated_at}",
        f"- Reports evaluated: {run.reports_evaluated}",
        f"- Tradelines evaluated: {run.tradelines_evaluated}",
        "",
        "WHAT DRIVES THIS BAND",
        *dim_lines,
        "",
        "CURRENT BLOCKERS",
        *blocker_lines,
        "",
        "Next steps live in your portal Tasks / action plan.",
    ]
    return "\n".join(sections).strip() + "\n"


def build_portal_readiness_pdf_bytes(run: CreditAnalysisRunResponse) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    payload = run.payload or {}
    disclaimer = payload.get("disclaimer") or ADVISORY_DISCLAIMER
    dimensions: list[dict[str, Any]] = payload.get("dimensions", [])
    blockers: list[dict[str, Any]] = payload.get("blockers", [])

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter_page_size,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Lending Readiness Report",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PortalRRTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "PortalRRBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    section_style = ParagraphStyle(
        "PortalRRSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=14,
        spaceAfter=8,
    )

    story: list[Any] = [
        Paragraph("Lending Readiness Report", title_style),
        Paragraph(
            "Borrower advisory summary — not a FICO score or loan decision.",
            body_style,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Disclaimer", section_style),
        Paragraph(disclaimer.replace("\n", "<br/>"), body_style),
        Paragraph("Readiness band", section_style),
        Paragraph(f"<b>{_band_label(run.band)}</b>", body_style),
        Paragraph(f"Generated at: {run.generated_at}", body_style),
        Paragraph("What drives this band", section_style),
    ]
    dim_items = [
        ListItem(
            Paragraph(
                f"{d.get('label', d.get('key', '?'))}: {_qualitative_status(d.get('score'))}",
                body_style,
            )
        )
        for d in dimensions
    ] or [ListItem(Paragraph("(none)", body_style))]
    story.append(ListFlowable(dim_items, bulletType="bullet", start="•"))
    story.append(Paragraph("Current blockers", section_style))
    blocker_items = [
        ListItem(
            Paragraph(
                f"{b.get('title', '?')}: {b.get('impact', '')} → {b.get('action', '')}",
                body_style,
            )
        )
        for b in blockers
    ] or [ListItem(Paragraph("(none)", body_style))]
    story.append(ListFlowable(blocker_items, bulletType="bullet", start="•"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "Next steps live in your portal Tasks / action plan.",
            ParagraphStyle(
                "PortalRRFoot",
                parent=body_style,
                textColor=colors.HexColor("#444444"),
                fontName="Helvetica-Oblique",
            ),
        )
    )
    doc.build(story)
    return buffer.getvalue()


def build_portal_readiness_export(
    run: CreditAnalysisRunResponse,
    export_format: PortalReadinessExportFormat,
) -> tuple[bytes, str, str]:
    if export_format == "pdf":
        content = build_portal_readiness_pdf_bytes(run)
    else:
        content = build_portal_readiness_text(run).encode("utf-8")
    return (
        content,
        portal_export_media_type(export_format),
        portal_export_filename(run, export_format),
    )
