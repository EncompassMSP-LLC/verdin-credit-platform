"""Platform event builders for domain services."""

import uuid
from typing import Any

from verdin_event_bus import PlatformEvent
from verdin_event_types import (
    AccountEventType,
    AuthEventType,
    CaseEventType,
    DocumentEventType,
    EventCategory,
    TaskEventType,
)

from api.modules.accounts.dispute_letter_models import DisputeLetter
from api.modules.accounts.models import Account
from api.modules.auth.models import User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.models import Document
from api.modules.tasks.models import Task


def case_created_event(case: Case, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=CaseEventType.CASE_CREATED.value,
        event_category=EventCategory.CASE.value,
        title="Case created",
        description=f"Case '{case.title}' was created for {case.client_name}.",
        organization_id=case.organization_id,
        case_id=case.id,
        performed_by=performed_by,
        source_module="cases",
        metadata={
            "case_number": case.case_number,
            "status": case.status.value if hasattr(case.status, "value") else case.status,
            "client_name": case.client_name,
        },
    )


def case_updated_event(case: Case, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=CaseEventType.CASE_UPDATED.value,
        event_category=EventCategory.CASE.value,
        title="Case updated",
        description=f"Case '{case.title}' was updated.",
        organization_id=case.organization_id,
        case_id=case.id,
        performed_by=performed_by,
        source_module="cases",
        metadata={
            "status": case.status.value if hasattr(case.status, "value") else case.status,
            "stage": case.stage.value if hasattr(case.stage, "value") else case.stage,
        },
    )


def case_closed_event(case: Case, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=CaseEventType.CASE_CLOSED.value,
        event_category=EventCategory.CASE.value,
        title="Case closed",
        description=f"Case '{case.title}' was closed.",
        organization_id=case.organization_id,
        case_id=case.id,
        performed_by=performed_by,
        source_module="cases",
        metadata={"status": case.status.value if hasattr(case.status, "value") else case.status},
    )


def account_created_event(account: Account, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=AccountEventType.ACCOUNT_CREATED.value,
        event_category=EventCategory.ACCOUNT.value,
        title="Account added",
        description=f"Account for '{account.creditor_name}' was added.",
        organization_id=account.organization_id,
        case_id=account.case_id,
        account_id=account.id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "creditor_name": account.creditor_name,
            "bureau": account.bureau.value if hasattr(account.bureau, "value") else account.bureau,
        },
    )


def account_updated_event(account: Account, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=AccountEventType.ACCOUNT_UPDATED.value,
        event_category=EventCategory.ACCOUNT.value,
        title="Account updated",
        description=f"Account '{account.creditor_name}' was updated.",
        organization_id=account.organization_id,
        case_id=account.case_id,
        account_id=account.id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={"creditor_name": account.creditor_name},
    )


def account_status_changed_event(
    account: Account,
    performed_by: uuid.UUID,
    *,
    previous_status: str | None = None,
) -> PlatformEvent:
    status = (
        account.account_status.value
        if hasattr(account.account_status, "value")
        else account.account_status
    )
    return PlatformEvent(
        event_type=AccountEventType.ACCOUNT_STATUS_CHANGED.value,
        event_category=EventCategory.ACCOUNT.value,
        title="Account status changed",
        description=f"Account '{account.creditor_name}' status changed to {status}.",
        organization_id=account.organization_id,
        case_id=account.case_id,
        account_id=account.id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "previous_status": previous_status,
            "account_status": status,
            "payment_status": (
                account.payment_status.value
                if hasattr(account.payment_status, "value")
                else account.payment_status
            ),
        },
    )


def dispute_letter_draft_created_event(
    dispute_letter: DisputeLetter,
    performed_by: uuid.UUID,
) -> PlatformEvent:
    return PlatformEvent(
        event_type="DISPUTE_LETTER_DRAFT_CREATED",
        event_category=EventCategory.ACCOUNT.value,
        title="Dispute letter draft saved",
        description=f"Dispute letter draft '{dispute_letter.subject}' was saved.",
        organization_id=dispute_letter.organization_id,
        case_id=dispute_letter.case_id,
        account_id=dispute_letter.account_id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "dispute_letter_id": str(dispute_letter.id),
            "template_id": dispute_letter.template_id,
            "status": (
                dispute_letter.status.value
                if hasattr(dispute_letter.status, "value")
                else dispute_letter.status
            ),
        },
    )


def dispute_letter_approved_event(
    dispute_letter: DisputeLetter,
    performed_by: uuid.UUID,
) -> PlatformEvent:
    return PlatformEvent(
        event_type="DISPUTE_LETTER_APPROVED",
        event_category=EventCategory.ACCOUNT.value,
        title="Dispute letter approved",
        description=f"Dispute letter '{dispute_letter.subject}' was approved for sending.",
        organization_id=dispute_letter.organization_id,
        case_id=dispute_letter.case_id,
        account_id=dispute_letter.account_id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "dispute_letter_id": str(dispute_letter.id),
            "template_id": dispute_letter.template_id,
            "status": (
                dispute_letter.status.value
                if hasattr(dispute_letter.status, "value")
                else dispute_letter.status
            ),
        },
    )


def dispute_letter_sent_event(
    dispute_letter: DisputeLetter,
    performed_by: uuid.UUID,
) -> PlatformEvent:
    return PlatformEvent(
        event_type="DISPUTE_LETTER_SENT",
        event_category=EventCategory.ACCOUNT.value,
        title="Dispute letter sent",
        description=f"Dispute letter '{dispute_letter.subject}' was marked as sent.",
        organization_id=dispute_letter.organization_id,
        case_id=dispute_letter.case_id,
        account_id=dispute_letter.account_id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "dispute_letter_id": str(dispute_letter.id),
            "template_id": dispute_letter.template_id,
            "status": (
                dispute_letter.status.value
                if hasattr(dispute_letter.status, "value")
                else dispute_letter.status
            ),
            "sent_at": dispute_letter.sent_at.isoformat() if dispute_letter.sent_at else None,
        },
    )


def dispute_letter_voided_event(
    dispute_letter: DisputeLetter,
    performed_by: uuid.UUID,
) -> PlatformEvent:
    return PlatformEvent(
        event_type="DISPUTE_LETTER_VOIDED",
        event_category=EventCategory.ACCOUNT.value,
        title="Dispute letter voided",
        description=f"Dispute letter '{dispute_letter.subject}' was voided.",
        organization_id=dispute_letter.organization_id,
        case_id=dispute_letter.case_id,
        account_id=dispute_letter.account_id,
        performed_by=performed_by,
        source_module="accounts",
        metadata={
            "dispute_letter_id": str(dispute_letter.id),
            "template_id": dispute_letter.template_id,
            "status": (
                dispute_letter.status.value
                if hasattr(dispute_letter.status, "value")
                else dispute_letter.status
            ),
        },
    )


def document_uploaded_event(document: Document, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=DocumentEventType.DOCUMENT_UPLOADED.value,
        event_category=EventCategory.DOCUMENT.value,
        title="Document uploaded",
        description=f"Document '{document.title}' was uploaded.",
        organization_id=document.organization_id,
        case_id=document.case_id,
        account_id=document.account_id,
        document_id=document.id,
        performed_by=performed_by,
        source_module="documents",
        metadata={"file_name": document.file_name, "mime_type": document.mime_type},
    )


def document_version_created_event(document: Document, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=DocumentEventType.DOCUMENT_VERSION_CREATED.value,
        event_category=EventCategory.DOCUMENT.value,
        title="Document version created",
        description=f"New version v{document.version_number} uploaded for '{document.title}'.",
        organization_id=document.organization_id,
        case_id=document.case_id,
        account_id=document.account_id,
        document_id=document.id,
        performed_by=performed_by,
        source_module="documents",
        metadata={"version_number": document.version_number, "file_name": document.file_name},
    )


def document_pipeline_event(
    document: Document,
    event_type: DocumentEventType,
    *,
    title: str,
    description: str,
    performed_by: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
    source_module: str = "documents",
) -> PlatformEvent:
    return PlatformEvent(
        event_type=event_type.value,
        event_category=EventCategory.DOCUMENT.value,
        title=title,
        description=description,
        organization_id=document.organization_id,
        case_id=document.case_id,
        account_id=document.account_id,
        document_id=document.id,
        performed_by=performed_by,
        source_module=source_module,
        metadata=metadata or {},
    )


def user_login_event(user: User) -> PlatformEvent:
    if user.organization_id is None:
        raise ValueError("Cannot publish login event without organization_id")
    return PlatformEvent(
        event_type=AuthEventType.USER_LOGIN.value,
        event_category=EventCategory.AUTH.value,
        title="User signed in",
        description=f"{user.email} signed in.",
        organization_id=user.organization_id,
        performed_by=user.id,
        source_module="auth",
        metadata={"email": user.email, "role": user.role.value},
    )


def is_case_closed_status(status: CaseStatus) -> bool:
    return status in (CaseStatus.CLOSED, CaseStatus.RESOLVED)


def _task_event_metadata(task: Task) -> dict[str, str | None]:
    return {
        "status": task.status.value if hasattr(task.status, "value") else task.status,
        "priority": task.priority.value if hasattr(task.priority, "value") else task.priority,
        "title": task.title,
    }


def task_created_event(task: Task, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=TaskEventType.TASK_CREATED.value,
        event_category=EventCategory.TASK.value,
        title="Task created",
        description=f"Task '{task.title}' was created.",
        organization_id=task.organization_id,
        case_id=task.case_id,
        account_id=task.account_id,
        document_id=task.document_id,
        performed_by=performed_by,
        source_module="tasks",
        metadata=_task_event_metadata(task),
    )


def task_updated_event(task: Task, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=TaskEventType.TASK_UPDATED.value,
        event_category=EventCategory.TASK.value,
        title="Task updated",
        description=f"Task '{task.title}' was updated.",
        organization_id=task.organization_id,
        case_id=task.case_id,
        account_id=task.account_id,
        document_id=task.document_id,
        performed_by=performed_by,
        source_module="tasks",
        metadata=_task_event_metadata(task),
    )


def task_completed_event(task: Task, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=TaskEventType.TASK_COMPLETED.value,
        event_category=EventCategory.TASK.value,
        title="Task completed",
        description=f"Task '{task.title}' was completed.",
        organization_id=task.organization_id,
        case_id=task.case_id,
        account_id=task.account_id,
        document_id=task.document_id,
        performed_by=performed_by,
        source_module="tasks",
        metadata=_task_event_metadata(task),
    )


def task_reopened_event(task: Task, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=TaskEventType.TASK_REOPENED.value,
        event_category=EventCategory.TASK.value,
        title="Task reopened",
        description=f"Task '{task.title}' was reopened.",
        organization_id=task.organization_id,
        case_id=task.case_id,
        account_id=task.account_id,
        document_id=task.document_id,
        performed_by=performed_by,
        source_module="tasks",
        metadata=_task_event_metadata(task),
    )


def task_deleted_event(task: Task, performed_by: uuid.UUID) -> PlatformEvent:
    return PlatformEvent(
        event_type=TaskEventType.TASK_DELETED.value,
        event_category=EventCategory.TASK.value,
        title="Task deleted",
        description=f"Task '{task.title}' was deleted.",
        organization_id=task.organization_id,
        case_id=task.case_id,
        account_id=task.account_id,
        document_id=task.document_id,
        performed_by=performed_by,
        source_module="tasks",
        metadata=_task_event_metadata(task),
    )
