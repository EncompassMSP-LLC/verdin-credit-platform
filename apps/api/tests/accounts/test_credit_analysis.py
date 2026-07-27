"""Unit tests for deterministic Lending Readiness compose (Vol 22)."""

import uuid
from decimal import Decimal

from api.modules.accounts.credit_analysis import compose_credit_analysis, score_to_band
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    PaymentStatus,
)


def _account(**overrides: object) -> Account:
    account = Account(
        organization_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        creditor_name="Test Bank",
        bureau=AccountBureau.EXPERIAN,
        account_type=AccountType.CREDIT_CARD,
        account_status=AccountStatus.OPEN,
        payment_status=PaymentStatus.CURRENT,
        dispute_status=DisputeStatus.NOT_STARTED,
        account_number_masked="****1234",
    )
    for key, value in overrides.items():
        setattr(account, key, value)
    return account


def test_score_to_band_thresholds() -> None:
    assert score_to_band(20) == "building"
    assert score_to_band(40) == "progressing"
    assert score_to_band(65) == "near_ready"
    assert score_to_band(85) == "lending_ready"


def test_compose_empty_accounts_building() -> None:
    result = compose_credit_analysis([])
    assert result.band == "building"
    assert result.borrower_readiness_score == 25
    assert result.tradelines_evaluated == 0
    assert result.payload["disclaimer"]
    assert any(b["id"] == "no-tradelines" for b in result.payload["blockers"])


def test_compose_healthy_tradeline_higher_than_collection() -> None:
    healthy = _account(
        payment_status=PaymentStatus.CURRENT,
        account_status=AccountStatus.OPEN,
        dispute_status=DisputeStatus.CORRECTED,
        balance=Decimal("500"),
        credit_limit=Decimal("5000"),
        bureau=AccountBureau.EQUIFAX,
    )
    stressed = _account(
        payment_status=PaymentStatus.COLLECTION,
        account_status=AccountStatus.COLLECTION,
        dispute_status=DisputeStatus.EVIDENCE_NEEDED,
        balance=Decimal("2000"),
        credit_limit=Decimal("2000"),
        bureau=AccountBureau.TRANSUNION,
    )
    healthy_run = compose_credit_analysis([healthy])
    stressed_run = compose_credit_analysis([stressed])
    assert healthy_run.borrower_readiness_score > stressed_run.borrower_readiness_score
    assert len(stressed_run.payload["blockers"]) >= 1
    assert len(healthy_run.payload["dimensions"]) == 8


def test_compose_includes_cross_bureau_and_metro2_blockers() -> None:
    experian = _account(
        id=uuid.uuid4(),
        creditor_name="Shared Bank",
        account_number_masked="****9999",
        bureau=AccountBureau.EXPERIAN,
        account_status=AccountStatus.OPEN,
        payment_status=PaymentStatus.CURRENT,
        balance=Decimal("1000"),
        credit_limit=Decimal("5000"),
    )
    equifax = _account(
        id=uuid.uuid4(),
        creditor_name="Shared Bank",
        account_number_masked="****9999",
        bureau=AccountBureau.EQUIFAX,
        account_status=AccountStatus.OPEN,
        payment_status=PaymentStatus.CURRENT,
        balance=Decimal("2500"),
        credit_limit=Decimal("5000"),
    )
    metro2_issue = _account(
        id=uuid.uuid4(),
        creditor_name="Closed Balance Bank",
        bureau=AccountBureau.TRANSUNION,
        account_status=AccountStatus.CLOSED,
        payment_status=PaymentStatus.CURRENT,
        balance=Decimal("400"),
        credit_limit=Decimal("400"),
    )
    result = compose_credit_analysis([experian, equifax, metro2_issue])
    ids = [b["id"] for b in result.payload["blockers"]]
    assert any(item.startswith("cross-bureau:") for item in ids)
    assert any(item.startswith("metro2:") for item in ids)
    summary = result.payload["compliance_summary"]
    assert summary["cross_bureau_total"] >= 1
    assert summary["metro2_total"] >= 1
    assert result.formula_version == "lrs.v1.1"
