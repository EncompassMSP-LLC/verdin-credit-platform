"""Unit tests for rule-based dispute draft generation."""

import uuid
from decimal import Decimal

from api.modules.accounts.dispute_drafts import build_dispute_reason_suggestions
from api.modules.accounts.models import Account, AccountBureau, AccountStatus, PaymentStatus


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
