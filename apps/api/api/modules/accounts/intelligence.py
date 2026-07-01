"""Account intelligence scoring and dispute readiness."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    DisputeStatus,
    InvestigationStatus,
    PaymentStatus,
)

CRITICAL_RISK_THRESHOLD = 75
DISPUTE_COOLDOWN_DAYS = 30

_PAYMENT_RISK: dict[PaymentStatus, int] = {
    PaymentStatus.CURRENT: 0,
    PaymentStatus.LATE_30: 15,
    PaymentStatus.LATE_60: 25,
    PaymentStatus.LATE_90: 35,
    PaymentStatus.LATE_120: 45,
    PaymentStatus.CHARGE_OFF: 50,
    PaymentStatus.COLLECTION: 50,
    PaymentStatus.REPOSSESSION: 45,
    PaymentStatus.FORECLOSURE: 45,
    PaymentStatus.UNKNOWN: 10,
}

_STATUS_RISK: dict[AccountStatus, int] = {
    AccountStatus.COLLECTION: 20,
    AccountStatus.CHARGE_OFF: 25,
    AccountStatus.REPOSSESSION: 25,
    AccountStatus.FORECLOSURE: 25,
    AccountStatus.OPEN: 0,
    AccountStatus.CLOSED: 5,
    AccountStatus.TRANSFERRED: 5,
    AccountStatus.PAID: 0,
    AccountStatus.SETTLED: 5,
    AccountStatus.DELETED: 0,
    AccountStatus.UNKNOWN: 10,
}

_ACTIVE_DISPUTE_STATUSES = frozenset(
    {
        DisputeStatus.DISPUTE_SENT,
        DisputeStatus.AWAITING_RESPONSE,
        DisputeStatus.VERIFIED,
        DisputeStatus.CORRECTED,
        DisputeStatus.DELETED,
        DisputeStatus.ESCALATED,
    }
)


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def calculate_risk_score(account: Account) -> int:
    score = 10
    score += _PAYMENT_RISK.get(account.payment_status, 10)
    score += _STATUS_RISK.get(account.account_status, 0)

    if account.past_due_amount is not None and account.past_due_amount > 0:
        past_due_bonus = min(20, int(account.past_due_amount / Decimal("500")))
        score += past_due_bonus

    if account.balance is not None and account.balance >= Decimal("10000"):
        score += 10

    return _clamp_score(score)


def calculate_next_eligible_dispute_date(account: Account) -> date | None:
    if account.last_dispute_date is None:
        return None
    return account.last_dispute_date + timedelta(days=DISPUTE_COOLDOWN_DAYS)


def _has_minimum_evidence(account: Account) -> bool:
    return (
        bool(account.creditor_name.strip())
        and account.bureau != AccountBureau.UNKNOWN
        and account.account_number_masked is not None
    )


def calculate_dispute_status(account: Account) -> DisputeStatus:
    current = account.dispute_status
    if current in _ACTIVE_DISPUTE_STATUSES:
        return current

    if not _has_minimum_evidence(account):
        return DisputeStatus.EVIDENCE_NEEDED

    next_eligible = calculate_next_eligible_dispute_date(account)
    if next_eligible is not None and next_eligible > date.today():
        return DisputeStatus.MONITORING

    if current in (
        DisputeStatus.NOT_STARTED,
        DisputeStatus.EVIDENCE_NEEDED,
        DisputeStatus.MONITORING,
    ):
        return DisputeStatus.READY_FOR_DISPUTE

    return current


def calculate_readiness_score(account: Account) -> int:
    base_by_status: dict[DisputeStatus, int] = {
        DisputeStatus.NOT_STARTED: 35,
        DisputeStatus.EVIDENCE_NEEDED: 25,
        DisputeStatus.READY_FOR_DISPUTE: 90,
        DisputeStatus.DISPUTE_SENT: 60,
        DisputeStatus.AWAITING_RESPONSE: 55,
        DisputeStatus.VERIFIED: 40,
        DisputeStatus.CORRECTED: 95,
        DisputeStatus.DELETED: 100,
        DisputeStatus.ESCALATED: 50,
        DisputeStatus.MONITORING: 30,
    }
    score = base_by_status.get(account.dispute_status, 30)

    if _has_minimum_evidence(account):
        score += 10

    if account.investigation_status == InvestigationStatus.OVERDUE:
        score -= 15
    elif account.investigation_status == InvestigationStatus.PENDING:
        score -= 5

    next_eligible = account.next_eligible_dispute_date
    if next_eligible is not None and next_eligible > date.today():
        score -= 20

    return _clamp_score(score)


def recommend_next_action(account: Account) -> str:
    if account.dispute_status == DisputeStatus.EVIDENCE_NEEDED:
        return "Collect bureau tradeline evidence and masked account identifier"
    if account.dispute_status == DisputeStatus.MONITORING:
        return "Wait until next eligible dispute date before filing"
    if account.dispute_status == DisputeStatus.READY_FOR_DISPUTE:
        return "Prepare and send dispute letter to CRA"
    if account.dispute_status == DisputeStatus.AWAITING_RESPONSE:
        return "Follow up on pending CRA or furnisher response"
    if account.dispute_status == DisputeStatus.VERIFIED:
        return "Review verified tradeline reporting and decide on escalation or monitoring"
    if account.dispute_status == DisputeStatus.CORRECTED:
        return "Confirm corrected reporting on the next credit report import"
    if account.dispute_status == DisputeStatus.DELETED:
        return "Monitor credit report to confirm tradeline removal"
    if account.risk_score is not None and account.risk_score >= CRITICAL_RISK_THRESHOLD:
        return "Prioritize high-risk tradeline for immediate review"
    if account.investigation_status == InvestigationStatus.OVERDUE:
        return "Escalate overdue investigation"
    return "Review tradeline details and update case notes"


def apply_account_intelligence(account: Account) -> None:
    account.next_eligible_dispute_date = calculate_next_eligible_dispute_date(account)
    account.dispute_status = calculate_dispute_status(account)
    account.risk_score = calculate_risk_score(account)
    account.readiness_score = calculate_readiness_score(account)
    if not account.ai_recommended_next_action:
        account.ai_recommended_next_action = recommend_next_action(account)
