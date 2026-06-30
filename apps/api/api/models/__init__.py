"""Backward-compatible model re-exports."""

from api.core.constants import UserRole
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata
from api.modules.documents.models import Document, DocumentVersion
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "Case",
    "CasePriority",
    "CaseStage",
    "CaseStatus",
    "Communication",
    "Document",
    "DocumentEntityResolution",
    "DocumentMetadata",
    "DocumentVersion",
    "Organization",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "TimelineEvent",
    "User",
    "UserRole",
]
