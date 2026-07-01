"""Rule-based dispute draft generation for credit accounts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from api.modules.accounts.models import Account, AccountStatus, PaymentStatus
from api.modules.cases.models import Case

DisputeReasonCategory = Literal["accuracy", "completeness", "verification"]
DisputeReasonSeverity = Literal["low", "medium", "high"]
DisputeRecipientType = Literal["credit_bureau", "furnisher"]

CRA_TEMPLATE_ID = "cra-tradeline-investigation-v1"
FURNISHER_TEMPLATE_ID = "furnisher-direct-dispute-v1"


@dataclass(frozen=True, slots=True)
class DisputeReasonSuggestion:
    code: str
    category: DisputeReasonCategory
    title: str
    description: str
    severity: DisputeReasonSeverity
    requires_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MissingEvidenceItem:
    code: str
    title: str
    description: str
    severity: DisputeReasonSeverity
    checklist_item: str | None = None


def _money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"${value:,.2f}"


def _label(value: object) -> str:
    raw = value.value if hasattr(value, "value") else str(value)
    return raw.replace("_", " ").title()


def build_dispute_reason_suggestions(account: Account) -> list[DisputeReasonSuggestion]:
    suggestions: list[DisputeReasonSuggestion] = []

    if account.account_status in {
        AccountStatus.COLLECTION,
        AccountStatus.CHARGE_OFF,
        AccountStatus.REPOSSESSION,
        AccountStatus.FORECLOSURE,
    }:
        suggestions.append(
            DisputeReasonSuggestion(
                code="account_status",
                category="accuracy",
                title="Account status reporting",
                description=(
                    f"Verify the reported account status of {_label(account.account_status)}."
                ),
                severity="high",
                requires_evidence=(
                    "Current credit report page showing the disputed tradeline",
                    "Creditor correspondence or statements supporting the correct status",
                ),
            )
        )

    if account.payment_status not in {PaymentStatus.CURRENT, PaymentStatus.UNKNOWN}:
        suggestions.append(
            DisputeReasonSuggestion(
                code="payment_history",
                category="accuracy",
                title="Payment history reporting",
                description=(
                    f"Verify the reported payment history showing {_label(account.payment_status)}."
                ),
                severity="high",
                requires_evidence=(
                    "Payment records or statements supporting payment history dispute",
                    "Current credit report page showing the disputed tradeline",
                ),
            )
        )

    if account.balance is not None or account.past_due_amount is not None:
        balance = _money(account.balance) or "the reported balance"
        past_due = _money(account.past_due_amount)
        if past_due is not None:
            description = (
                f"Verify the reported balance of {balance} and past due amount of {past_due}."
            )
        else:
            description = f"Verify the reported balance of {balance}."
        suggestions.append(
            DisputeReasonSuggestion(
                code="balance",
                category="accuracy",
                title="Balance and past-due amounts",
                description=description,
                severity="medium",
                requires_evidence=(
                    "Statements or creditor records supporting balance dispute",
                    "Current credit report page showing the disputed tradeline",
                ),
            )
        )

    if account.date_first_delinquency is not None:
        suggestions.append(
            DisputeReasonSuggestion(
                code="delinquency_date",
                category="completeness",
                title="Date of first delinquency",
                description=(
                    "Verify the date of first delinquency and confirm the reporting period "
                    "is accurate."
                ),
                severity="medium",
                requires_evidence=(
                    "Payment records supporting the correct delinquency timeline",
                    "Current credit report page showing the disputed tradeline",
                ),
            )
        )

    if not suggestions:
        suggestions.append(
            DisputeReasonSuggestion(
                code="general_accuracy",
                category="verification",
                title="General accuracy review",
                description=(
                    "Verify that this tradeline is complete, accurate, and fully documented."
                ),
                severity="low",
                requires_evidence=(
                    "Current credit report page showing the disputed tradeline",
                    "Government-issued ID and proof of current mailing address",
                ),
            )
        )

    return suggestions


def build_dispute_reasons(account: Account) -> list[str]:
    return [suggestion.description for suggestion in build_dispute_reason_suggestions(account)]


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


def detect_missing_evidence(
    account: Account,
    case: Case,
    *,
    evidence_checklist: list[str],
    reason_suggestions: list[DisputeReasonSuggestion],
) -> list[MissingEvidenceItem]:
    missing: list[MissingEvidenceItem] = []
    suggestion_codes = {suggestion.code for suggestion in reason_suggestions}

    if not account.account_number_masked:
        missing.append(
            MissingEvidenceItem(
                code="account_identifier",
                title="Masked account identifier",
                description=(
                    "Add a masked account number on the tradeline before filing so staff can "
                    "match bureau records to the correct account."
                ),
                severity="high",
                checklist_item="Masked account identifier evidence for bureau matching",
            )
        )

    if suggestion_codes & {"payment_history", "delinquency_date"}:
        if account.date_reported is None and account.date_last_activity is None:
            missing.append(
                MissingEvidenceItem(
                    code="reporting_dates",
                    title="Reporting timeline dates",
                    description=(
                        "Add date reported or date of last activity to support payment history "
                        "and delinquency disputes."
                    ),
                    severity="medium",
                    checklist_item=next(
                        (
                            item
                            for item in evidence_checklist
                            if "payment history" in item.lower() or "delinquency" in item.lower()
                        ),
                        None,
                    ),
                )
            )

    if (
        account.account_status
        in {
            AccountStatus.COLLECTION,
            AccountStatus.CHARGE_OFF,
            AccountStatus.REPOSSESSION,
            AccountStatus.FORECLOSURE,
        }
        and not account.remarks
    ):
        missing.append(
            MissingEvidenceItem(
                code="account_notes",
                title="Dispute support notes",
                description=(
                    "Add account remarks summarizing why the adverse status reporting is disputed."
                ),
                severity="medium",
                checklist_item=next(
                    (item for item in evidence_checklist if "Notes supporting" in item),
                    None,
                ),
            )
        )

    if not case.client_email:
        missing.append(
            MissingEvidenceItem(
                code="client_contact",
                title="Client contact email",
                description=(
                    "Add the client email on the linked case for identity verification and "
                    "bureau correspondence."
                ),
                severity="medium",
                checklist_item=next(
                    (item for item in evidence_checklist if "Government-issued ID" in item),
                    "Government-issued ID and proof of current mailing address",
                ),
            )
        )

    return missing


def build_furnisher_evidence_checklist(account: Account) -> list[str]:
    checklist = build_evidence_checklist(account)
    checklist.append("Copy of credit report showing furnisher-reported tradeline")
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


def build_furnisher_dispute_body(account: Account, case: Case, dispute_reasons: list[str]) -> str:
    account_identifier = account.account_number_masked or "account number not provided"
    reason_lines = "\n".join(f"- {reason}" for reason in dispute_reasons)
    furnisher_name = account.original_creditor or account.creditor_name
    return (
        f"To whom it may concern at {furnisher_name},\n\n"
        f"I am writing on behalf of {case.client_name} regarding inaccurate information your "
        f"company is furnishing to {_label(account.bureau)} for account {account_identifier}. "
        "The consumer disputes the accuracy and completeness of the information you are reporting.\n\n"
        f"Under the Fair Credit Reporting Act, please investigate the following items:\n"
        f"{reason_lines}\n\n"
        "Correct or delete any information that cannot be verified as complete and accurate, "
        "and notify all consumer reporting agencies to whom you furnish data.\n\n"
        "Sincerely,\nVerdin Credit Platform"
    )
