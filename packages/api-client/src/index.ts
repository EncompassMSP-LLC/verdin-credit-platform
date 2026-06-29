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
  deleteAccount,
  getAccount,
  getAccountIntelligenceSummary,
  listAccounts,
  listCaseAccounts,
  updateAccount,
  type Account,
  type AccountIntelligenceSummary,
  type CreateAccountInput,
  type ListAccountsParams,
  type NextActionItem,
  type UpdateAccountInput,
} from './accounts';

export {
  confirmDocumentResolution,
  deleteDocument,
  extractDocumentMetadata,
  getDocument,
  getDocumentDownloadUrl,
  getDocumentMetadata,
  getDocumentOcr,
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
  type DocumentEntityResolution,
  type DocumentMetadata,
  type DocumentOcrResult,
  type DocumentResolutions,
  type DocumentVersion,
  type ListDocumentsParams,
  type UpdateDocumentInput,
  type UploadDocumentInput,
} from './documents';

export { getTask, listTasks, type ListTasksParams, type Task } from './tasks';

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
