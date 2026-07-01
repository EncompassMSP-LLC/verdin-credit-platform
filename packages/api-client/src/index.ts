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
  type DashboardOverview,
  type DashboardPerformance,
  type DashboardProcessing,
  type DashboardResponse,
  type DashboardTasks,
  type DashboardTimelineItem,
} from './dashboard';

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
  markAccountAwaitingDisputeResponse,
  markAccountDisputeResponseReceived,
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
