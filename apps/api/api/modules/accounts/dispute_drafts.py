"""Rule-based dispute draft generation for credit accounts."""

from __future__ import annotations

from decimal import Decimal

from api.modules.accounts.models import Account, AccountStatus, PaymentStatus
from api.modules.cases.models import Case


def _money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"${value:,.2f}"


def _label(value: object) -> str:
    raw = value.value if hasattr(value, "value") else str(value)
    return raw.replace("_", " ").title()


def build_dispute_reasons(account: Account) -> list[str]:
    reasons: list[str] = []
    if account.account_status in {
        AccountStatus.COLLECTION,
        AccountStatus.CHARGE_OFF,
        AccountStatus.REPOSSESSION,
        AccountStatus.FORECLOSURE,
    }:
        reasons.append(f"Verify the reported account status of {_label(account.account_status)}.")
    if account.payment_status not in {PaymentStatus.CURRENT, PaymentStatus.UNKNOWN}:
        reasons.append(
            f"Verify the reported payment history showing {_label(account.payment_status)}."
        )
    if account.balance is not None or account.past_due_amount is not None:
        balance = _money(account.balance) or "the reported balance"
        past_due = _money(account.past_due_amount)
        if past_due is not None:
            reasons.append(
                f"Verify the reported balance of {balance} and past due amount of {past_due}."
            )
        else:
            reasons.append(f"Verify the reported balance of {balance}.")
    if account.date_first_delinquency is not None:
        reasons.append(
            "Verify the date of first delinquency and confirm the reporting period is accurate."
        )
    if not reasons:
        reasons.append("Verify that this tradeline is complete, accurate, and fully documented.")
    return reasons


def build_evidence_checklist(account: Account) -> list[str]:
    checklist = [
        "Current credit report page showing the disputed tradeline",
        "Government-issued ID and proof of current mailing address",
    ]
    if account.account_number_masked:
        checklist.append(f"Masked account identifier evidence for {account.account_number_masked}")
    if account.remarks:
        checklist.append("Notes supporting the disputed reporting details")
    if account.payment_status not in {PaymentStatus.CURRENT, PaymentStatus.UNKNOWN}:
        checklist.append("Payment records or statements supporting payment history dispute")
    if account.balance is not None or account.past_due_amount is not None:
        checklist.append("Statements or creditor records supporting balance dispute")
    return checklist


def build_dispute_body(account: Account, case: Case, dispute_reasons: list[str]) -> str:
    account_identifier = account.account_number_masked or "account number not provided"
    reason_lines = "\n".join(f"- {reason}" for reason in dispute_reasons)
    return (
        f"To whom it may concern,\n\n"
        f"I am writing on behalf of {case.client_name} regarding the {account.bureau.value} "
        f"tradeline reported by {account.creditor_name} ({account_identifier}). "
        "The consumer disputes the accuracy and completeness of this account as reported.\n\n"
        f"Please investigate the following items:\n{reason_lines}\n\n"
        "Please verify this information with the furnisher, provide the method of verification, "
        "and delete or correct any information that cannot be verified as complete and accurate.\n\n"
        "Sincerely,\nVerdin Credit Platform"
    )
