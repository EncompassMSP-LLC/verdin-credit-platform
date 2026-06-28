"""Backward-compatible model re-exports."""

from api.core.constants import UserRole
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.models import Document
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "Case",
    "CaseStatus",
    "Communication",
    "Document",
    "Organization",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "TimelineEvent",
    "User",
    "UserRole",
]
