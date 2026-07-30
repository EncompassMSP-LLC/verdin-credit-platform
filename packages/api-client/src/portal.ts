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
  /** Partnership display name when a referral exists (Vol 19 P2-3). */
  referring_partner_name?: string | null;
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

export type MessageAttachmentScanStatus = 'pending' | 'clean' | 'rejected' | 'failed';

export interface MessageAttachment {
  id: string;
  message_id: string | null;
  document_id: string;
  display_filename: string;
  mime_type: string;
  byte_size: number;
  scan_status: MessageAttachmentScanStatus;
  scan_detail: string | null;
  downloadable: boolean;
  created_at: string;
}

export interface PortalThreadMessage {
  id: string;
  thread_id: string;
  sender_role: PortalMessageSenderRole;
  portal_user_id: string | null;
  staff_user_id: string | null;
  body: string;
  created_at: string;
  attachments?: MessageAttachment[];
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
  attachment_ids?: string[];
  idempotency_key?: string;
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
  invitation_pending?: boolean;
}

export interface ClientPortalInviteActionResponse extends ClientPortalUser {
  detail: string;
  invitation_queued: boolean;
  invite_token?: string | null;
}

export interface ProvisionPortalUserInput {
  email: string;
  password?: string;
  send_invite?: boolean;
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

export interface PortalPasswordResetRequestResponse {
  detail: string;
  reset_token?: string | null;
}

export async function portalForgotPassword(
  email: string,
): Promise<PortalPasswordResetRequestResponse> {
  return request<PortalPasswordResetRequestResponse>(apiPath('/portal/auth/forgot-password'), {
    method: 'POST',
    body: { email },
    auth: false,
  });
}

export async function portalResetPassword(input: {
  token: string;
  password: string;
}): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/reset-password'), {
    method: 'POST',
    body: input,
    auth: false,
  });
}

export async function portalAcceptInvite(input: {
  token: string;
  password: string;
}): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/accept-invite'), {
    method: 'POST',
    body: input,
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

export async function uploadPortalMessageAttachment(
  caseId: string,
  file: File | Blob,
  filename?: string,
): Promise<MessageAttachment> {
  const form = new FormData();
  form.append('file', file, filename);
  return uploadRequest<MessageAttachment>(
    apiPath(`/portal/cases/${caseId}/messages/attachments`),
    form,
  );
}

export async function deletePortalMessageAttachment(
  caseId: string,
  attachmentId: string,
): Promise<void> {
  await request<void>(apiPath(`/portal/cases/${caseId}/messages/attachments/${attachmentId}`), {
    method: 'DELETE',
  });
}

export function portalMessageAttachmentDownloadUrl(caseId: string, attachmentId: string): string {
  return apiPath(`/portal/cases/${caseId}/messages/attachments/${attachmentId}/download`);
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
  description?: string | null;
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

export interface PortalReadinessReport {
  case_id: string;
  credit_analysis_run_id: string;
  band: string;
  updated_at: string;
  generated_at: string;
  reports_evaluated: number;
  tradelines_evaluated: number;
  formula_version: string;
  score_version: string;
  disclaimer: string;
  dimensions: Array<{ key?: string; label?: string; score?: number; weight?: number }>;
  blockers: Array<{ id?: string; title?: string; impact?: string; action?: string }>;
}

export async function getPortalCaseReadinessReport(caseId: string): Promise<PortalReadinessReport> {
  return request<PortalReadinessReport>(apiPath(`/portal/cases/${caseId}/readiness-report`));
}

export type PortalTimelineEventType = 'case' | 'readiness' | 'document' | 'task';

export interface PortalTimelineItem {
  id: string;
  event_at: string;
  event_type: PortalTimelineEventType | string;
  title: string;
  detail: string | null;
  href: string | null;
}

export interface PortalTimelineResponse {
  case_id: string;
  items: PortalTimelineItem[];
}

export async function getPortalCaseTimeline(
  caseId: string,
  options?: { event_type?: PortalTimelineEventType | string },
): Promise<PortalTimelineResponse> {
  const params = new URLSearchParams();
  if (options?.event_type) {
    params.set('event_type', options.event_type);
  }
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return request<PortalTimelineResponse>(apiPath(`/portal/cases/${caseId}/timeline${suffix}`));
}

export interface PortalDisputeStrategyStageSuggestion {
  stage_kind: string;
  title: string;
  objective: string;
  recommended: boolean;
}

export interface PortalDisputeStrategyAccountSuggestion {
  creditor_label: string;
  account_number_masked: string | null;
  summary: string;
  recommended_stage_titles: string[];
  stages: PortalDisputeStrategyStageSuggestion[];
}

export interface PortalDisputeStrategySuggestionsSummary {
  accounts_planned: number;
  issues_covered: number;
  high_strength_accounts: number;
  cfpb_recommended: number;
  attorney_recommended: number;
}

export interface PortalDisputeStrategySuggestions {
  case_id: string;
  disclaimer: string;
  staff_mediated: boolean;
  auto_send: boolean;
  source: 'staff_run' | 'none' | string;
  generated_at: string | null;
  summary: PortalDisputeStrategySuggestionsSummary;
  suggestions: PortalDisputeStrategyAccountSuggestion[];
}

export async function getPortalDisputeStrategySuggestions(
  caseId: string,
): Promise<PortalDisputeStrategySuggestions> {
  return request<PortalDisputeStrategySuggestions>(
    apiPath(`/portal/cases/${caseId}/dispute-strategy-suggestions`),
  );
}

export function getPortalCaseReadinessReportExportUrl(
  caseId: string,
  format: 'text' | 'pdf' = 'pdf',
): string {
  return apiPath(`/portal/cases/${caseId}/readiness-report/export?format=${format}`);
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

export type PortalNotificationCategory = 'system' | 'task' | 'dispute' | 'document' | 'workflow';

export interface PortalNotification {
  id: string;
  title: string;
  body: string | null;
  category: PortalNotificationCategory;
  read_at: string | null;
  entity_type: string | null;
  entity_id: string | null;
  action_url: string | null;
  created_at: string;
}

export interface ListPortalNotificationsParams {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
  category?: PortalNotificationCategory;
  sort_by?: 'created_at' | 'read_at';
  sort_order?: 'asc' | 'desc';
}

export interface PortalUnreadCountResponse {
  unread_count: number;
}

function buildPortalNotificationQuery(params: ListPortalNotificationsParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function listPortalNotifications(params: ListPortalNotificationsParams = {}) {
  return request<{
    items: PortalNotification[];
    total: number;
    page: number;
    page_size: number;
    pages: number;
  }>(apiPath(`/portal/notifications${buildPortalNotificationQuery(params)}`));
}

export function getPortalUnreadNotificationCount() {
  return request<PortalUnreadCountResponse>(apiPath('/portal/notifications/unread-count'));
}

export function markPortalNotificationRead(notificationId: string) {
  return request<PortalNotification>(apiPath(`/portal/notifications/${notificationId}/read`), {
    method: 'POST',
  });
}

export function markAllPortalNotificationsRead() {
  return request<PortalUnreadCountResponse>(apiPath('/portal/notifications/mark-all-read'), {
    method: 'POST',
  });
}

export async function provisionClientPortalUser(
  clientId: string,
  input: ProvisionPortalUserInput,
): Promise<ClientPortalInviteActionResponse> {
  return request<ClientPortalInviteActionResponse>(apiPath(`/clients/${clientId}/portal-user`), {
    method: 'POST',
    body: input,
  });
}

export async function resendClientPortalInvite(
  clientId: string,
): Promise<ClientPortalInviteActionResponse> {
  return request<ClientPortalInviteActionResponse>(
    apiPath(`/clients/${clientId}/portal-user/resend-invite`),
    { method: 'POST' },
  );
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
