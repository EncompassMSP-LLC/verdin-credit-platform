"""FCRA §605B identity-theft block packet export (staff-mediated).

Produces bureau block-request letters and a readiness manifest. This is not live
bureau submission — operators mail or upload packets after review.
"""

from __future__ import annotations

import re
import uuid
import zipfile
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from typing import Any, Literal

from api.modules.accounts.dispute_mail_addresses import (
    MailingAddress,
    bureau_dispute_address,
    resolve_consumer_address,
    resolve_return_address,
)
from api.modules.accounts.models import AccountBureau

FCRA_605B_CITATION = "15 U.S.C. § 1681c-2 (FCRA Section 605B)"

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")

LetterFormat = Literal["text", "pdf"]


@dataclass(frozen=True, slots=True)
class BlockTradeline:
    creditor_name: str
    account_number_masked: str | None
    match_key: str | None
    bureau: str | None
    review_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class Fcra605bBlockLetterContext:
    letter_date: date
    consumer_name: str
    consumer_address_lines: tuple[str, ...]
    return_address: MailingAddress
    recipient: MailingAddress
    bureau_label: str
    tradelines: tuple[BlockTradeline, ...]
    attestation_recorded: bool
    packet_readiness: int | None
    missing_evidence: tuple[str, ...]


def fcra_605b_packet_filename(case_id: uuid.UUID) -> str:
    short = str(case_id).replace("-", "")[:8]
    return f"fcra-605b-block-packet-{short}.zip"


def _slugify(value: str) -> str:
    cleaned = _SAFE_NAME.sub("_", value).strip("._") or "item"
    return cleaned[:60]


def parse_bureau(value: str | None) -> AccountBureau | None:
    if not value:
        return None
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "experian": AccountBureau.EXPERIAN,
        "equifax": AccountBureau.EQUIFAX,
        "transunion": AccountBureau.TRANSUNION,
        "trans_union": AccountBureau.TRANSUNION,
    }
    if normalized in aliases:
        return aliases[normalized]
    try:
        return AccountBureau(normalized)
    except ValueError:
        return None


def build_block_letter_context(
    *,
    letter_date: date,
    consumer_name: str,
    consumer_address_lines: list[str] | None,
    organization_name: str | None,
    bureau: str | None,
    tradelines: list[BlockTradeline],
    attestation_recorded: bool,
    packet_readiness: int | None,
    missing_evidence: list[str],
) -> Fcra605bBlockLetterContext:
    bureau_enum = parse_bureau(bureau)
    if bureau_enum is not None:
        recipient = bureau_dispute_address(bureau_enum)
        bureau_label = bureau_enum.value.replace("_", " ").title()
    else:
        label = (bureau or "credit bureau").replace("_", " ").title()
        recipient = MailingAddress(
            name=f"{label} — Identity Theft Block Requests",
            lines=("[Verify current CRA identity-theft / block mailing address before sending]",),
        )
        bureau_label = label
    consumer = resolve_consumer_address(
        consumer_name=consumer_name,
        address_lines=consumer_address_lines,
    )
    return Fcra605bBlockLetterContext(
        letter_date=letter_date,
        consumer_name=consumer.name,
        consumer_address_lines=tuple(consumer.lines),
        return_address=resolve_return_address(organization_name=organization_name),
        recipient=recipient,
        bureau_label=bureau_label,
        tradelines=tuple(tradelines),
        attestation_recorded=attestation_recorded,
        packet_readiness=packet_readiness,
        missing_evidence=tuple(missing_evidence),
    )


def _format_address_block(name: str, lines: tuple[str, ...]) -> str:
    return "\n".join([name, *lines])


def build_605b_block_letter_body(context: Fcra605bBlockLetterContext) -> str:
    date_label = context.letter_date.strftime("%B %d, %Y")
    tradeline_lines = []
    for item in context.tradelines:
        account = item.account_number_masked or "account number on file"
        tradeline_lines.append(f"  • {item.creditor_name} ({account})")
    if not tradeline_lines:
        tradeline_lines.append("  • (none listed)")
    attestation_note = (
        "I previously attested that I did not open or authorize the identified accounts "
        "and that the information results from identity theft."
        if context.attestation_recorded
        else "Consumer attestation must be recorded before mailing this request."
    )
    missing = (
        "\n".join(f"  • {item}" for item in context.missing_evidence)
        if context.missing_evidence
        else "  • (none flagged by readiness checklist)"
    )
    readiness = (
        f"{context.packet_readiness}%" if context.packet_readiness is not None else "not assessed"
    )
    return (
        f"{_format_address_block(context.consumer_name, context.consumer_address_lines)}\n\n"
        f"{date_label}\n\n"
        f"{_format_address_block(context.recipient.name, context.recipient.lines)}\n\n"
        f"RE: FCRA §605B identity-theft block request — {context.bureau_label}\n\n"
        f"To Whom It May Concern:\n\n"
        f"I, {context.consumer_name}, request that {context.bureau_label} block the following "
        f"information pursuant to {FCRA_605B_CITATION} because it results from alleged "
        f"identity theft and does not relate to any transaction by me.\n\n"
        f"{attestation_note}\n\n"
        f"Information to block:\n"
        f"{chr(10).join(tradeline_lines)}\n\n"
        "Please block the identified information within four business days of receiving "
        "the materials required by §605B, notify me of the block, and provide the "
        "furnisher with a copy of my identity-theft report and related materials as "
        "required by law.\n\n"
        "This request is an identity-theft block under §605B. It is not an ordinary "
        "FCRA §611 accuracy dispute.\n\n"
        f"Packet readiness (internal): {readiness}\n"
        f"Evidence still needed (internal checklist):\n{missing}\n\n"
        "Enclosures (when available): proof of identity; Identity Theft Report; "
        "consumer statement / attestation; proof of address; credit-report pages showing "
        "the fraudulent information.\n\n"
        "Sincerely,\n\n"
        f"{context.consumer_name}\n"
        f"{chr(10).join(context.consumer_address_lines)}\n\n"
        f"Return mail to:\n"
        f"{_format_address_block(context.return_address.name, context.return_address.lines)}\n"
    )


def build_605b_block_letter_pdf(context: Fcra605bBlockLetterContext) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    page_width, page_height = letter_page_size
    margin = 72
    line_height = 14
    y = page_height - margin
    max_width = page_width - (2 * margin)

    def new_page() -> None:
        nonlocal y
        pdf.showPage()
        y = page_height - margin

    def draw_wrapped(text: str, *, font_name: str = "Helvetica", font_size: int = 11) -> None:
        nonlocal y
        pdf.setFont(font_name, font_size)
        for raw_line in text.splitlines():
            if not raw_line:
                y -= line_height
                if y < margin:
                    new_page()
                    pdf.setFont(font_name, font_size)
                continue
            words = raw_line.split(" ")
            current = ""
            for word in words:
                candidate = f"{current} {word}".strip()
                if pdf.stringWidth(candidate, font_name, font_size) <= max_width:
                    current = candidate
                    continue
                if y < margin:
                    new_page()
                    pdf.setFont(font_name, font_size)
                pdf.drawString(margin, y, current)
                y -= line_height
                current = word
            if current:
                if y < margin:
                    new_page()
                    pdf.setFont(font_name, font_size)
                pdf.drawString(margin, y, current)
                y -= line_height

    draw_wrapped(build_605b_block_letter_body(context))
    pdf.save()
    return buffer.getvalue()


def build_605b_packet_manifest(
    *,
    case_id: uuid.UUID,
    consumer_name: str,
    confirmed_count: int,
    bureau_labels: list[str],
    packet_readiness: int | None,
    missing_evidence: list[str],
    evidence_checklist: list[dict[str, Any]],
) -> str:
    readiness = f"{packet_readiness}%" if packet_readiness is not None else "not assessed"
    bureaus = ", ".join(bureau_labels) if bureau_labels else "(none)"
    missing_lines = (
        "\n".join(f"- {item}" for item in missing_evidence) if missing_evidence else "- (none)"
    )
    checklist_lines = []
    for item in evidence_checklist:
        item_id = str(item.get("item_id") or item.get("id") or "item")
        label = str(item.get("label") or item_id)
        status_value = str(item.get("status") or "unknown")
        checklist_lines.append(f"- [{status_value}] {label} (`{item_id}`)")
    if not checklist_lines:
        checklist_lines.append("- (no incident checklist)")
    return (
        f"# FCRA §605B identity-theft block packet\n\n"
        f"- Case ID: `{case_id}`\n"
        f"- Consumer: {consumer_name}\n"
        f"- Confirmed fraudulent tradelines: {confirmed_count}\n"
        f"- Bureaus in this packet: {bureaus}\n"
        f"- Packet readiness: {readiness}\n"
        f"- Legal citation: {FCRA_605B_CITATION}\n\n"
        "## Operator notice\n\n"
        "This ZIP is a **staff-mediated preparation packet**. It does **not** submit "
        "anything to the credit bureaus. Live unsupervised §605B filing remains deferred.\n\n"
        "Ordinary FCRA §611 dispute letters must not be used for consumer-confirmed "
        "identity-theft claims.\n\n"
        "## Missing evidence (required items)\n\n"
        f"{missing_lines}\n\n"
        "## Evidence checklist\n\n"
        f"{chr(10).join(checklist_lines)}\n\n"
        "## Packet contents\n\n"
        "- `README.md` — this manifest\n"
        "- `letters/` — per-bureau §605B block request letters\n"
    )


def build_605b_packet_zip(
    *,
    manifest_markdown: str,
    letter_files: list[tuple[str, bytes]],
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.md", manifest_markdown.encode("utf-8"))
        for path, content in letter_files:
            archive.writestr(path, content)
    return buffer.getvalue()


def letter_exhibit_path(
    *,
    bureau_label: str,
    letter_format: LetterFormat,
) -> str:
    extension = "txt" if letter_format == "text" else "pdf"
    return f"letters/605b-block-{_slugify(bureau_label)}.{extension}"


def export_block_letter(
    context: Fcra605bBlockLetterContext,
    letter_format: LetterFormat,
) -> tuple[bytes, str]:
    path = letter_exhibit_path(
        bureau_label=context.bureau_label,
        letter_format=letter_format,
    )
    if letter_format == "pdf":
        return build_605b_block_letter_pdf(context), path
    return build_605b_block_letter_body(context).encode("utf-8"), path
