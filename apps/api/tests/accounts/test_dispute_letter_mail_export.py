"""Unit tests for mail-ready dispute letter exports."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from api.modules.accounts.dispute_letter_mail_export import (
    build_mail_export,
    build_mail_export_context,
    build_mail_letter_body,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.dispute_mail_addresses import (
    bureau_dispute_address,
    normalize_consumer_address_lines,
)
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    PaymentStatus,
)
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus


def _sample_account() -> Account:
    return Account(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        bureau=AccountBureau.EXPERIAN,
        creditor_name="ACHIEVE PERSONAL LOANS",
        account_number_masked="****1081",
        account_type=AccountType.PERSONAL_LOAN,
        account_status=AccountStatus.CHARGE_OFF,
        payment_status=PaymentStatus.CHARGE_OFF,
    )


def _sample_case() -> Case:
    now = datetime.now(UTC)
    return Case(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Chris Personal",
        client_name="Chris Verdin",
        client_email="chris@example.com",
        status=CaseStatus.ACTIVE,
        stage=CaseStage.DISPUTE_PREPARATION,
        priority=CasePriority.MEDIUM,
        opened_at=now,
    )


def _sample_letter() -> DisputeLetter:
    return DisputeLetter(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        recipient_type="credit_bureau",
        status=DisputeLetterStatus.DRAFT,
        template_id="cra-tradeline-investigation-v1",
        subject="Dispute of ACHIEVE PERSONAL LOANS tradeline",
        body="Internal draft body",
        disputed_items=["Verify the reported balance of $18,764.00."],
        requested_action="Delete or correct unverifiable information.",
        evidence_checklist=["Government-issued ID"],
        compliance_notes=["Draft requires staff review before sending."],
        generated_by="rules",
        generated_at=datetime.now(UTC),
        sent_at=None,
    )


def test_build_mail_letter_body_includes_fcra_and_excludes_internal_sections() -> None:
    context = build_mail_export_context(
        account=_sample_account(),
        case=_sample_case(),
        dispute_letter=_sample_letter(),
        consumer_address_lines=["123 Main St", "Austin, TX 78701"],
    )
    body = build_mail_letter_body(context)

    assert "15 U.S.C. § 1681i" in body
    assert "ACHIEVE PERSONAL LOANS" in body
    assert "Chris Verdin" in body
    assert "Experian" in body
    assert "EVIDENCE CHECKLIST" not in body
    assert "COMPLIANCE NOTES" not in body
    assert context.disputed_items[0] in body


def test_build_mail_export_pdf_outputs() -> None:
    letter = _sample_letter()
    context = build_mail_export_context(
        account=_sample_account(),
        case=_sample_case(),
        dispute_letter=letter,
    )

    letter_content, letter_name, letter_type = build_mail_export(letter, context, "mail-letter")
    label_content, label_name, label_type = build_mail_export(letter, context, "mail-label")
    packet_content, packet_name, packet_type = build_mail_export(letter, context, "mail-packet")

    assert letter_name.startswith("dispute-mail-letter-")
    assert label_name.startswith("dispute-mail-label-")
    assert packet_name.startswith("mail-packet-achieve-personal-loans-")
    assert letter_type == "application/pdf"
    assert label_type == "application/pdf"
    assert packet_type == "application/pdf"
    assert letter_content.startswith(b"%PDF")
    assert label_content.startswith(b"%PDF")
    assert packet_content.startswith(b"%PDF")


def test_bureau_dispute_address_for_experian() -> None:
    address = bureau_dispute_address(AccountBureau.EXPERIAN)
    assert address.name == "Experian"
    assert "Allen, TX" in address.lines[-1]


def test_normalize_consumer_address_lines_splits_commas() -> None:
    lines = normalize_consumer_address_lines(["123 Main St, Austin, TX 78701"])
    assert lines == ["123 Main St", "Austin", "TX 78701"]
