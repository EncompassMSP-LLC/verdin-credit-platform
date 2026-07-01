"""Register all ORM models with SQLAlchemy metadata."""

from api.core.constants import UserRole
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.models import Document
from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "Case",
    "CaseStatus",
    "Communication",
    "Document",
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
