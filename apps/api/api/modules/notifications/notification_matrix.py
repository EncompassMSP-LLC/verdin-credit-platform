"""LRP notification matrix v1 — event → audience → channel map (LRP-202).

Source: docs/lrp-enterprise/.../section-14-automation/notification-matrix.md
SMS remains TCPA-gated; realtor audience deferred until partner JWT realm (LRP-301).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    CRM_TASK = "crm_task"


class NotificationAudience(StrEnum):
    PARTNER_SUCCESS = "partner_success"
    CREDIT_SPECIALIST = "credit_specialist"
    REFERRING_LO = "referring_lo"
    REALTOR = "realtor"
    BORROWER = "borrower"
    CASE_OWNER = "case_owner"
    PARTNER_AUTHORIZED = "partner_authorized"
    ENG_ONCALL = "eng_oncall"
    OPS = "ops"
    PARTNER_SUCCESS_LEAD = "partner_success_lead"


class NotificationMatrixEvent(StrEnum):
    WEBSITE_CONTACT = "website_contact"
    REFERRAL_SUBMITTED = "referral_submitted"
    REFERRAL_ASSIGNED = "referral_assigned"
    CONSULTATION_SCHEDULED = "consultation_scheduled"
    APPOINTMENT_REMINDER_T24H = "appointment_reminder_t24h"
    APPOINTMENT_REMINDER_T1H = "appointment_reminder_t1h"
    CONSULTATION_COMPLETED = "consultation_completed"
    STATUS_REPORT_PUBLISHED = "status_report_published"
    MORTGAGE_READY = "mortgage_ready"
    PARTNER_INACTIVE_30D = "partner_inactive_30d"
    PORTAL_INVITE = "portal_invite"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_NEEDS_ATTENTION = "document_needs_attention"
    DISPUTE_LETTER_READY = "dispute_letter_ready"
    DISPUTE_LETTER_SENT = "dispute_letter_sent"
    READINESS_REPORT_AVAILABLE = "readiness_report_available"
    WORKER_JOB_FAILED = "worker_job_failed"
    DELIVERABILITY_ALERT = "deliverability_alert"
    SLA_BREACH_REFERRAL_ACK = "sla_breach_referral_ack"


SCHEMA_VERSION = "notification-matrix.v1"

_ADVISORY_FOOTER = (
    "This message is operational only — not an underwriting decision, loan approval, "
    "or guarantee of funding."
)


@dataclass(frozen=True, slots=True)
class MatrixRoute:
    audience: NotificationAudience
    channels: frozenset[NotificationChannel]
    optional: bool = False


@dataclass(frozen=True, slots=True)
class MatrixEventDefinition:
    event: NotificationMatrixEvent
    title: str
    category: str
    routes: tuple[MatrixRoute, ...]
    group: str


NOTIFICATION_MATRIX: dict[NotificationMatrixEvent, MatrixEventDefinition] = {
    NotificationMatrixEvent.WEBSITE_CONTACT: MatrixEventDefinition(
        event=NotificationMatrixEvent.WEBSITE_CONTACT,
        title="Website contact (B2B)",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
        ),
    ),
    NotificationMatrixEvent.REFERRAL_SUBMITTED: MatrixEventDefinition(
        event=NotificationMatrixEvent.REFERRAL_SUBMITTED,
        title="Referral submitted",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
            MatrixRoute(
                NotificationAudience.CREDIT_SPECIALIST,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REALTOR,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL}),
            ),
        ),
    ),
    NotificationMatrixEvent.REFERRAL_ASSIGNED: MatrixEventDefinition(
        event=NotificationMatrixEvent.REFERRAL_ASSIGNED,
        title="Referral assigned",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset({NotificationChannel.IN_APP, NotificationChannel.CRM_TASK}),
            ),
            MatrixRoute(
                NotificationAudience.CREDIT_SPECIALIST,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.CONSULTATION_SCHEDULED: MatrixEventDefinition(
        event=NotificationMatrixEvent.CONSULTATION_SCHEDULED,
        title="Consultation scheduled",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CREDIT_SPECIALIST,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REALTOR,
                frozenset({NotificationChannel.IN_APP}),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.SMS,
                        NotificationChannel.IN_APP,
                    }
                ),
            ),
        ),
    ),
    NotificationMatrixEvent.APPOINTMENT_REMINDER_T24H: MatrixEventDefinition(
        event=NotificationMatrixEvent.APPOINTMENT_REMINDER_T24H,
        title="Appointment reminder (T-24h)",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.SMS,
                        NotificationChannel.IN_APP,
                    }
                ),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.IN_APP}),
                optional=True,
            ),
        ),
    ),
    NotificationMatrixEvent.APPOINTMENT_REMINDER_T1H: MatrixEventDefinition(
        event=NotificationMatrixEvent.APPOINTMENT_REMINDER_T1H,
        title="Appointment reminder (T-1h)",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.SMS,
                    }
                ),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.CONSULTATION_COMPLETED: MatrixEventDefinition(
        event=NotificationMatrixEvent.CONSULTATION_COMPLETED,
        title="Consultation completed",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
            MatrixRoute(
                NotificationAudience.CREDIT_SPECIALIST,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REALTOR,
                frozenset({NotificationChannel.EMAIL}),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.STATUS_REPORT_PUBLISHED: MatrixEventDefinition(
        event=NotificationMatrixEvent.STATUS_REPORT_PUBLISHED,
        title="Status report published",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REALTOR,
                frozenset({NotificationChannel.EMAIL}),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.MORTGAGE_READY: MatrixEventDefinition(
        event=NotificationMatrixEvent.MORTGAGE_READY,
        title="Mortgage Ready (advisory)",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CREDIT_SPECIALIST,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REFERRING_LO,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.REALTOR,
                frozenset({NotificationChannel.EMAIL}),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.PARTNER_INACTIVE_30D: MatrixEventDefinition(
        event=NotificationMatrixEvent.PARTNER_INACTIVE_30D,
        title="Partner inactive 30d",
        category="workflow",
        group="partner_referral",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.CRM_TASK}),
            ),
        ),
    ),
    NotificationMatrixEvent.PORTAL_INVITE: MatrixEventDefinition(
        event=NotificationMatrixEvent.PORTAL_INVITE,
        title="Portal invite",
        category="system",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.TASK_DUE_SOON: MatrixEventDefinition(
        event=NotificationMatrixEvent.TASK_DUE_SOON,
        title="Task due soon",
        category="task",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.SMS,
                    }
                ),
                optional=True,
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.TASK_OVERDUE: MatrixEventDefinition(
        event=NotificationMatrixEvent.TASK_OVERDUE,
        title="Task overdue",
        category="task",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
        ),
    ),
    NotificationMatrixEvent.DOCUMENT_UPLOADED: MatrixEventDefinition(
        event=NotificationMatrixEvent.DOCUMENT_UPLOADED,
        title="Document uploaded",
        category="document",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP, NotificationChannel.CRM_TASK}),
            ),
        ),
    ),
    NotificationMatrixEvent.DOCUMENT_NEEDS_ATTENTION: MatrixEventDefinition(
        event=NotificationMatrixEvent.DOCUMENT_NEEDS_ATTENTION,
        title="Document needs attention",
        category="document",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
        ),
    ),
    NotificationMatrixEvent.DISPUTE_LETTER_READY: MatrixEventDefinition(
        event=NotificationMatrixEvent.DISPUTE_LETTER_READY,
        title="Dispute letter ready for review",
        category="dispute",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
        ),
    ),
    NotificationMatrixEvent.DISPUTE_LETTER_SENT: MatrixEventDefinition(
        event=NotificationMatrixEvent.DISPUTE_LETTER_SENT,
        title="Dispute letter sent (staff-approved)",
        category="dispute",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.PARTNER_AUTHORIZED,
                frozenset({NotificationChannel.IN_APP}),
                optional=True,
            ),
        ),
    ),
    NotificationMatrixEvent.READINESS_REPORT_AVAILABLE: MatrixEventDefinition(
        event=NotificationMatrixEvent.READINESS_REPORT_AVAILABLE,
        title="Readiness report available",
        category="workflow",
        group="borrower_case",
        routes=(
            MatrixRoute(
                NotificationAudience.BORROWER,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.CASE_OWNER,
                frozenset({NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.PARTNER_AUTHORIZED,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
                optional=True,
            ),
        ),
    ),
    NotificationMatrixEvent.WORKER_JOB_FAILED: MatrixEventDefinition(
        event=NotificationMatrixEvent.WORKER_JOB_FAILED,
        title="Worker job failed (retries exhausted)",
        category="system",
        group="system_ops",
        routes=(
            MatrixRoute(
                NotificationAudience.ENG_ONCALL,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
            MatrixRoute(
                NotificationAudience.OPS,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.DELIVERABILITY_ALERT: MatrixEventDefinition(
        event=NotificationMatrixEvent.DELIVERABILITY_ALERT,
        title="SMS/email deliverability alert",
        category="system",
        group="system_ops",
        routes=(
            MatrixRoute(
                NotificationAudience.OPS,
                frozenset({NotificationChannel.EMAIL, NotificationChannel.IN_APP}),
            ),
        ),
    ),
    NotificationMatrixEvent.SLA_BREACH_REFERRAL_ACK: MatrixEventDefinition(
        event=NotificationMatrixEvent.SLA_BREACH_REFERRAL_ACK,
        title="SLA breach (referral ack)",
        category="workflow",
        group="system_ops",
        routes=(
            MatrixRoute(
                NotificationAudience.PARTNER_SUCCESS_LEAD,
                frozenset(
                    {
                        NotificationChannel.EMAIL,
                        NotificationChannel.IN_APP,
                        NotificationChannel.CRM_TASK,
                    }
                ),
            ),
        ),
    ),
}


def list_matrix_events() -> list[MatrixEventDefinition]:
    return list(NOTIFICATION_MATRIX.values())


def get_matrix_event(event: NotificationMatrixEvent | str) -> MatrixEventDefinition:
    key = NotificationMatrixEvent(event)
    return NOTIFICATION_MATRIX[key]


def advisory_footer() -> str:
    return _ADVISORY_FOOTER
