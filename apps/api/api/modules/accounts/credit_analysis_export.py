"""Export of a persisted credit-analysis (Lending Readiness) run.

Renders an already-loaded :class:`CreditAnalysisRunResponse` into a human-readable
text or PDF document for operator review or partner handoff.  This is a pure
formatter — it performs no scoring, no I/O, and no network calls.

Guardrails:
- The ADVISORY_DISCLAIMER is reproduced prominently at the top of every export.
- No approval, guarantee, or underwriting language appears here or in callers.
- Exports are operator-gated; the platform never auto-transmits them.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Literal

from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_schemas import CreditAnalysisRunResponse

CreditAnalysisExportFormat = Literal["text", "pdf"]

_MEDIA_TYPES: dict[CreditAnalysisExportFormat, str] = {
    "text": "text/plain; charset=utf-8",
    "pdf": "application/pdf",
}


def export_media_type(export_format: CreditAnalysisExportFormat) -> str:
    return _MEDIA_TYPES[export_format]


def export_filename(
    run: CreditAnalysisRunResponse, export_format: CreditAnalysisExportFormat
) -> str:
    short_id = str(run.id).split("-", 1)[0]
    extension = "txt" if export_format == "text" else "pdf"
    return f"mortgage-readiness-{short_id}.{extension}"


def _format_date(value: object) -> str:
    if value is None:
        return "—"
    return str(value)


def _bullet_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- (none)"]
    return [f"- {item}" for item in items]


def _dimension_lines(dimensions: list[dict[str, Any]]) -> list[str]:
    lines = []
    for dim in dimensions:
        label = dim.get("label", dim.get("key", "?"))
        score = dim.get("score", "?")
        weight = dim.get("weight", 0)
        lines.append(f"- {label}: {score}/100 (weight {int(weight * 100)}%)")
    return lines or ["- (none)"]


def _blocker_lines(blockers: list[dict[str, Any]]) -> list[str]:
    lines = []
    for b in blockers:
        title = b.get("title", "?")
        impact = b.get("impact", "")
        action = b.get("action", "")
        lines.append(f"- {title}: {impact} → {action}")
    return lines or ["- (none)"]


def build_credit_analysis_text(run: CreditAnalysisRunResponse) -> str:
    """Render the run as a plain-text advisory readiness document."""
    payload = run.payload or {}
    disclaimer = payload.get("disclaimer") or ADVISORY_DISCLAIMER
    dimensions: list[dict[str, Any]] = payload.get("dimensions", [])
    blockers: list[dict[str, Any]] = payload.get("blockers", [])

    sections: list[str] = [
        "MORTGAGE READINESS REPORT",
        "Advisory readiness composite for partner handoff.",
        "",
        "DISCLAIMER",
        disclaimer,
        "",
        "READINESS SUMMARY",
        f"- Score: {run.mortgage_readiness_score}/100",
        f"- Band: {run.band}",
        f"- Reports evaluated: {run.reports_evaluated}",
        f"- Tradelines evaluated: {run.tradelines_evaluated}",
        f"- Formula version: {run.formula_version}",
        f"- Score version: {run.score_version}",
        f"- Generated at: {_format_date(run.generated_at)}",
        f"- Run ID: {run.id}",
        "",
        "DIMENSIONS",
        *_dimension_lines(dimensions),
        "",
        "BLOCKERS / PRIORITY ITEMS",
        *_blocker_lines(blockers),
    ]
    return "\n".join(sections).strip() + "\n"


def build_credit_analysis_pdf_bytes(run: CreditAnalysisRunResponse) -> bytes:
    """Render the run as a structured multi-section PDF for operator/partner review."""
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
        title="Mortgage Readiness Report",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MRTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a1a"),
    )
    subtitle_style = ParagraphStyle(
        "MRSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=13,
        spaceAfter=14,
        textColor=colors.HexColor("#444444"),
    )
    section_style = ParagraphStyle(
        "MRSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a1a"),
    )
    body_style = ParagraphStyle(
        "MRBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "MRBullet",
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
            .replace("™", "&trade;")
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

    dim_items = [
        f"{dim.get('label', dim.get('key', '?'))}: {dim.get('score', '?')}/100 "
        f"(weight {int(dim.get('weight', 0) * 100)}%)"
        for dim in dimensions
    ]
    blocker_items = [
        f"{b.get('title', '?')}: {b.get('impact', '')} → {b.get('action', '')}" for b in blockers
    ]

    story: list[object] = [
        Paragraph("MORTGAGE READINESS REPORT", title_style),
        Paragraph("Advisory readiness composite for partner handoff.", subtitle_style),
        section_heading("DISCLAIMER"),
        Paragraph(esc(disclaimer), body_style),
        Spacer(1, 6),
        section_heading("READINESS SUMMARY"),
        bullet_list(
            [
                f"Score: {run.mortgage_readiness_score}/100",
                f"Band: {run.band}",
                f"Reports evaluated: {run.reports_evaluated}",
                f"Tradelines evaluated: {run.tradelines_evaluated}",
                f"Formula version: {run.formula_version}",
                f"Score version: {run.score_version}",
                f"Generated at: {_format_date(run.generated_at)}",
                f"Run ID: {run.id}",
            ]
        ),
        section_heading("DIMENSIONS"),
        bullet_list(dim_items),
        section_heading("BLOCKERS / PRIORITY ITEMS"),
        bullet_list(blocker_items),
    ]
    doc.build(story)
    return buffer.getvalue()


def build_credit_analysis_export(
    run: CreditAnalysisRunResponse,
    export_format: CreditAnalysisExportFormat,
) -> tuple[bytes, str, str]:
    filename = export_filename(run, export_format)
    media_type = export_media_type(export_format)
    if export_format == "text":
        content = build_credit_analysis_text(run).encode("utf-8")
    else:
        content = build_credit_analysis_pdf_bytes(run)
    return content, filename, media_type


def sanitize_content_disposition_filename(filename: str) -> str:
    safe = re.sub(r"[^\w.\-]", "_", filename)
    return safe or "mortgage-readiness.txt"
