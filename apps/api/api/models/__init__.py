"""Backward-compatible model re-exports."""

from api.core.constants import UserRole
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "Case",
    "CasePriority",
    "CaseStage",
    "CaseStatus",
    "Client",
    "ClientContact",
    "ClientStatus",
    "ContactRelationship",
    "Communication",
    "Document",
    "DocumentEntityResolution",
    "DocumentMetadata",
    "DocumentParsedCreditReport",
    "DocumentVersion",
    "DisputeLetter",
    "DisputeLetterStatus",
    "Notification",
    "NotificationCategory",
    "Organization",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "TimelineEvent",
    "User",
    "UserRole",
]
