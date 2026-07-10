"""Unit tests for dispute mail packet attachment resolution and merging."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from api.modules.accounts.dispute_letter_mail_export import (
    build_mail_export,
    build_mail_export_context,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.dispute_mail_attachments import (
    MailPacketAttachment,
    ResolvedMailPacketAttachments,
    merge_mail_packet_pdf,
)
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    PaymentStatus,
)
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus


def _minimal_pdf() -> bytes:
    from io import BytesIO

    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    pdf.drawString(72, 720, "Attachment page")
    pdf.save()
    return buffer.getvalue()


def test_merge_mail_packet_pdf_appends_attachment_pages() -> None:
    base_pdf = _minimal_pdf()
    attachments = ResolvedMailPacketAttachments(
        identity=MailPacketAttachment(
            label="Government-issued photo ID",
            content=_minimal_pdf(),
            mime_type="application/pdf",
        ),
        proof_of_address=None,
        credit_report=None,
    )

    merged = merge_mail_packet_pdf(base_pdf, attachments)

    from io import BytesIO

    from pypdf import PdfReader

    reader = PdfReader(BytesIO(merged))
    assert len(reader.pages) == 2


def test_build_mail_packet_marks_attached_items_on_checklist() -> None:
    letter = DisputeLetter(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        recipient_type="credit_bureau",
        status=DisputeLetterStatus.DRAFT,
        template_id="cra-tradeline-investigation-v1",
        subject="Dispute",
        body="Body",
        disputed_items=["Balance is wrong"],
        requested_action="Delete",
        evidence_checklist=[],
        compliance_notes=[],
        generated_by="rules",
        generated_at=datetime.now(UTC),
        sent_at=None,
    )
    account = Account(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        bureau=AccountBureau.EXPERIAN,
        creditor_name="TEST CREDITOR",
        account_number_masked="****1234",
        account_type=AccountType.CREDIT_CARD,
        account_status=AccountStatus.OPEN,
        payment_status=PaymentStatus.CURRENT,
    )
    case = Case(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Test",
        client_name="Test Client",
        status=CaseStatus.ACTIVE,
        stage=CaseStage.DISPUTE_PREPARATION,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    context = build_mail_export_context(account=account, case=case, dispute_letter=letter)
    attachments = ResolvedMailPacketAttachments(
        identity=MailPacketAttachment(
            label="Government-issued photo ID",
            content=_minimal_pdf(),
            mime_type="application/pdf",
        ),
        proof_of_address=MailPacketAttachment(
            label="Proof of current mailing address",
            content=_minimal_pdf(),
            mime_type="application/pdf",
        ),
        credit_report=MailPacketAttachment(
            label="Experian credit report",
            content=_minimal_pdf(),
            mime_type="application/pdf",
        ),
    )

    content, _, media_type = build_mail_export(
        letter, context, "mail-packet", attachments=attachments
    )

    assert media_type == "application/pdf"
    assert content.startswith(b"%PDF")

    from io import BytesIO

    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content))
    assert len(reader.pages) >= 5
