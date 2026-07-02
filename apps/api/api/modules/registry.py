"""Register all ORM models with SQLAlchemy metadata."""

from api.core.constants import UserRole
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CaseStatus
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship
from api.modules.compliance.models import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    RetentionPolicy,
    RetentionScope,
)
from api.modules.documents.models import Document
from api.modules.messaging.models import (
    MessageSenderRole,
    MessageThread,
    MessageThreadStatus,
    ThreadMessage,
)
from api.modules.notifications.models import EmailDeliveryLog, Notification, NotificationCategory
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "Case",
    "CaseStatus",
    "Client",
    "ClientContact",
    "ClientPortalUser",
    "ClientStatus",
    "ConsentRecord",
    "ConsentStatus",
    "ConsentType",
    "ContactRelationship",
    "Communication",
    "Document",
    "DisputeLetter",
    "DisputeLetterStatus",
    "EmailDeliveryLog",
    "MessageSenderRole",
    "MessageThread",
    "MessageThreadStatus",
    "Notification",
    "NotificationCategory",
    "Organization",
    "RetentionPolicy",
    "RetentionScope",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "ThreadMessage",
    "TimelineEvent",
    "User",
    "UserRole",
]
