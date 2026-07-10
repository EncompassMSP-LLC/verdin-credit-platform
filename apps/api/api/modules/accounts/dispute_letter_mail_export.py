"""Mail-ready dispute letter and label export helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from io import BytesIO
from typing import Literal

from reportlab.pdfgen.canvas import Canvas

from api.modules.accounts.dispute_letter_models import DisputeLetter
from api.modules.accounts.dispute_mail_addresses import (
    FCRA_CRA_CITATION,
    FCRA_FURNISHER_CITATION,
    MailingAddress,
    bureau_dispute_address,
    furnisher_dispute_address,
    has_placeholder_address,
    resolve_consumer_address,
    resolve_return_address,
)
from api.modules.accounts.dispute_mail_attachments import (
    ResolvedMailPacketAttachments,
    attachment_labels,
    merge_mail_packet_pdf,
)
from api.modules.accounts.models import Account
from api.modules.cases.models import Case

DisputeMailExportFormat = Literal["mail-letter", "mail-label", "mail-packet", "report-excerpt"]

_MEDIA_TYPES: dict[DisputeMailExportFormat, str] = {
    "mail-letter": "application/pdf",
    "mail-label": "application/pdf",
    "mail-packet": "application/pdf",
    "report-excerpt": "application/pdf",
}


@dataclass(frozen=True, slots=True)
class DisputeMailExportContext:
    letter_date: date
    consumer: MailingAddress
    return_address: MailingAddress
    recipient: MailingAddress
    account_creditor: str
    account_number_masked: str | None
    bureau_label: str
    recipient_type: str
    disputed_items: tuple[str, ...]
    requested_action: str


def build_mail_export_context(
    *,
    account: Account,
    case: Case,
    dispute_letter: DisputeLetter,
    consumer_address_lines: list[str] | None = None,
    organization_name: str | None = None,
) -> DisputeMailExportContext:
    if dispute_letter.recipient_type == "furnisher":
        recipient = furnisher_dispute_address(account)
    else:
        recipient = bureau_dispute_address(account.bureau)

    return DisputeMailExportContext(
        letter_date=datetime.now(UTC).date(),
        consumer=resolve_consumer_address(
            consumer_name=case.client_name,
            address_lines=consumer_address_lines,
        ),
        return_address=resolve_return_address(organization_name=organization_name),
        recipient=recipient,
        account_creditor=account.creditor_name,
        account_number_masked=account.account_number_masked,
        bureau_label=account.bureau.value.replace("_", " ").title(),
        recipient_type=dispute_letter.recipient_type,
        disputed_items=tuple(dispute_letter.disputed_items),
        requested_action=dispute_letter.requested_action,
    )


def build_mail_letter_body(context: DisputeMailExportContext) -> str:
    account_identifier = context.account_number_masked or "account number on file"
    dispute_lines = "\n".join(f"  • {item}" for item in context.disputed_items) or "  • (none)"
    date_label = context.letter_date.strftime("%B %d, %Y")

    if context.recipient_type == "furnisher":
        legal_basis = (
            f"Pursuant to {FCRA_FURNISHER_CITATION}, I dispute the accuracy and completeness "
            "of the information your company is furnishing to consumer reporting agencies."
        )
        closing = (
            "Please investigate these items, correct or delete any information that cannot be "
            "verified as complete and accurate, and notify all consumer reporting agencies to "
            "whom you furnish data."
        )
    else:
        legal_basis = (
            f"Pursuant to {FCRA_CRA_CITATION}, I dispute the accuracy and completeness of the "
            f"following information appearing on my {context.bureau_label} consumer report."
        )
        closing = (
            "Please conduct a reasonable reinvestigation of the disputed items, provide the "
            "method of verification, and delete or correct any information that cannot be "
            "verified as complete and accurate within 30 days of receipt."
        )

    return (
        f"{_format_address_block(context.consumer)}\n\n"
        f"{date_label}\n\n"
        f"{_format_address_block(context.recipient)}\n\n"
        f"RE: Dispute of {context.account_creditor} tradeline ({account_identifier})\n\n"
        f"To Whom It May Concern:\n\n"
        f"I, {context.consumer.name}, dispute inaccurate or incomplete credit reporting for the "
        f"tradeline furnished by {context.account_creditor} and reported to "
        f"{context.bureau_label}.\n\n"
        f"{legal_basis}\n\n"
        f"Disputed items:\n{dispute_lines}\n\n"
        f"{closing}\n\n"
        "Enclosures: copy of government-issued identification and proof of current mailing "
        "address; copy of the consumer report page showing the disputed tradeline.\n\n"
        "Sincerely,\n\n"
        f"{context.consumer.name}\n"
        f"{chr(10).join(context.consumer.lines)}\n\n"
        f"Return mail to:\n{_format_address_block(context.return_address)}"
    )


def assess_mail_readiness(context: DisputeMailExportContext) -> list[str]:
    warnings: list[str] = []
    if has_placeholder_address(context.consumer):
        warnings.append("Add the consumer mailing address from their government-issued ID.")
    if has_placeholder_address(context.return_address):
        warnings.append(
            "Configure DISPUTE_RETURN_ADDRESS_LINE1 (and LINE2/LINE3) for your return address."
        )
    if has_placeholder_address(context.recipient):
        warnings.append("Verify the bureau or furnisher mailing address before sending.")
    if not context.account_number_masked:
        warnings.append("Add a masked account number so the bureau can match the tradeline.")
    return warnings


def build_mailing_checklist_body(
    context: DisputeMailExportContext,
    *,
    attached_labels: tuple[str, ...] = (),
) -> str:
    warnings = assess_mail_readiness(context)
    warning_lines = (
        "\n".join(f"  ! {item}" for item in warnings)
        if warnings
        else "  All required mailing fields are populated."
    )
    attached = {label.lower() for label in attached_labels}
    id_status = (
        "  [x] Attach a copy of government-issued photo ID (included in this PDF)"
        if any("photo id" in label or "government-issued" in label for label in attached)
        else "  [ ] Attach a copy of government-issued photo ID"
    )
    report_status = (
        "  [x] Attach the credit report page showing this tradeline (included in this PDF; other tradelines redacted)"
        if any("tradeline page" in label or "credit report" in label for label in attached)
        else "  [ ] Attach the credit report page showing this tradeline"
    )
    address_status = (
        "  [x] Attach proof of current mailing address (included in this PDF)"
        if any("mailing address" in label or "proof of" in label for label in attached)
        else "  [ ] Attach proof of current mailing address"
    )
    return (
        f"MAILING CHECKLIST — {context.account_creditor.upper()} ({context.bureau_label})\n\n"
        "Before mailing:\n"
        "  [ ] Print and sign the dispute letter (previous page)\n"
        f"{id_status}\n"
        f"{address_status}\n"
        f"{report_status}\n"
        "  [ ] Affix the MAIL TO label and RETURN label from page 1\n"
        "  [ ] Send via USPS Certified Mail with Return Receipt Requested\n\n"
        f"Mail to:\n{_format_address_block(context.recipient)}\n\n"
        f"Return to:\n{_format_address_block(context.return_address)}\n\n"
        f"Consumer:\n{_format_address_block(context.consumer)}\n\n"
        "Readiness:\n"
        f"{warning_lines}"
    )


def export_mail_filename(
    dispute_letter: DisputeLetter,
    export_format: DisputeMailExportFormat,
    *,
    creditor_name: str | None = None,
) -> str:
    short_id = str(dispute_letter.id).split("-", 1)[0]
    if export_format == "mail-packet":
        slug = _slugify(creditor_name or "tradeline")
        return f"mail-packet-{slug}-{short_id}.pdf"
    suffix = "mail-letter" if export_format == "mail-letter" else "mail-label"
    return f"dispute-{suffix}-{short_id}.pdf"


def build_mail_export(
    dispute_letter: DisputeLetter,
    context: DisputeMailExportContext,
    export_format: DisputeMailExportFormat,
    *,
    attachments: ResolvedMailPacketAttachments | None = None,
) -> tuple[bytes, str, str]:
    filename = export_mail_filename(
        dispute_letter,
        export_format,
        creditor_name=context.account_creditor,
    )
    media_type = _MEDIA_TYPES[export_format]
    if export_format == "mail-letter":
        content = build_mail_letter_pdf(context)
    elif export_format == "mail-label":
        content = build_mail_label_pdf(context)
    else:
        content = build_mail_packet_pdf(context, attachments=attachments)
    return content, filename, media_type


def build_mail_packet_pdf(
    context: DisputeMailExportContext,
    *,
    attachments: ResolvedMailPacketAttachments | None = None,
) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    attached_labels = attachment_labels(attachments) if attachments is not None else ()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    _render_mail_label_page(pdf, context)
    pdf.showPage()
    _render_mail_letter_page(pdf, context)
    pdf.showPage()
    _render_checklist_page(pdf, context, attached_labels=attached_labels)
    pdf.save()
    base_pdf = buffer.getvalue()
    if attachments is None:
        return base_pdf
    return merge_mail_packet_pdf(base_pdf, attachments)


def build_mail_letter_pdf(context: DisputeMailExportContext) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    _render_mail_letter_page(pdf, context)
    pdf.save()
    return buffer.getvalue()


def build_mail_label_pdf(context: DisputeMailExportContext) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    _render_mail_label_page(pdf, context)
    pdf.save()
    return buffer.getvalue()


def _render_mail_letter_page(pdf: Canvas, context: DisputeMailExportContext) -> None:
    from reportlab.lib.pagesizes import letter as letter_page_size

    page_width, page_height = letter_page_size
    margin = 72
    line_height = 14
    y = page_height - margin

    def draw_wrapped(text: str, *, font_name: str = "Helvetica", font_size: int = 11) -> None:
        nonlocal y
        pdf.setFont(font_name, font_size)
        for line in _wrap_lines(text):
            if y < margin:
                pdf.showPage()
                y = page_height - margin
            if not line:
                y -= line_height
                continue
            pdf.drawString(margin, y, line)
            y -= line_height

    draw_wrapped(build_mail_letter_body(context))


def _render_checklist_page(
    pdf: Canvas,
    context: DisputeMailExportContext,
    *,
    attached_labels: tuple[str, ...] = (),
) -> None:
    from reportlab.lib.pagesizes import letter as letter_page_size

    page_width, page_height = letter_page_size
    margin = 72
    line_height = 14
    y = page_height - margin

    pdf.setFont("Helvetica", 11)
    for line in _wrap_lines(
        build_mailing_checklist_body(context, attached_labels=attached_labels),
        max_chars=95,
    ):
        if y < margin:
            break
        if not line:
            y -= line_height
            continue
        pdf.drawString(margin, y, line)
        y -= line_height


def _render_mail_label_page(pdf: Canvas, context: DisputeMailExportContext) -> None:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.lib.units import inch

    page_width, page_height = letter_page_size
    margin = 0.5 * inch
    label_height = 2.0 * inch
    label_width = (page_width - (2 * margin)) / 2 - (0.25 * inch)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, page_height - margin, "Dispute mailing packet — labels")

    _draw_label_box(
        pdf,
        title="MAIL TO",
        address=context.recipient,
        x=margin,
        y=page_height - margin - 0.35 * inch - label_height,
        width=label_width,
        height=label_height,
    )
    _draw_label_box(
        pdf,
        title="RETURN",
        address=context.return_address,
        x=margin + label_width + 0.5 * inch,
        y=page_height - margin - 0.35 * inch - label_height,
        width=label_width,
        height=label_height,
    )

    consumer_y = page_height - margin - 0.35 * inch - (label_height * 2) - 0.5 * inch
    _draw_label_box(
        pdf,
        title="CONSUMER",
        address=context.consumer,
        x=margin,
        y=consumer_y,
        width=page_width - (2 * margin),
        height=label_height,
    )

    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        margin,
        consumer_y - 0.3 * inch,
        f"Tradeline: {context.account_creditor} · Bureau: {context.bureau_label}",
    )


def _draw_label_box(
    pdf: Canvas,
    *,
    title: str,
    address: MailingAddress,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    pdf.setLineWidth(1)
    pdf.rect(x, y, width, height)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 8, y + height - 16, title)
    pdf.setFont("Helvetica", 11)
    line_y = y + height - 34
    for line in address.formatted_lines():
        pdf.drawString(x + 8, line_y, line[:70])
        line_y -= 14


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


def _format_address_block(address: MailingAddress) -> str:
    return "\n".join(address.formatted_lines())


def _slugify(value: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:40] or "tradeline"
