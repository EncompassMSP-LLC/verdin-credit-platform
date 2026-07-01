"""Unit tests for rule-based dispute draft generation."""

import uuid
from decimal import Decimal

from api.modules.accounts.dispute_drafts import (
    build_dispute_reason_suggestions,
    build_evidence_checklist,
    build_furnisher_dispute_body,
    detect_missing_evidence,
)
from api.modules.accounts.models import Account, AccountBureau, AccountStatus, PaymentStatus
from api.modules.cases.models import Case


def _account(**overrides: object) -> Account:
    account = Account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        creditor_name="Example Bank",
        bureau=AccountBureau.EQUIFAX,
        account_status=AccountStatus.OPEN,
        payment_status=PaymentStatus.CURRENT,
    )
    for field, value in overrides.items():
        setattr(account, field, value)
    return account


def test_build_dispute_reason_suggestions_includes_payment_and_balance() -> None:
    account = _account(
        payment_status=PaymentStatus.LATE_60,
        balance=Decimal("1500.00"),
        past_due_amount=Decimal("300.00"),
    )

    suggestions = build_dispute_reason_suggestions(account)
    codes = {item.code for item in suggestions}

    assert codes == {"payment_history", "balance"}
    payment = next(item for item in suggestions if item.code == "payment_history")
    assert payment.severity == "high"
    assert payment.category == "accuracy"
    assert "payment history" in payment.description.lower()
    assert payment.requires_evidence


def test_build_dispute_reason_suggestions_fallback() -> None:
    account = _account()

    suggestions = build_dispute_reason_suggestions(account)

    assert len(suggestions) == 1
    assert suggestions[0].code == "general_accuracy"
    assert suggestions[0].severity == "low"


def test_detect_missing_evidence_flags_account_and_case_gaps() -> None:
    account = _account(
        payment_status=PaymentStatus.LATE_60,
        balance=Decimal("1500.00"),
        account_number_masked=None,
    )
    case = Case(client_name="Account Client", client_email=None)
    suggestions = build_dispute_reason_suggestions(account)
    checklist = build_evidence_checklist(account)

    missing = detect_missing_evidence(
        account,
        case,
        evidence_checklist=checklist,
        reason_suggestions=suggestions,
    )
    codes = {item.code for item in missing}

    assert "account_identifier" in codes
    assert "reporting_dates" in codes
    assert "client_contact" in codes


def test_build_furnisher_dispute_body_uses_furnisher_language() -> None:
    account = _account(
        payment_status=PaymentStatus.LATE_60,
        balance=Decimal("1500.00"),
        account_number_masked="****1234",
    )
    case = Case(client_name="Account Client", client_email="client@example.com")
    reasons = ["Verify the reported payment history showing Late 60."]

    body = build_furnisher_dispute_body(account, case, reasons)

    assert "Example Bank" in body
    assert "Fair Credit Reporting Act" in body
    assert "consumer reporting agencies" in body
