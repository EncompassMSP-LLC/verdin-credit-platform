"""Unit tests for dispute letter export helpers."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from api.modules.accounts.dispute_letter_export import (
    build_dispute_letter_export,
    build_dispute_letter_plain_text,
    export_filename,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus


def _sample_letter() -> DisputeLetter:
    letter_id = uuid.uuid4()
    return DisputeLetter(
        id=letter_id,
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        recipient_type="credit_bureau",
        status=DisputeLetterStatus.DRAFT,
        template_id="cra-tradeline-investigation-v1",
        subject="Dispute of inaccurate tradeline reporting",
        body="Please investigate the reporting for Example Bank account ending in 1234.",
        disputed_items=["Balance reported inaccurately"],
        requested_action="Delete or correct the tradeline within 30 days.",
        evidence_checklist=["Government-issued ID"],
        compliance_notes=["FCRA Section 611 applies."],
        generated_by="rules",
        generated_at=datetime.now(UTC),
        sent_at=None,
    )


def test_build_dispute_letter_plain_text_includes_sections() -> None:
    letter = _sample_letter()
    text = build_dispute_letter_plain_text(letter)

    assert letter.subject in text
    assert letter.body in text
    assert "DISPUTED ITEMS" in text
    assert letter.disputed_items[0] in text
    assert "COMPLIANCE NOTES" in text
    assert letter.compliance_notes[0] in text


def test_export_filename_uses_short_id() -> None:
    letter = _sample_letter()
    assert export_filename(letter, "text") == f"dispute-letter-{letter.id.hex[:8]}.txt"
    assert export_filename(letter, "pdf") == f"dispute-letter-{letter.id.hex[:8]}.pdf"


def test_build_dispute_letter_pdf_starts_with_pdf_header() -> None:
    letter = _sample_letter()
    content, filename, media_type = build_dispute_letter_export(letter, "pdf")

    assert filename.endswith(".pdf")
    assert media_type == "application/pdf"
    assert content.startswith(b"%PDF")
