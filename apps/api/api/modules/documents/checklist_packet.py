"""Build staff-mediated checklist exhibit ZIP packets."""

from __future__ import annotations

import re
import uuid
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.models import Case
from api.modules.documents.constants import DocumentType
from api.modules.documents.models import Document
from api.modules.documents.storage import DocumentStorage, async_get

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
_LETTER_STATUSES_INCLUDED = frozenset({"draft", "review", "approved", "sent"})


def checklist_packet_filename(kind: Literal["cfpb", "attorney"], case_id: uuid.UUID) -> str:
    short = str(case_id).replace("-", "")[:8]
    return f"{kind}-checklist-packet-{short}.zip"


def _safe_filename(name: str, *, document_id: uuid.UUID) -> str:
    cleaned = _SAFE_NAME.sub("_", name).strip("._") or "document"
    stem = Path(cleaned).stem[:80] or "document"
    suffix = Path(cleaned).suffix[:20]
    return f"{stem}__{document_id.hex[:8]}{suffix}"


def _extension_for(document: Document) -> str:
    name = document.file_name or ""
    suffix = Path(name).suffix
    if suffix:
        return suffix
    mime = (document.mime_type or "").lower()
    if mime == "application/pdf":
        return ".pdf"
    if mime in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if mime == "image/png":
        return ".png"
    return ".bin"


async def _load_document_bytes(
    storage: DocumentStorage,
    document: Document | None,
) -> bytes | None:
    if document is None or not document.storage_key:
        return None
    try:
        return await async_get(storage, document.storage_key)
    except Exception:
        return None


async def _get_document(
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


async def _resolve_typed_document(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case: Case,
    pointer_id: uuid.UUID | None,
    document_type: str,
) -> Document | None:
    if pointer_id is not None:
        document = await _get_document(
            session,
            organization_id=organization_id,
            case_id=case.id,
            document_id=pointer_id,
        )
        if document is not None:
            return document
    result = await session.execute(
        select(Document)
        .where(
            Document.organization_id == organization_id,
            Document.case_id == case.id,
            Document.deleted_at.is_(None),
            Document.document_type == document_type,
        )
        .order_by(Document.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _list_typed_documents(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    document_type: str,
) -> list[Document]:
    result = await session.execute(
        select(Document)
        .where(
            Document.organization_id == organization_id,
            Document.case_id == case_id,
            Document.deleted_at.is_(None),
            Document.document_type == document_type,
        )
        .order_by(Document.created_at.desc())
        .limit(50)
    )
    return list(result.scalars().all())


async def collect_checklist_exhibits(
    session: AsyncSession,
    storage: DocumentStorage,
    *,
    organization_id: uuid.UUID,
    case: Case,
) -> list[tuple[str, bytes]]:
    """Best-effort identity, POA, credit reports, and bureau responses."""
    exhibits: list[tuple[str, bytes]] = []

    identity = await _resolve_typed_document(
        session,
        organization_id=organization_id,
        case=case,
        pointer_id=case.identity_document_id,
        document_type=DocumentType.IDENTITY_DOCUMENT.value,
    )
    identity_bytes = await _load_document_bytes(storage, identity)
    if identity is not None and identity_bytes is not None:
        exhibits.append((f"exhibits/identity{_extension_for(identity)}", identity_bytes))

    proof = await _resolve_typed_document(
        session,
        organization_id=organization_id,
        case=case,
        pointer_id=case.proof_of_address_document_id,
        document_type=DocumentType.PROOF_OF_ADDRESS.value,
    )
    proof_bytes = await _load_document_bytes(storage, proof)
    if proof is not None and proof_bytes is not None:
        exhibits.append((f"exhibits/proof-of-address{_extension_for(proof)}", proof_bytes))

    for document in await _list_typed_documents(
        session,
        organization_id=organization_id,
        case_id=case.id,
        document_type=DocumentType.CREDIT_REPORT.value,
    ):
        content = await _load_document_bytes(storage, document)
        if content is None:
            continue
        name = _safe_filename(document.file_name or "credit-report", document_id=document.id)
        exhibits.append((f"exhibits/credit-reports/{name}", content))

    for document in await _list_typed_documents(
        session,
        organization_id=organization_id,
        case_id=case.id,
        document_type=DocumentType.BUREAU_RESPONSE.value,
    ):
        content = await _load_document_bytes(storage, document)
        if content is None:
            continue
        name = _safe_filename(document.file_name or "bureau-response", document_id=document.id)
        exhibits.append((f"exhibits/bureau-responses/{name}", content))

    return exhibits


def dispute_letter_exhibit_path(
    *,
    status: str,
    recipient_type: str,
    letter_id: uuid.UUID,
    letter_format: Literal["text", "pdf"] = "text",
) -> str:
    short = letter_id.hex[:8]
    status_slug = _SAFE_NAME.sub("_", status).strip("_") or "letter"
    recipient_slug = _SAFE_NAME.sub("_", recipient_type).strip("_") or "recipient"
    extension = "txt" if letter_format == "text" else "pdf"
    return f"exhibits/dispute-letters/{status_slug}_{recipient_slug}__{short}.{extension}"


async def collect_checklist_letter_exhibits(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    letter_format: Literal["text", "pdf"] = "text",
) -> list[tuple[str, bytes]]:
    """Best-effort dispute letter exports (text or PDF; no mail consent gate)."""
    from api.modules.accounts.dispute_letter_export import build_dispute_letter_export
    from api.modules.accounts.dispute_letter_models import DisputeLetter

    result = await session.execute(
        select(DisputeLetter)
        .where(
            DisputeLetter.organization_id == organization_id,
            DisputeLetter.case_id == case_id,
            DisputeLetter.deleted_at.is_(None),
        )
        .order_by(DisputeLetter.created_at.desc())
        .limit(50)
    )
    exhibits: list[tuple[str, bytes]] = []
    for letter in result.scalars().all():
        status_value = (
            letter.status.value if hasattr(letter.status, "value") else str(letter.status)
        )
        if status_value not in _LETTER_STATUSES_INCLUDED:
            continue
        content, _filename, _media = build_dispute_letter_export(letter, letter_format)
        path = dispute_letter_exhibit_path(
            status=status_value,
            recipient_type=letter.recipient_type,
            letter_id=letter.id,
            letter_format=letter_format,
        )
        exhibits.append((path, content))
    return exhibits


def mail_packet_exhibit_path(filename: str) -> str:
    cleaned = _SAFE_NAME.sub("_", filename).strip("._") or "mail-packet.pdf"
    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf"
    return f"exhibits/mail-packets/{cleaned}"


def report_excerpt_exhibit_path(filename: str) -> str:
    cleaned = _SAFE_NAME.sub("_", filename).strip("._") or "report-excerpt.pdf"
    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf"
    return f"exhibits/report-excerpts/{cleaned}"


def build_checklist_packet_zip(
    *,
    markdown_name: str,
    markdown_bytes: bytes,
    exhibits: list[tuple[str, bytes]],
    pdf_name: str | None = None,
    pdf_bytes: bytes | None = None,
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(markdown_name, markdown_bytes)
        if pdf_name and pdf_bytes is not None:
            archive.writestr(pdf_name, pdf_bytes)
        for path, content in exhibits:
            archive.writestr(path, content)
    return buffer.getvalue()
