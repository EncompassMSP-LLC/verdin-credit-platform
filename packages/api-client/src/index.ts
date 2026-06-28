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

export { getCase, listCases, type Case, type ListCasesParams } from './cases';

export { getAccount, listAccounts, type Account, type ListAccountsParams } from './accounts';

export { getDocument, listDocuments, type Document, type ListDocumentsParams } from './documents';

export { getTask, listTasks, type ListTasksParams, type Task } from './tasks';

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
