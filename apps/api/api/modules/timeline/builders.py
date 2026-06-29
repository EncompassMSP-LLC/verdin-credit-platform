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
)

from api.modules.accounts.models import Account
from api.modules.auth.models import User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.models import Document


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
