"""Unwanted-call complaint incident entities (LRP-209A).

Staff-mediated tracking only. Never auto-submits to FTC/CFPB/DNC registries
and never draws legal conclusions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class UnwantedCallPartyType(StrEnum):
    CREDITOR = "creditor"
    COLLECTOR = "collector"
    TELEMARKETER = "telemarketer"
    UNKNOWN = "unknown"


class UnwantedCallChannel(StrEnum):
    PHONE = "phone"
    VOIP = "voip"
    SMS = "sms"
    UNKNOWN = "unknown"


class UnwantedCallIncidentStatus(StrEnum):
    OPEN = "open"
    DOCUMENTING = "documenting"
    DRAFT_READY = "draft_ready"
    SUBMITTED_EXTERNALLY = "submitted_externally"
    FOLLOW_UP_DUE = "follow_up_due"
    CLOSED = "closed"
    ABANDONED = "abandoned"


class UnwantedCallComplaintTarget(StrEnum):
    NONE = "none"
    FTC = "ftc"
    CFPB = "cfpb"
    STATE_AG = "state_ag"
    CARRIER = "carrier"
    OTHER = "other"


class UnwantedCallExternalSubmissionStatus(StrEnum):
    NOT_STARTED = "not_started"
    DRAFT_PREPARED = "draft_prepared"
    CLIENT_SUBMITTED = "client_submitted"
    STAFF_RECORDED = "staff_recorded"


class UnwantedCallIncident(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Staff-logged unwanted call with advisory eligibility and draft scaffold."""

    __tablename__ = "unwanted_call_incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True, index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True
    )
    creditor_or_collector_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    party_type: Mapped[UnwantedCallPartyType] = mapped_column(
        Enum(
            UnwantedCallPartyType,
            name="unwanted_call_party_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UnwantedCallPartyType.UNKNOWN,
    )
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    caller_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    called_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    channel: Mapped[UnwantedCallChannel] = mapped_column(
        Enum(
            UnwantedCallChannel,
            name="unwanted_call_channel",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UnwantedCallChannel.PHONE,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preference_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    eligibility_guidance: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    status: Mapped[UnwantedCallIncidentStatus] = mapped_column(
        Enum(
            UnwantedCallIncidentStatus,
            name="unwanted_call_incident_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UnwantedCallIncidentStatus.OPEN,
        index=True,
    )
    follow_up_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    follow_up_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    complaint_target: Mapped[UnwantedCallComplaintTarget] = mapped_column(
        Enum(
            UnwantedCallComplaintTarget,
            name="unwanted_call_complaint_target",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UnwantedCallComplaintTarget.NONE,
    )
    external_submission_status: Mapped[UnwantedCallExternalSubmissionStatus] = mapped_column(
        Enum(
            UnwantedCallExternalSubmissionStatus,
            name="unwanted_call_external_submission_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UnwantedCallExternalSubmissionStatus.NOT_STARTED,
    )
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True
    )
    draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)
