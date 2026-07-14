"""Resolve and merge supporting documents into dispute mail packets."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

from sqlalchemy import select

from api.modules.accounts.models import Account, AccountBureau
from api.modules.documents.constants import DocumentType
from api.modules.documents.models import Document
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.documents.storage import DocumentStorage, async_get

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from api.modules.cases.models import Case

_IMAGE_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/tiff"})
_PDF_MIME_TYPE = "application/pdf"


def resolve_known_tradeline_pages(
    *,
    page_map_raw: object,
    file_hash: str,
    creditor_name: str,
    account_number_masked: str | None,
    pdf_bytes: bytes,
) -> tuple[tuple[int, ...] | None, dict[str, object] | None]:
    """Resolve page numbers from cache or locate+write-through on miss.

    Returns ``(known_page_numbers, updated_page_map)``. ``updated_page_map`` is
    set only when a cache miss was located and should be persisted.
    """
    from api.modules.accounts.dispute_report_redaction import locate_tradeline_pages
    from api.modules.documents.tradeline_page_map import (
        CACHE_MISS,
        get_cached_pages,
        merge_page_map_entry,
        normalize_page_map,
    )

    page_map = normalize_page_map(page_map_raw, file_hash=file_hash)
    cached = get_cached_pages(
        page_map,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
    )
    if cached is not CACHE_MISS and isinstance(cached, tuple):
        return cached, None

    located = locate_tradeline_pages(
        pdf_bytes,
        target_creditor=creditor_name,
        target_account_masked=account_number_masked,
    )
    if located is None:
        return None, None

    updated = merge_page_map_entry(
        page_map,
        file_hash=file_hash,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
        pages=located,
    )
    return located, updated


@dataclass(frozen=True, slots=True)
class MailPacketAttachment:
    label: str
    content: bytes
    mime_type: str


@dataclass(frozen=True, slots=True)
class ResolvedMailPacketAttachments:
    identity: MailPacketAttachment | None
    proof_of_address: MailPacketAttachment | None
    credit_report: MailPacketAttachment | None


async def resolve_mail_packet_attachments(
    session: AsyncSession,
    storage: DocumentStorage,
    *,
    organization_id: uuid.UUID,
    case: Case,
    account: Account,
) -> ResolvedMailPacketAttachments:
    bureau_label = account.bureau.value.replace("_", " ").title()
    identity_document = await _resolve_identity_document(
        session,
        organization_id=organization_id,
        case=case,
    )
    proof_of_address_document = await _resolve_proof_of_address_document(
        session,
        organization_id=organization_id,
        case=case,
    )
    credit_report_document = await _resolve_credit_report_document(
        session,
        organization_id=organization_id,
        case_id=case.id,
        bureau=account.bureau,
    )

    identity = await _load_attachment(
        storage, identity_document, label="Government-issued photo ID"
    )
    proof_of_address = await _load_attachment(
        storage,
        proof_of_address_document,
        label="Proof of current mailing address",
    )
    credit_report = await _load_credit_report_attachment(
        session,
        storage,
        credit_report_document,
        account=account,
        bureau_label=bureau_label,
    )
    return ResolvedMailPacketAttachments(
        identity=identity,
        proof_of_address=proof_of_address,
        credit_report=credit_report,
    )


async def _resolve_identity_document(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case: Case,
) -> Document | None:
    candidate_ids: list[uuid.UUID] = []
    if case.identity_document_id is not None:
        candidate_ids.append(case.identity_document_id)
    if case.client_id is not None:
        from api.modules.clients.models import Client

        client = await session.get(Client, case.client_id)
        if client is not None and client.identity_document_id is not None:
            if client.identity_document_id not in candidate_ids:
                candidate_ids.append(client.identity_document_id)

    for document_id in candidate_ids:
        document = await _get_case_document(
            session,
            organization_id=organization_id,
            case_id=case.id,
            document_id=document_id,
        )
        if document is not None:
            return document

    result = await session.execute(
        select(Document)
        .where(
            Document.organization_id == organization_id,
            Document.case_id == case.id,
            Document.deleted_at.is_(None),
            Document.document_type == DocumentType.IDENTITY_DOCUMENT.value,
        )
        .order_by(Document.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _resolve_proof_of_address_document(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case: Case,
) -> Document | None:
    candidate_ids: list[uuid.UUID] = []
    if case.proof_of_address_document_id is not None:
        candidate_ids.append(case.proof_of_address_document_id)
    if case.client_id is not None:
        from api.modules.clients.models import Client

        client = await session.get(Client, case.client_id)
        if client is not None and client.proof_of_address_document_id is not None:
            if client.proof_of_address_document_id not in candidate_ids:
                candidate_ids.append(client.proof_of_address_document_id)

    for document_id in candidate_ids:
        document = await _get_case_document(
            session,
            organization_id=organization_id,
            case_id=case.id,
            document_id=document_id,
        )
        if document is not None:
            return document

    result = await session.execute(
        select(Document)
        .where(
            Document.organization_id == organization_id,
            Document.case_id == case.id,
            Document.deleted_at.is_(None),
            Document.document_type == DocumentType.PROOF_OF_ADDRESS.value,
        )
        .order_by(Document.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _resolve_credit_report_document(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    bureau: AccountBureau,
) -> Document | None:
    bureau_value = bureau.value

    parsed_result = await session.execute(
        select(Document)
        .join(DocumentParsedCreditReport, DocumentParsedCreditReport.document_id == Document.id)
        .where(
            DocumentParsedCreditReport.organization_id == organization_id,
            DocumentParsedCreditReport.bureau == bureau_value,
            Document.case_id == case_id,
            Document.deleted_at.is_(None),
        )
        .order_by(DocumentParsedCreditReport.parsed_at.desc())
        .limit(1)
    )
    parsed_match = parsed_result.scalar_one_or_none()
    if parsed_match is not None:
        return parsed_match

    typed_result = await session.execute(
        select(Document)
        .where(
            Document.organization_id == organization_id,
            Document.case_id == case_id,
            Document.deleted_at.is_(None),
            Document.document_type == DocumentType.CREDIT_REPORT.value,
        )
        .order_by(Document.created_at.desc())
    )
    typed_documents = list(typed_result.scalars())
    for document in typed_documents:
        haystack = f"{document.title} {document.file_name}".lower()
        if bureau_value in haystack:
            return document

    return typed_documents[0] if typed_documents else None


async def _get_case_document(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Document | None:
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == organization_id,
            Document.case_id == case_id,
            Document.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _load_credit_report_attachment(
    session: AsyncSession,
    storage: DocumentStorage,
    document: Document | None,
    *,
    account: Account,
    bureau_label: str,
) -> MailPacketAttachment | None:
    if document is None:
        return None

        from api.modules.accounts.dispute_report_redaction import (
            build_redacted_tradeline_excerpt,
            parsed_creditor_names,
        )

    content = await async_get(storage, document.storage_key)
    mime_type = document.mime_type or "application/octet-stream"
    if mime_type != _PDF_MIME_TYPE and not content.startswith(b"%PDF"):
        return MailPacketAttachment(
            label=f"{bureau_label} credit report",
            content=content,
            mime_type=mime_type,
        )

    parsed_result = await session.execute(
        select(DocumentParsedCreditReport).where(
            DocumentParsedCreditReport.document_id == document.id,
            DocumentParsedCreditReport.organization_id == document.organization_id,
        )
    )
    parsed_report_row = parsed_result.scalar_one_or_none()
    parsed_report = parsed_report_row.parsed_report if parsed_report_row is not None else None
    creditor_names = parsed_creditor_names(parsed_report)
    known_page_numbers: tuple[int, ...] | None = None
    if parsed_report_row is not None:
        known_page_numbers, updated_page_map = resolve_known_tradeline_pages(
            page_map_raw=parsed_report_row.tradeline_page_map,
            file_hash=document.file_hash,
            creditor_name=account.creditor_name,
            account_number_masked=account.account_number_masked,
            pdf_bytes=content,
        )
        if updated_page_map is not None:
            parsed_report_row.tradeline_page_map = updated_page_map
            await session.flush()
    excerpt = build_redacted_tradeline_excerpt(
        content,
        target_creditor=account.creditor_name,
        target_account_masked=account.account_number_masked,
        other_creditors=creditor_names,
        known_page_numbers=known_page_numbers,
    )
    if excerpt is None:
        return MailPacketAttachment(
            label=f"{bureau_label} credit report",
            content=content,
            mime_type="application/pdf",
        )

    if excerpt.used_full_report_fallback:
        label = f"{bureau_label} credit report"
    else:
        pages = ", ".join(str(page) for page in excerpt.page_numbers)
        label = f"{bureau_label} tradeline page ({pages})"

    return MailPacketAttachment(
        label=label,
        content=excerpt.pdf_bytes,
        mime_type="application/pdf",
    )


async def build_account_report_excerpt(
    session: AsyncSession,
    storage: DocumentStorage,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    account: Account,
) -> tuple[bytes, str] | None:
    document = await _resolve_credit_report_document(
        session,
        organization_id=organization_id,
        case_id=case_id,
        bureau=account.bureau,
    )
    attachment = await _load_credit_report_attachment(
        session,
        storage,
        document,
        account=account,
        bureau_label=account.bureau.value.replace("_", " ").title(),
    )
    if attachment is None:
        return None

    short_creditor = re.sub(r"[^a-z0-9]+", "-", account.creditor_name.lower()).strip("-")[:40]
    filename = f"report-excerpt-{short_creditor or 'tradeline'}.pdf"
    return attachment.content, filename


async def _load_attachment(
    storage: DocumentStorage,
    document: Document | None,
    *,
    label: str,
) -> MailPacketAttachment | None:
    if document is None:
        return None

    content = await async_get(storage, document.storage_key)
    mime_type = document.mime_type or "application/octet-stream"
    return MailPacketAttachment(label=label, content=content, mime_type=mime_type)


def merge_mail_packet_pdf(
    base_pdf: bytes,
    attachments: ResolvedMailPacketAttachments,
) -> bytes:
    attachment_pdfs: list[bytes] = []
    for attachment in (
        attachments.identity,
        attachments.proof_of_address,
        attachments.credit_report,
    ):
        if attachment is None:
            continue
        pdf_bytes = _attachment_to_pdf(attachment)
        if pdf_bytes is not None:
            attachment_pdfs.append(pdf_bytes)

    if not attachment_pdfs:
        return base_pdf

    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for pdf_bytes in (base_pdf, *attachment_pdfs):
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def attachment_labels(attachments: ResolvedMailPacketAttachments) -> tuple[str, ...]:
    labels: list[str] = []
    if attachments.identity is not None:
        labels.append(attachments.identity.label)
    if attachments.proof_of_address is not None:
        labels.append(attachments.proof_of_address.label)
    if attachments.credit_report is not None:
        labels.append(attachments.credit_report.label)
    return tuple(labels)


def _attachment_to_pdf(attachment: MailPacketAttachment) -> bytes | None:
    mime_type = attachment.mime_type.lower()
    if mime_type == _PDF_MIME_TYPE or attachment.content.startswith(b"%PDF"):
        return attachment.content
    if mime_type in _IMAGE_MIME_TYPES:
        return _image_bytes_to_pdf(attachment.content)
    return None


def _image_bytes_to_pdf(data: bytes) -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    image = ImageReader(BytesIO(data))
    image_width, image_height = image.getSize()
    page_width, page_height = letter_page_size
    margin = 36
    max_width = page_width - (2 * margin)
    max_height = page_height - (2 * margin)
    scale = min(max_width / image_width, max_height / image_height, 1.0)
    width = image_width * scale
    height = image_height * scale
    x = (page_width - width) / 2
    y = (page_height - height) / 2
    pdf.drawImage(image, x, y, width=width, height=height, preserveAspectRatio=True)
    pdf.save()
    return buffer.getvalue()
