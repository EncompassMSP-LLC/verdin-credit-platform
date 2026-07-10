"""Unit tests for account intelligence scoring."""

from datetime import date, timedelta
from decimal import Decimal

from api.modules.accounts.intelligence import (
    CRITICAL_RISK_THRESHOLD,
    apply_account_intelligence,
    calculate_risk_score,
    recommend_next_action,
)
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    PaymentStatus,
)


def _make_account(**kwargs: object) -> Account:
    account = Account(
        organization_id=kwargs.get("organization_id"),  # type: ignore[arg-type]
        case_id=kwargs.get("case_id"),  # type: ignore[arg-type]
        creditor_name=str(kwargs.get("creditor_name", "Test Creditor")),
        bureau=kwargs.get("bureau", AccountBureau.EQUIFAX),  # type: ignore[arg-type]
        account_type=kwargs.get("account_type", AccountType.CREDIT_CARD),  # type: ignore[arg-type]
        account_status=kwargs.get("account_status", AccountStatus.OPEN),  # type: ignore[arg-type]
        payment_status=kwargs.get("payment_status", PaymentStatus.CURRENT),  # type: ignore[arg-type]
        account_number_masked=kwargs.get("account_number_masked", "****1234"),  # type: ignore[arg-type]
    )
    for key, value in kwargs.items():
        if hasattr(account, key):
            setattr(account, key, value)
    return account


def test_risk_score_increases_for_delinquency() -> None:
    import uuid

    current = _make_account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        payment_status=PaymentStatus.CURRENT,
    )
    delinquent = _make_account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        payment_status=PaymentStatus.LATE_90,
        past_due_amount=Decimal("1000"),
    )
    assert calculate_risk_score(delinquent) > calculate_risk_score(current)


def test_readiness_score_higher_when_evidence_complete() -> None:
    import uuid

    org_id = uuid.uuid4()
    case_id = uuid.uuid4()
    incomplete = _make_account(
        organization_id=org_id,
        case_id=case_id,
        bureau=AccountBureau.UNKNOWN,
        account_number_masked=None,
        dispute_status=DisputeStatus.EVIDENCE_NEEDED,
    )
    complete = _make_account(
        organization_id=org_id,
        case_id=case_id,
        bureau=AccountBureau.EQUIFAX,
        account_number_masked="****9999",
        dispute_status=DisputeStatus.READY_FOR_DISPUTE,
    )
    apply_account_intelligence(incomplete)
    apply_account_intelligence(complete)
    assert complete.readiness_score is not None
    assert incomplete.readiness_score is not None
    assert complete.readiness_score > incomplete.readiness_score


def test_next_eligible_dispute_date_after_last_dispute() -> None:
    import uuid

    last_dispute = date.today() - timedelta(days=10)
    account = _make_account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        last_dispute_date=last_dispute,
    )
    apply_account_intelligence(account)
    assert account.next_eligible_dispute_date == last_dispute + timedelta(days=30)


def test_critical_risk_threshold() -> None:
    assert CRITICAL_RISK_THRESHOLD == 75


def test_apply_account_intelligence_refreshes_recommended_action() -> None:
    import uuid

    account = _make_account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        dispute_status=DisputeStatus.EVIDENCE_NEEDED,
        ai_recommended_next_action="Stale recommendation",
    )
    apply_account_intelligence(account)
    assert account.ai_recommended_next_action == recommend_next_action(account)
