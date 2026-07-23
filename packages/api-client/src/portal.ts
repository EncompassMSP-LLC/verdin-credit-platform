import {
  ApiClientError,
  apiPath,
  getAccessToken,
  getApiBaseUrl,
  request,
  uploadRequest,
} from './http';
import type { ConsentRecord, ConsentDocumentTemplateKey, ConsentType } from './compliance';
import type {
  ConfirmIdentityTheftAccountRequest,
  IdentityTheftAccountReview,
  IdentityTheftCaseCenter,
} from './documents';

export interface PortalLoginInput {
  email: string;
  password: string;
}

export interface PortalTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PortalMeResponse {
  id: string;
  organization_id: string;
  client_id: string;
  email: string;
  client_display_name: string;
  is_active: boolean;
  last_login_at: string | null;
}

export type PortalCaseStatus = 'open' | 'active' | 'on_hold' | 'resolved' | 'closed';
export type PortalCaseStage =
  | 'intake'
  | 'review'
  | 'evidence_gathering'
  | 'dispute_preparation'
  | 'awaiting_response'
  | 'monitoring'
  | 'complete';

export interface PortalCaseSummary {
  id: string;
  case_number: string | null;
  title: string;
  status: PortalCaseStatus;
  stage: PortalCaseStage;
  opened_at: string;
  closed_at: string | null;
  updated_at: string;
}

export interface PortalCaseDetail extends PortalCaseSummary {
  dispute_accounts: Record<string, number>;
  account_count: number;
}

export interface PortalCaseProgressResponse {
  items: PortalCaseSummary[];
}

export interface PortalDocument {
  id: string;
  case_id: string;
  title: string;
  description: string | null;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  processing_status: string;
  created_at: string;
}

export interface PortalCaseDocumentsResponse {
  items: PortalDocument[];
}

export interface UploadPortalCaseDocumentInput {
  file: File | Blob;
  title: string;
  description?: string | null;
}

export type PortalMessageSenderRole = 'portal_client' | 'staff';

export interface PortalThreadMessage {
  id: string;
  thread_id: string;
  sender_role: PortalMessageSenderRole;
  portal_user_id: string | null;
  staff_user_id: string | null;
  body: string;
  created_at: string;
}

export interface PortalCaseMessageThread {
  case_id: string;
  thread_id: string | null;
  client_id: string | null;
  status: 'open' | 'closed' | null;
  messages: PortalThreadMessage[];
}

export interface SendPortalMessageInput {
  body: string;
}

export interface ClientPortalUser {
  id: string;
  organization_id: string;
  client_id: string;
  email: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProvisionPortalUserInput {
  email: string;
  password: string;
}

export interface UpdatePortalUserInput {
  email?: string;
  password?: string;
  is_active?: boolean;
}

export async function portalLogin(input: PortalLoginInput): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/login'), {
    method: 'POST',
    body: input,
    auth: false,
  });
}

export async function portalRefresh(refreshToken: string): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/refresh'), {
    method: 'POST',
    body: { refresh_token: refreshToken },
    auth: false,
  });
}

export async function getPortalMe(): Promise<PortalMeResponse> {
  return request<PortalMeResponse>(apiPath('/portal/auth/me'));
}

export async function listPortalCases(): Promise<PortalCaseProgressResponse> {
  return request<PortalCaseProgressResponse>(apiPath('/portal/cases'));
}

export async function getPortalCase(caseId: string): Promise<PortalCaseDetail> {
  return request<PortalCaseDetail>(apiPath(`/portal/cases/${caseId}`));
}

export async function listPortalCaseDocuments(
  caseId: string,
): Promise<PortalCaseDocumentsResponse> {
  return request<PortalCaseDocumentsResponse>(apiPath(`/portal/cases/${caseId}/documents`));
}

export async function uploadPortalCaseDocument(
  caseId: string,
  input: UploadPortalCaseDocumentInput,
): Promise<PortalDocument> {
  const form = new FormData();
  form.append('file', input.file);
  form.append('title', input.title);
  if (input.description) form.append('description', input.description);
  return uploadRequest<PortalDocument>(apiPath(`/portal/cases/${caseId}/documents`), form);
}

export interface PortalConsentRequirement {
  template_key: ConsentDocumentTemplateKey;
  consent_type: ConsentType;
  label: string;
  title: string;
  is_signed: boolean;
  consent_id: string | null;
  legal_review_status: string;
}

export interface PortalCaseConsentsResponse {
  items: PortalConsentRequirement[];
  legal_review_notice: string;
}

export interface SignPortalConsentInput {
  template_key: ConsentDocumentTemplateKey;
  signer_name: string;
  attestation_accepted: boolean;
  signature_file?: File | null;
}

export function getPortalConsentPreviewUrl(
  caseId: string,
  templateKey: ConsentDocumentTemplateKey,
): string {
  return apiPath(`/portal/cases/${caseId}/consents/${templateKey}/preview`);
}

export async function downloadPortalConsentPreview(
  caseId: string,
  templateKey: ConsentDocumentTemplateKey,
): Promise<{ blob: Blob; filename: string }> {
  const url = `${getApiBaseUrl()}${getPortalConsentPreviewUrl(caseId, templateKey)}`;
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as { detail?: string; code?: string };
    throw new ApiClientError(
      error.detail || `HTTP ${response.status}`,
      response.status,
      error.code,
    );
  }

  const disposition = response.headers.get('content-disposition');
  const match = disposition ? /filename="([^"]+)"/.exec(disposition) : null;
  const filename = match?.[1] ?? `consent-preview-${templateKey}.pdf`;
  return { blob: await response.blob(), filename };
}

export async function listPortalCaseConsents(caseId: string): Promise<PortalCaseConsentsResponse> {
  return request<PortalCaseConsentsResponse>(apiPath(`/portal/cases/${caseId}/consents`));
}

export async function getPortalIdentityTheftCenter(
  caseId: string,
): Promise<IdentityTheftCaseCenter> {
  return request<IdentityTheftCaseCenter>(apiPath(`/portal/cases/${caseId}/identity-theft-center`));
}

export async function confirmPortalIdentityTheftAccount(
  caseId: string,
  body: ConfirmIdentityTheftAccountRequest,
): Promise<IdentityTheftAccountReview> {
  return request<IdentityTheftAccountReview>(
    apiPath(`/portal/cases/${caseId}/identity-theft/account-reviews`),
    { method: 'POST', body },
  );
}

export async function signPortalCaseConsent(
  caseId: string,
  input: SignPortalConsentInput,
): Promise<ConsentRecord> {
  const form = new FormData();
  form.append('template_key', input.template_key);
  form.append('signer_name', input.signer_name);
  form.append('attestation_accepted', String(input.attestation_accepted));
  if (input.signature_file) form.append('signature_file', input.signature_file);
  return uploadRequest<ConsentRecord>(apiPath(`/portal/cases/${caseId}/consents/sign`), form);
}

export async function listPortalCaseMessages(caseId: string): Promise<PortalCaseMessageThread> {
  return request<PortalCaseMessageThread>(apiPath(`/portal/cases/${caseId}/messages`));
}

export async function sendPortalCaseMessage(
  caseId: string,
  input: SendPortalMessageInput,
): Promise<PortalThreadMessage> {
  return request<PortalThreadMessage>(apiPath(`/portal/cases/${caseId}/messages`), {
    method: 'POST',
    body: input,
  });
}

export interface PortalPushStatus {
  enabled: boolean;
  ready: boolean;
  provider: string;
  vapid_public_key: string | null;
  blockers: string[];
  active_subscription_count: number;
}

export interface PortalPushSubscribeInput {
  endpoint: string;
  p256dh_key: string;
  auth_key: string;
  user_agent?: string | null;
}

export interface PortalPushSubscription {
  id: string;
  endpoint: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export async function getPortalPushStatus(): Promise<PortalPushStatus> {
  return request<PortalPushStatus>(apiPath('/portal/push/status'));
}

export async function subscribePortalPush(
  input: PortalPushSubscribeInput,
): Promise<PortalPushSubscription> {
  return request<PortalPushSubscription>(apiPath('/portal/push/subscribe'), {
    method: 'POST',
    body: input,
  });
}

export async function unsubscribePortalPush(subscriptionId: string): Promise<void> {
  await request<void>(apiPath(`/portal/push/subscriptions/${subscriptionId}`), {
    method: 'DELETE',
  });
}

export interface PortalReadinessDimension {
  key: string;
  label: string;
  score: number;
  weight: number;
}

export interface PortalReadinessBlocker {
  id: string;
  title: string;
  impact: string;
  action: string;
}

export interface PortalReadinessAccount {
  id: string;
  creditor_label: string;
  bureau: string;
  readiness_score: number | null;
  risk_score: number | null;
  dispute_status: string;
  recommended_action: string | null;
}

export interface PortalCaseReadiness {
  case_id: string;
  overall: number;
  band: string;
  updated_at: string;
  trend: number | null;
  disclaimer: string;
  dimensions: PortalReadinessDimension[];
  blockers: PortalReadinessBlocker[];
  accounts: PortalReadinessAccount[];
}

export interface PortalInsightItem {
  id: string;
  title: string;
  summary: string;
  confidence: number;
  actions: string[];
  source: string;
}

export interface PortalCaseInsights {
  case_id: string;
  disclaimer: string;
  items: PortalInsightItem[];
}

export type PortalChecklistStatus = 'open' | 'done';
export type PortalChecklistPriority = 'high' | 'medium' | 'low';

export interface PortalChecklistItem {
  id: string;
  case_id: string;
  title: string;
  category: string;
  priority: PortalChecklistPriority;
  status: PortalChecklistStatus;
  due_date: string | null;
  sort_order: number;
  updated_at: string;
}

export interface PortalChecklistResponse {
  case_id: string;
  items: PortalChecklistItem[];
}

export interface PortalLearningModule {
  id: string;
  title: string;
  minutes: number;
  level: string;
  summary: string;
  completed: boolean;
  completed_at: string | null;
}

export interface PortalLearningModulesResponse {
  items: PortalLearningModule[];
}

export async function getPortalCaseReadiness(caseId: string): Promise<PortalCaseReadiness> {
  return request<PortalCaseReadiness>(apiPath(`/portal/cases/${caseId}/readiness`));
}

export async function getPortalCaseInsights(caseId: string): Promise<PortalCaseInsights> {
  return request<PortalCaseInsights>(apiPath(`/portal/cases/${caseId}/insights`));
}

export interface PortalCreditAnalysis {
  run_id: string;
  case_id: string;
  generated_at: string;
  borrower_readiness: {
    overall?: number;
    band?: string;
    product_name?: string;
    dimensions?: Array<{ key: string; label: string; score: number; weight: number }>;
    disclaimer?: string;
  };
  mortgage_readiness: {
    overall?: number;
    band?: string;
    estimated_ready_weeks?: number;
    blockers?: Array<{ title: string; impact: string; action: string }>;
    disclaimer?: string;
  };
  borrower_action_plan: {
    title?: string;
    items?: Array<{ priority: string; title: string; action: string }>;
    disclaimer?: string;
  };
  dispute_recommendations: {
    title?: string;
    items: Array<{
      creditor?: string;
      bureau?: string;
      recommended_action?: string;
      priority?: string;
    }>;
    disclaimer?: string;
  };
  timeline: Array<{ at: string; type: string; title: string; detail: string }>;
  audit_summary: Record<string, number>;
  compliance_summary: {
    metro2_total: number;
    fcra_total: number;
    identity_theft_total: number;
  };
  disclaimer: string;
}

export async function getPortalCaseCreditAnalysis(caseId: string): Promise<PortalCreditAnalysis> {
  return request<PortalCreditAnalysis>(apiPath(`/portal/cases/${caseId}/credit-analysis`));
}

export async function listPortalCaseChecklist(caseId: string): Promise<PortalChecklistResponse> {
  return request<PortalChecklistResponse>(apiPath(`/portal/cases/${caseId}/checklist`));
}

export async function updatePortalChecklistItem(
  itemId: string,
  status: PortalChecklistStatus,
): Promise<PortalChecklistItem> {
  return request<PortalChecklistItem>(apiPath(`/portal/checklist/${itemId}`), {
    method: 'PATCH',
    body: { status },
  });
}

export async function listPortalLearningModules(): Promise<PortalLearningModulesResponse> {
  return request<PortalLearningModulesResponse>(apiPath('/portal/learning/modules'));
}

export async function completePortalLearningModule(
  moduleId: string,
): Promise<PortalLearningModule> {
  return request<PortalLearningModule>(apiPath(`/portal/learning/modules/${moduleId}/complete`), {
    method: 'POST',
  });
}

export async function reopenPortalLearningModule(moduleId: string): Promise<PortalLearningModule> {
  return request<PortalLearningModule>(apiPath(`/portal/learning/modules/${moduleId}/reopen`), {
    method: 'POST',
  });
}

export async function provisionClientPortalUser(
  clientId: string,
  input: ProvisionPortalUserInput,
): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`), {
    method: 'POST',
    body: input,
  });
}

export async function getClientPortalUser(clientId: string): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`));
}

export async function updateClientPortalUser(
  clientId: string,
  input: UpdatePortalUserInput,
): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`), {
    method: 'PATCH',
    body: input,
  });
}

export async function revokeClientPortalUser(clientId: string): Promise<void> {
  await request<void>(apiPath(`/clients/${clientId}/portal-user`), { method: 'DELETE' });
}
