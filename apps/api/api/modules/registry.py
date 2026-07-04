"""Register all ORM models with SQLAlchemy metadata."""

from api.core.constants import UserRole
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.billing.models import BillingWebhookEvent, OrganizationBillingAccount
from api.modules.cases.models import Case, CaseStatus
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.push_models import (
    PortalPushDeliveryLog,
    PortalPushDeliveryStatus,
    PortalPushSubscription,
)
from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship
from api.modules.compliance.models import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    EnforcementRunStatus,
    EnforcementTriggerSource,
    RetentionEnforcementRun,
    RetentionPolicy,
    RetentionScope,
)
from api.modules.documents.models import Document
from api.modules.enterprise.models import UserSsoEnrollment, UserTotpEnrollment
from api.modules.messaging.models import (
    MessageSenderRole,
    MessageThread,
    MessageThreadStatus,
    ThreadMessage,
)
from api.modules.notifications.models import (
    EmailDeliveryLog,
    Notification,
    NotificationCategory,
    SmsDeliveryLog,
)
from api.modules.org_admin.models import ApiKeyScope, OrganizationApiKey
from api.modules.org_admin.rotation_models import ApiKeyRotationLog
from api.modules.reporting.materialized_models import (
    ReportingMvRefreshRun,
    ReportingMvRefreshStatus,
    ReportingMvTriggerSource,
)
from api.modules.reporting.predictive_models import (
    PredictiveOutcomeRefreshRun,
    PredictiveOutcomeRefreshStatus,
    PredictiveOutcomeSnapshot,
    PredictiveOutcomeTriggerSource,
)
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import Communication, TimelineEvent

__all__ = [
    "Account",
    "ApiKeyRotationLog",
    "ApiKeyScope",
    "BillingWebhookEvent",
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
    "EnforcementRunStatus",
    "EnforcementTriggerSource",
    "MessageSenderRole",
    "MessageThread",
    "MessageThreadStatus",
    "Notification",
    "NotificationCategory",
    "Organization",
    "OrganizationApiKey",
    "OrganizationBillingAccount",
    "PortalPushDeliveryLog",
    "PortalPushDeliveryStatus",
    "PortalPushSubscription",
    "ReportingMvRefreshRun",
    "ReportingMvRefreshStatus",
    "ReportingMvTriggerSource",
    "PredictiveOutcomeRefreshRun",
    "PredictiveOutcomeRefreshStatus",
    "PredictiveOutcomeSnapshot",
    "PredictiveOutcomeTriggerSource",
    "RetentionPolicy",
    "RetentionEnforcementRun",
    "RetentionScope",
    "SmsDeliveryLog",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "ThreadMessage",
    "TimelineEvent",
    "User",
    "UserRole",
    "UserSsoEnrollment",
    "UserTotpEnrollment",
]
