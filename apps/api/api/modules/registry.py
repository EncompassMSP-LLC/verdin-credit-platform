"""Register all ORM models with SQLAlchemy metadata."""

from api.core.constants import UserRole
from api.modules.accounts.autonomous_bureau_filing_models import (
    AutonomousBureauFilingRun,
    AutonomousBureauFilingRunStatus,
)
from api.modules.accounts.bureau_live_api_models import BureauLiveApiRun, BureauLiveApiRunStatus
from api.modules.accounts.bureau_refiling_models import BureauRefilingRun, BureauRefilingRunStatus
from api.modules.accounts.bureau_unsupervised_refiling_models import (
    BureauUnsupervisedRefilingRun,
    BureauUnsupervisedRefilingRunStatus,
)
from api.modules.accounts.dispute_bureau_submission_models import (
    DisputeBureauSubmissionRun,
    DisputeBureauSubmissionStatus,
)
from api.modules.accounts.dispute_draft_augment_models import LlmDisputeDraftAugment
from api.modules.accounts.dispute_filing_prep_models import (
    DisputeFilingPrepRun,
    DisputeFilingPrepStatus,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.models import Account
from api.modules.auth.models import Organization, User
from api.modules.billing.collection_models import (
    BillingInvoiceCollectionRun,
    BillingInvoiceCollectionRunKind,
    BillingInvoiceCollectionRunStatus,
    BillingInvoiceCollectionTriggerSource,
)
from api.modules.billing.invoice_pdf_models import StripeInvoicePdfRun, StripeInvoicePdfRunStatus
from api.modules.billing.invoicing_models import (
    BillingInvoicingRun,
    BillingInvoicingRunKind,
    BillingInvoicingRunStatus,
    BillingInvoicingTriggerSource,
)
from api.modules.billing.models import BillingWebhookEvent, OrganizationBillingAccount
from api.modules.billing.stripe_charge_retry_models import (
    StripeChargeRetryRun,
    StripeChargeRetryRunStatus,
)
from api.modules.billing.stripe_live_charge_retry_execution_models import (
    StripeLiveChargeRetryExecutionRun,
    StripeLiveChargeRetryExecutionRunStatus,
)
from api.modules.billing.stripe_live_tax_api_models import (
    StripeLiveTaxApiRun,
    StripeLiveTaxApiRunStatus,
)
from api.modules.billing.tax_calculation_models import (
    StripeTaxCalculationRun,
    StripeTaxCalculationRunStatus,
)
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
from api.modules.documents.batch_summary_models import (
    BatchDocumentSummaryRun,
    BatchSummaryRunStatus,
    BatchSummaryTriggerSource,
)
from api.modules.documents.models import Document
from api.modules.enterprise.bulk_idp_provisioning_models import (
    BulkIdpProvisioningRun,
    BulkIdpProvisioningRunStatus,
)
from api.modules.enterprise.federation_metadata_models import (
    SamlFederationMetadataUpload,
    SamlMetadataValidationStatus,
)
from api.modules.enterprise.federation_models import (
    IdpFederationProvider,
    IdpFederationProviderType,
)
from api.modules.enterprise.hris_lifecycle_models import (
    HrisLifecycleSyncRun,
    HrisLifecycleSyncRunStatus,
)
from api.modules.enterprise.hris_passwordless_ui_models import (
    HrisPasswordlessUiRun,
    HrisPasswordlessUiRunStatus,
)
from api.modules.enterprise.models import UserSsoEnrollment, UserTotpEnrollment
from api.modules.enterprise.saml_automated_rotation_models import (
    SamlAutomatedRotationRun,
    SamlAutomatedRotationRunStatus,
)
from api.modules.enterprise.saml_cert_rotation_models import (
    SamlCertificateRotationRun,
    SamlCertificateRotationStatus,
)
from api.modules.enterprise.saml_passwordless_enrollment_models import (
    SamlPasswordlessEnrollmentRun,
    SamlPasswordlessEnrollmentRunStatus,
)
from api.modules.llm.agent_execution_models import (
    AgentExecutionStep,
    AgentExecutionStepStatus,
)
from api.modules.llm.agent_observability_models import (
    AgentObservabilityKind,
    AgentObservabilityRun,
    AgentObservabilityRunStatus,
    AgentObservabilityTriggerSource,
)
from api.modules.llm.agent_supervised_loop_models import (
    AgentSupervisedLoopRun,
    AgentSupervisedLoopStatus,
)
from api.modules.llm.agent_tool_calling_models import (
    AgentExternalToolKind,
    AgentToolInvocationRequest,
    AgentToolInvocationStatus,
)
from api.modules.llm.agent_unsupervised_loop_models import (
    AgentUnsupervisedLoopRun,
    AgentUnsupervisedLoopStatus,
)
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
from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
    SmsMarketingTriggerSource,
)
from api.modules.org_admin.models import (
    ApiKeyScope,
    OAuthDeveloperApp,
    OAuthDeveloperAppStatus,
    OrganizationApiKey,
)
from api.modules.org_admin.rotation_models import ApiKeyRotationLog
from api.modules.reporting.cross_org_benchmark_models import (
    CrossOrgBenchmarkRun,
    CrossOrgBenchmarkRunStatus,
    CrossOrgBenchmarkTriggerSource,
)
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
    "AgentExecutionStep",
    "AgentExecutionStepStatus",
    "AgentExternalToolKind",
    "AgentSupervisedLoopRun",
    "AgentSupervisedLoopStatus",
    "AgentUnsupervisedLoopRun",
    "AgentUnsupervisedLoopStatus",
    "AgentToolInvocationRequest",
    "AgentToolInvocationStatus",
    "AgentObservabilityKind",
    "AgentObservabilityRun",
    "AgentObservabilityRunStatus",
    "AgentObservabilityTriggerSource",
    "ApiKeyRotationLog",
    "ApiKeyScope",
    "OAuthDeveloperApp",
    "OAuthDeveloperAppStatus",
    "BillingInvoiceCollectionRun",
    "BillingInvoiceCollectionRunKind",
    "BillingInvoiceCollectionRunStatus",
    "BillingInvoiceCollectionTriggerSource",
    "StripeInvoicePdfRun",
    "StripeInvoicePdfRunStatus",
    "StripeLiveTaxApiRun",
    "StripeLiveTaxApiRunStatus",
    "StripeChargeRetryRun",
    "StripeChargeRetryRunStatus",
    "StripeLiveChargeRetryExecutionRun",
    "StripeLiveChargeRetryExecutionRunStatus",
    "StripeTaxCalculationRun",
    "StripeTaxCalculationRunStatus",
    "BillingInvoicingRun",
    "BillingInvoicingRunKind",
    "BillingInvoicingRunStatus",
    "BillingInvoicingTriggerSource",
    "BillingWebhookEvent",
    "AutonomousBureauFilingRun",
    "AutonomousBureauFilingRunStatus",
    "BureauRefilingRun",
    "BureauRefilingRunStatus",
    "BureauUnsupervisedRefilingRun",
    "BureauUnsupervisedRefilingRunStatus",
    "BureauLiveApiRun",
    "BureauLiveApiRunStatus",
    "Case",
    "CaseStatus",
    "BatchDocumentSummaryRun",
    "BatchSummaryRunStatus",
    "BatchSummaryTriggerSource",
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
    "DisputeFilingPrepRun",
    "DisputeFilingPrepStatus",
    "DisputeBureauSubmissionRun",
    "DisputeBureauSubmissionStatus",
    "EmailDeliveryLog",
    "EnforcementRunStatus",
    "EnforcementTriggerSource",
    "IdpFederationProvider",
    "IdpFederationProviderType",
    "LlmDisputeDraftAugment",
    "HrisLifecycleSyncRun",
    "HrisLifecycleSyncRunStatus",
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
    "CrossOrgBenchmarkRun",
    "CrossOrgBenchmarkRunStatus",
    "CrossOrgBenchmarkTriggerSource",
    "PredictiveOutcomeRefreshRun",
    "PredictiveOutcomeRefreshStatus",
    "PredictiveOutcomeSnapshot",
    "PredictiveOutcomeTriggerSource",
    "RetentionPolicy",
    "RetentionEnforcementRun",
    "RetentionScope",
    "SamlFederationMetadataUpload",
    "SamlMetadataValidationStatus",
    "SamlAutomatedRotationRun",
    "SamlAutomatedRotationRunStatus",
    "SamlPasswordlessEnrollmentRun",
    "SamlPasswordlessEnrollmentRunStatus",
    "HrisPasswordlessUiRun",
    "HrisPasswordlessUiRunStatus",
    "BulkIdpProvisioningRun",
    "BulkIdpProvisioningRunStatus",
    "SamlCertificateRotationRun",
    "SamlCertificateRotationStatus",
    "SmsDeliveryLog",
    "SmsMarketingCampaignRun",
    "SmsMarketingCampaignStatus",
    "SmsMarketingTriggerSource",
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
