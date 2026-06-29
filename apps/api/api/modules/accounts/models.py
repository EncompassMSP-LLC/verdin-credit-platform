"""Credit tradeline account models."""

import uuid
from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class AccountBureau(StrEnum):
    EQUIFAX = "equifax"
    EXPERIAN = "experian"
    TRANSUNION = "transunion"
    INNOVIS = "innovis"
    UNKNOWN = "unknown"


class AccountType(StrEnum):
    MORTGAGE = "mortgage"
    AUTO = "auto"
    CREDIT_CARD = "credit_card"
    COLLECTION = "collection"
    PERSONAL_LOAN = "personal_loan"
    STUDENT_LOAN = "student_loan"
    MEDICAL = "medical"
    UTILITY = "utility"
    TELECOM = "telecom"
    OTHER = "other"


class AccountStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    COLLECTION = "collection"
    CHARGE_OFF = "charge_off"
    REPOSSESSION = "repossession"
    FORECLOSURE = "foreclosure"
    TRANSFERRED = "transferred"
    PAID = "paid"
    SETTLED = "settled"
    DELETED = "deleted"
    UNKNOWN = "unknown"


class PaymentStatus(StrEnum):
    CURRENT = "current"
    LATE_30 = "late_30"
    LATE_60 = "late_60"
    LATE_90 = "late_90"
    LATE_120 = "late_120"
    CHARGE_OFF = "charge_off"
    COLLECTION = "collection"
    REPOSSESSION = "repossession"
    FORECLOSURE = "foreclosure"
    UNKNOWN = "unknown"


class DisputeStatus(StrEnum):
    NOT_STARTED = "not_started"
    EVIDENCE_NEEDED = "evidence_needed"
    READY_FOR_DISPUTE = "ready_for_dispute"
    DISPUTE_SENT = "dispute_sent"
    AWAITING_RESPONSE = "awaiting_response"
    VERIFIED = "verified"
    CORRECTED = "corrected"
    DELETED = "deleted"
    ESCALATED = "escalated"
    MONITORING = "monitoring"


class InvestigationStatus(StrEnum):
    NONE = "none"
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    ESCALATED = "escalated"


class Account(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    bureau: Mapped[AccountBureau] = mapped_column(
        Enum(AccountBureau, name="account_bureau", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AccountBureau.UNKNOWN,
        index=True,
    )
    creditor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_creditor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_number_masked: Mapped[str | None] = mapped_column(String(50), nullable=True)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(
            AccountType,
            name="tradeline_account_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=AccountType.OTHER,
        index=True,
    )
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(
            AccountStatus,
            name="tradeline_account_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=AccountStatus.UNKNOWN,
        index=True,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="tradeline_payment_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PaymentStatus.UNKNOWN,
        index=True,
    )
    balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    high_balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    monthly_payment: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    past_due_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    date_opened: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_reported: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_last_activity: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_first_delinquency: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_removal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    responsibility: Mapped[str | None] = mapped_column(String(50), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispute_status: Mapped[DisputeStatus] = mapped_column(
        Enum(
            DisputeStatus,
            name="tradeline_dispute_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=DisputeStatus.NOT_STARTED,
        index=True,
    )
    dispute_round: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    investigation_status: Mapped[InvestigationStatus] = mapped_column(
        Enum(
            InvestigationStatus,
            name="tradeline_investigation_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=InvestigationStatus.NONE,
    )
    last_dispute_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_eligible_dispute_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    response_received: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cra_dispute: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    furnisher_dispute: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cfpb_dispute: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_recommended_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    organization: Mapped["Organization"] = relationship(back_populates="accounts")
    case: Mapped["Case"] = relationship(back_populates="credit_accounts")
