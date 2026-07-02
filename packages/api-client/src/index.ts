import { apiPath, request } from './http';

export {
  ApiClientError,
  ApiNotImplementedError,
  apiPath,
  configureApiClient,
  getAccessToken,
  getApiBaseUrl,
  notImplemented,
  request,
  setAccessToken,
  uploadRequest,
  type ApiClientConfig,
  type RequestOptions,
} from './http';

export {
  getCurrentUser,
  login,
  refreshToken,
  type LoginRequest,
  type RefreshTokenRequest,
  type TokenResponse,
  type User,
} from './auth';

export {
  getDashboard,
  type DashboardAccounts,
  type DashboardAlertItem,
  type DashboardAlerts,
  type DashboardAlertSeverity,
  type DashboardAlertType,
  type DashboardCases,
  type DashboardDocuments,
  type DashboardOperations,
  type DashboardOverview,
  type DashboardPerformance,
  type DashboardProcessing,
  type DashboardResponse,
  type DashboardTasks,
  type DashboardTimelineItem,
} from './dashboard';

export {
  getOperationsReporting,
  type ClientReportingMetrics,
  type NotificationReportingMetrics,
  type OperationsReporting,
  type OperationsReportingResponse,
} from './reporting';

export {
  createCase,
  deleteCase,
  getCase,
  listCases,
  updateCase,
  type Case,
  type CreateCaseInput,
  type ListCasesParams,
  type UpdateCaseInput,
} from './cases';

export {
  createClient,
  createClientContact,
  deleteClient,
  deleteClientContact,
  getClient,
  getClientContact,
  listClientContacts,
  listClients,
  updateClient,
  updateClientContact,
  type Client,
  type ClientContact,
  type ClientStatus,
  type ContactRelationship,
  type CreateClientContactInput,
  type CreateClientInput,
  type ListClientContactsParams,
  type ListClientsParams,
  type UpdateClientContactInput,
  type UpdateClientInput,
} from './clients';

export { getLlmStatus, type LlmGateStatus } from './llm';

export {
  createAccount,
  createAccountDisputeDraftReviewTask,
  createAccountDisputeLetterDraft,
  createAccountDisputeLetterReviewTask,
  approveAccountDisputeLetter,
  sendAccountDisputeLetter,
  voidAccountDisputeLetter,
  deleteAccount,
  getAccount,
  getAccountDisputeDraft,
  getAccountIntelligenceSummary,
  listAccountDisputeLetters,
  getAccountDisputeLetter,
  downloadAccountDisputeLetterExport,
  markAccountAwaitingDisputeResponse,
  markAccountDisputeResponseReceived,
  escalateAccountOverdueInvestigation,
  listAccounts,
  listCaseAccounts,
  updateAccount,
  type Account,
  type AccountDisputeDraft,
  type DisputeReasonSuggestion,
  type DisputeRecipientType,
  type DisputeResponseOutcome,
  type MissingEvidenceItem,
  type AccountIntelligenceSummary,
  type CreateAccountInput,
  type DisputeLetter,
  type DisputeLetterExportFormat,
  type DisputeLetterStatus,
  type ListAccountsParams,
  type NextActionItem,
  type UpdateAccountInput,
} from './accounts';

export {
  compareDocumentParsedCreditReport,
  confirmDocumentResolution,
  createDocumentParsedCreditReportReviewTask,
  deleteDocument,
  extractDocumentMetadata,
  getDocument,
  getDocumentDuplicateGroup,
  getDocumentDownloadUrl,
  getDocumentMetadata,
  getDocumentOcr,
  getDocumentParsedCreditReportAccountCandidates,
  getDocumentParsedCreditReport,
  getDocumentResolutions,
  listDocumentVersions,
  listDocuments,
  rejectDocumentResolution,
  resolveDocumentEntities,
  retryDocumentOcr,
  updateDocument,
  uploadDocument,
  uploadDocumentVersion,
  type Document,
  type DocumentDuplicateGroup,
  type DocumentEntityResolution,
  type DocumentMetadata,
  type DocumentOcrResult,
  type DocumentParsedCreditReportAccountCandidates,
  type DocumentParsedCreditReport,
  type DocumentParsedCreditReportComparison,
  type DocumentResolutions,
  type DocumentVersion,
  type ListDocumentsParams,
  type ParsedReportAccountChange,
  type ParsedReportAccountCandidate,
  type ParsedReportComparisonSummary,
  type UpdateDocumentInput,
  type UploadDocumentInput,
} from './documents';

export {
  completeTask,
  createTask,
  deleteTask,
  getTask,
  listTasks,
  reopenTask,
  updateTask,
  type CreateTaskInput,
  type ListTasksParams,
  type Task,
  type UpdateTaskInput,
} from './tasks';

export {
  getTimelineEvent,
  listTimelineEvents,
  type ListTimelineParams,
  type TimelineEvent,
} from './timeline';

export {
  createNotification,
  getNotificationEmailDeliveryStatus,
  getUnreadNotificationCount,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type CreateNotificationInput,
  type EmailDeliveryStatus,
  type ListNotificationsParams,
  type Notification,
  type NotificationCategory,
  type UnreadCountResponse,
} from './notifications';

export {
  getPortalCase,
  getPortalMe,
  listPortalCases,
  portalLogin,
  portalRefresh,
  provisionClientPortalUser,
  getClientPortalUser,
  updateClientPortalUser,
  revokeClientPortalUser,
  type ClientPortalUser,
  type PortalCaseDetail,
  type PortalCaseProgressResponse,
  type PortalCaseStage,
  type PortalCaseStatus,
  type PortalCaseSummary,
  type PortalLoginInput,
  type PortalMeResponse,
  type PortalTokenResponse,
  type ProvisionPortalUserInput,
  type UpdatePortalUserInput,
} from './portal';

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}

export interface VersionResponse {
  version: string;
  name: string;
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>(apiPath('/health'), { auth: false });
}

export async function getVersion(): Promise<VersionResponse> {
  return request<VersionResponse>(apiPath('/version'), { auth: false });
}
