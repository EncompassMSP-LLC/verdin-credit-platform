import type {
  AccountBureau,
  AccountStatus,
  AccountType,
  DisputeStatus,
  PaginatedResponse,
  PaymentStatus,
} from '@verdin/shared';

import type { Task } from './tasks';
import { ApiClientError, apiPath, getAccessToken, getApiBaseUrl, request } from './http';

export interface Account {
  id: string;
  organization_id: string;
  case_id: string;
  bureau: AccountBureau;
  creditor_name: string;
  original_creditor: string | null;
  account_number_masked: string | null;
  account_type: AccountType;
  account_status: AccountStatus;
  payment_status: PaymentStatus;
  balance: string | null;
  high_balance: string | null;
  credit_limit: string | null;
  monthly_payment: string | null;
  past_due_amount: string | null;
  date_opened: string | null;
  date_reported: string | null;
  date_last_activity: string | null;
  date_first_delinquency: string | null;
  estimated_removal_date: string | null;
  responsibility: string | null;
  remarks: string | null;
  dispute_status: DisputeStatus;
  dispute_round: number;
  investigation_status: string;
  last_dispute_date: string | null;
  next_eligible_dispute_date: string | null;
  response_received: boolean;
  cra_dispute: boolean;
  furnisher_dispute: boolean;
  cfpb_dispute: boolean;
  ai_summary: string | null;
  ai_recommended_next_action: string | null;
  risk_score: number | null;
  readiness_score: number | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateAccountInput {
  case_id: string;
  bureau?: AccountBureau;
  creditor_name: string;
  original_creditor?: string | null;
  account_number_masked?: string | null;
  account_type?: AccountType;
  account_status?: AccountStatus;
  payment_status?: PaymentStatus;
  balance?: string | null;
  high_balance?: string | null;
  credit_limit?: string | null;
  monthly_payment?: string | null;
  past_due_amount?: string | null;
  date_opened?: string | null;
  date_reported?: string | null;
  remarks?: string | null;
  dispute_status?: DisputeStatus;
}

export interface UpdateAccountInput {
  bureau?: AccountBureau;
  creditor_name?: string;
  original_creditor?: string | null;
  account_number_masked?: string | null;
  account_type?: AccountType;
  account_status?: AccountStatus;
  payment_status?: PaymentStatus;
  balance?: string | null;
  past_due_amount?: string | null;
  remarks?: string | null;
  dispute_status?: DisputeStatus;
}

export interface ListAccountsParams {
  page?: number;
  page_size?: number;
  search?: string;
  case_id?: string;
  client_id?: string;
  bureau?: AccountBureau;
  account_type?: AccountType;
  account_status?: AccountStatus;
  payment_status?: PaymentStatus;
  dispute_status?: DisputeStatus;
  min_risk_score?: number;
  max_risk_score?: number;
  min_readiness_score?: number;
  dispute_ready?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface NextActionItem {
  account_id: string;
  case_id: string;
  creditor_name: string;
  bureau: AccountBureau;
  dispute_status: DisputeStatus;
  risk_score: number | null;
  readiness_score: number | null;
  recommended_action: string;
}

export interface CrossBureauIntelligenceSummary {
  available: boolean;
  reports_compared: string[];
  actionable_discrepancies: number;
  dispute_ready_discrepancies: number;
  investigation_needed: number;
  consistent_tradelines: number;
  total_tradelines: number;
}

export interface AccountIntelligenceSummary {
  total_accounts: number;
  total_balance: string;
  collection_count: number;
  charge_off_count: number;
  critical_accounts: number;
  dispute_ready_count: number;
  evidence_needed_count: number;
  total_past_due: string;
  accounts_by_bureau: Record<string, number>;
  accounts_by_type: Record<string, number>;
  accounts_by_status: Record<string, number>;
  highest_balance_accounts: Account[];
  highest_risk_accounts: Account[];
  next_action_queue: NextActionItem[];
  scoring_model: 'heuristic' | 'calibrated';
  cross_bureau: CrossBureauIntelligenceSummary | null;
}

export interface AccountLlmRecommendation {
  account_id: string;
  recommendation: string;
  provider: string;
  model: string;
  prompt_hash: string;
  pii_scrubbed: boolean;
  generated_at: string;
  cross_bureau_informed: boolean;
}

export interface DisputeReasonSuggestion {
  code: string;
  category: 'accuracy' | 'completeness' | 'verification';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  requires_evidence: string[];
}

export interface MissingEvidenceItem {
  code: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  checklist_item: string | null;
}

export type DisputeRecipientType = 'credit_bureau' | 'furnisher';

export interface AccountDisputeDraft {
  account_id: string;
  case_id: string;
  bureau: AccountBureau;
  recipient_type: DisputeRecipientType;
  template_id: string;
  subject: string;
  body: string;
  disputed_items: string[];
  dispute_reason_suggestions: DisputeReasonSuggestion[];
  requested_action: string;
  evidence_checklist: string[];
  compliance_notes: string[];
  evidence_ready: boolean;
  missing_evidence: MissingEvidenceItem[];
  generated_by: 'rules';
  readiness_score: number | null;
  risk_score: number | null;
}

export type DisputeLetterStatus = 'draft' | 'review' | 'approved' | 'sent' | 'void';

export interface DisputeLetter {
  id: string;
  organization_id: string;
  case_id: string;
  account_id: string;
  recipient_type: string;
  status: DisputeLetterStatus;
  template_id: string;
  subject: string;
  body: string;
  disputed_items: string[];
  requested_action: string;
  evidence_checklist: string[];
  compliance_notes: string[];
  generated_by: string;
  generated_at: string;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

function buildQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function createAccount(input: CreateAccountInput): Promise<Account> {
  return request<Account>(apiPath('/accounts'), { method: 'POST', body: input });
}

export async function listAccounts(
  params: ListAccountsParams = {},
): Promise<PaginatedResponse<Account>> {
  return request<PaginatedResponse<Account>>(
    `${apiPath('/accounts')}${buildQuery(params as Record<string, unknown>)}`,
  );
}

export async function getAccount(accountId: string): Promise<Account> {
  return request<Account>(apiPath(`/accounts/${accountId}`));
}

export async function getAccountDisputeDraft(
  accountId: string,
  recipientType: DisputeRecipientType = 'credit_bureau',
): Promise<AccountDisputeDraft> {
  return request<AccountDisputeDraft>(
    `${apiPath(`/accounts/${accountId}/dispute-draft`)}${buildQuery({ recipient_type: recipientType })}`,
  );
}

export async function createAccountDisputeDraftReviewTask(accountId: string): Promise<Task> {
  return request<Task>(apiPath(`/accounts/${accountId}/dispute-draft/review-task`), {
    method: 'POST',
  });
}

export async function createAccountDisputeLetterDraft(
  accountId: string,
  recipientType: DisputeRecipientType = 'credit_bureau',
): Promise<DisputeLetter> {
  return request<DisputeLetter>(
    `${apiPath(`/accounts/${accountId}/dispute-draft/letters`)}${buildQuery({ recipient_type: recipientType })}`,
    { method: 'POST' },
  );
}

export async function listAccountDisputeLetters(accountId: string): Promise<DisputeLetter[]> {
  return request<DisputeLetter[]>(apiPath(`/accounts/${accountId}/dispute-letters`));
}

export async function getAccountDisputeLetter(
  accountId: string,
  letterId: string,
): Promise<DisputeLetter> {
  return request<DisputeLetter>(apiPath(`/accounts/${accountId}/dispute-letters/${letterId}`));
}

export type DisputeLetterExportFormat =
  'text' | 'pdf' | 'mail-letter' | 'mail-label' | 'mail-packet' | 'report-excerpt';

function parseContentDispositionFilename(header: string | null, fallback: string): string {
  if (!header) return fallback;
  const match = /filename="([^"]+)"/.exec(header);
  return match?.[1] ?? fallback;
}

export async function downloadAccountDisputeLetterExport(
  accountId: string,
  letterId: string,
  format: DisputeLetterExportFormat,
): Promise<{ blob: Blob; filename: string }> {
  const url = `${getApiBaseUrl()}${apiPath(
    `/accounts/${accountId}/dispute-letters/${letterId}/export`,
  )}?format=${format}`;
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

  const fallback =
    format === 'text'
      ? 'dispute-letter.txt'
      : format === 'mail-packet'
        ? 'mail-packet.pdf'
        : format === 'mail-label'
          ? 'dispute-mail-label.pdf'
          : format === 'mail-letter'
            ? 'dispute-mail-letter.pdf'
            : 'dispute-letter.pdf';
  const filename = parseContentDispositionFilename(
    response.headers.get('Content-Disposition'),
    fallback,
  );
  return { blob: await response.blob(), filename };
}

export async function createAccountDisputeLetterReviewTask(
  accountId: string,
  letterId: string,
): Promise<Task> {
  return request<Task>(apiPath(`/accounts/${accountId}/dispute-letters/${letterId}/review-task`), {
    method: 'POST',
  });
}

export async function approveAccountDisputeLetter(
  accountId: string,
  letterId: string,
): Promise<DisputeLetter> {
  return request<DisputeLetter>(
    apiPath(`/accounts/${accountId}/dispute-letters/${letterId}/approve`),
    { method: 'POST' },
  );
}

export async function sendAccountDisputeLetter(
  accountId: string,
  letterId: string,
): Promise<DisputeLetter> {
  return request<DisputeLetter>(
    apiPath(`/accounts/${accountId}/dispute-letters/${letterId}/send`),
    { method: 'POST' },
  );
}

export async function voidAccountDisputeLetter(
  accountId: string,
  letterId: string,
): Promise<DisputeLetter> {
  return request<DisputeLetter>(
    apiPath(`/accounts/${accountId}/dispute-letters/${letterId}/void`),
    { method: 'POST' },
  );
}

export type DisputeResponseOutcome = 'verified' | 'corrected' | 'deleted';

export async function markAccountAwaitingDisputeResponse(accountId: string): Promise<Account> {
  return request<Account>(apiPath(`/accounts/${accountId}/dispute-awaiting-response`), {
    method: 'POST',
  });
}

export async function markAccountDisputeResponseReceived(
  accountId: string,
  outcome: DisputeResponseOutcome,
): Promise<Account> {
  return request<Account>(apiPath(`/accounts/${accountId}/dispute-response-received`), {
    method: 'POST',
    body: { outcome },
  });
}

export async function escalateAccountOverdueInvestigation(accountId: string): Promise<Account> {
  return request<Account>(apiPath(`/accounts/${accountId}/dispute-investigation-overdue`), {
    method: 'POST',
  });
}

export type DisputeResponseRecordOutcome =
  'deleted' | 'verified' | 'updated' | 'corrected' | 'no_response' | 'rejected';

export type DisputeResponseMethod = 'mail' | 'portal' | 'phone' | 'email' | 'other';

export interface DisputeResponseRecord {
  id: string;
  organization_id: string;
  case_id: string;
  account_id: string;
  dispute_letter_id: string | null;
  document_id: string | null;
  outcome: DisputeResponseRecordOutcome;
  response_method: DisputeResponseMethod;
  response_date: string | null;
  recorded_at: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  created_by_id: string | null;
}

export interface RecordDisputeResponseInput {
  outcome: DisputeResponseRecordOutcome;
  response_method?: DisputeResponseMethod;
  dispute_letter_id?: string | null;
  document_id?: string | null;
  response_date?: string | null;
  notes?: string | null;
}

export async function recordAccountDisputeResponse(
  accountId: string,
  input: RecordDisputeResponseInput,
): Promise<DisputeResponseRecord> {
  return request<DisputeResponseRecord>(apiPath(`/accounts/${accountId}/dispute-responses`), {
    method: 'POST',
    body: input,
  });
}

export async function listAccountDisputeResponses(
  accountId: string,
): Promise<DisputeResponseRecord[]> {
  return request<DisputeResponseRecord[]>(apiPath(`/accounts/${accountId}/dispute-responses`));
}

export type ReinvestigationClockState =
  'not_sent' | 'awaiting' | 'due_soon' | 'overdue' | 'responded';

export interface AccountReinvestigationClock {
  account_id: string;
  creditor_name: string;
  dispute_status: DisputeStatus;
  last_dispute_date: string | null;
  deadline: string | null;
  days_remaining: number | null;
  state: ReinvestigationClockState;
  response_received: boolean;
  response_count: number;
}

export interface CaseReinvestigationClockSummary {
  not_sent: number;
  awaiting: number;
  due_soon: number;
  overdue: number;
  responded: number;
}

export interface CaseReinvestigationClock {
  case_id: string;
  generated_at: string;
  summary: CaseReinvestigationClockSummary;
  accounts: AccountReinvestigationClock[];
}

export async function getCaseReinvestigationClock(
  caseId: string,
): Promise<CaseReinvestigationClock> {
  return request<CaseReinvestigationClock>(
    apiPath(`/accounts/reinvestigation-clock${buildQuery({ case_id: caseId })}`),
  );
}

export type RedisputeAction =
  'wait' | 'prepare_initial' | 'redispute' | 'escalate_cfpb' | 'escalate_attorney' | 'resolved';

export type RedisputePriority = 'high' | 'medium' | 'low';

export interface AccountRedisputeReadiness {
  account_id: string;
  creditor_name: string;
  dispute_status: DisputeStatus;
  clock_state: ReinvestigationClockState;
  latest_outcome: DisputeResponseRecordOutcome | null;
  dispute_round: number;
  risk_score: number | null;
  action: RedisputeAction;
  priority: RedisputePriority;
  reason: string;
}

export interface CaseRedisputeReadinessSummary {
  wait: number;
  prepare_initial: number;
  redispute: number;
  escalate_cfpb: number;
  escalate_attorney: number;
  resolved: number;
  high_priority: number;
}

export interface CaseRedisputeReadiness {
  case_id: string;
  generated_at: string;
  summary: CaseRedisputeReadinessSummary;
  accounts: AccountRedisputeReadiness[];
}

export async function getCaseRedisputeReadiness(caseId: string): Promise<CaseRedisputeReadiness> {
  return request<CaseRedisputeReadiness>(
    apiPath(`/accounts/redispute-readiness${buildQuery({ case_id: caseId })}`),
  );
}

export interface CaseReinvestigationSummary {
  case_id: string;
  generated_at: string;
  total_accounts: number;
  disputed_accounts: number;
  total_responses: number;
  clock: CaseReinvestigationClockSummary;
  readiness: CaseRedisputeReadinessSummary;
  next_deadline: string | null;
  next_deadline_account_id: string | null;
  next_deadline_creditor: string | null;
  most_overdue_days: number | null;
  action_items: AccountRedisputeReadiness[];
}

export async function getCaseReinvestigationSummary(
  caseId: string,
): Promise<CaseReinvestigationSummary> {
  return request<CaseReinvestigationSummary>(
    apiPath(`/accounts/reinvestigation-summary${buildQuery({ case_id: caseId })}`),
  );
}

export type LlmDisputeDraftAugmentStatusValue = 'completed' | 'failed';

export interface LlmDisputeDraftAugment {
  id: string;
  organization_id: string;
  account_id: string;
  case_id: string;
  recipient_type: string;
  base_template_id: string;
  base_subject: string;
  base_body: string;
  augmented_body: string | null;
  status: LlmDisputeDraftAugmentStatusValue;
  provider: string | null;
  model: string | null;
  prompt_hash: string | null;
  requested_by_user_id: string | null;
  requested_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  pii_scrubbed: boolean;
}

export interface LlmDisputeDraftAugmentInput {
  recipient_type?: 'credit_bureau' | 'furnisher';
}

export function listAccountDisputeDraftLlmAugments(
  accountId: string,
  params: { page?: number; page_size?: number } = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<LlmDisputeDraftAugment>>(
    apiPath(`/accounts/${accountId}/dispute-draft/llm-augments${query ? `?${query}` : ''}`),
  );
}

export function createAccountDisputeDraftLlmAugment(
  accountId: string,
  input: LlmDisputeDraftAugmentInput = {},
) {
  return request<LlmDisputeDraftAugment>(
    apiPath(`/accounts/${accountId}/dispute-draft/llm-augment`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export async function updateAccount(
  accountId: string,
  input: UpdateAccountInput,
): Promise<Account> {
  return request<Account>(apiPath(`/accounts/${accountId}`), { method: 'PATCH', body: input });
}

export async function deleteAccount(accountId: string): Promise<void> {
  await request<void>(apiPath(`/accounts/${accountId}`), { method: 'DELETE' });
}

export async function listCaseAccounts(
  caseId: string,
  params: ListAccountsParams = {},
): Promise<PaginatedResponse<Account>> {
  return request<PaginatedResponse<Account>>(
    `${apiPath(`/cases/${caseId}/accounts`)}${buildQuery(params as Record<string, unknown>)}`,
  );
}

export async function listClientAccounts(
  clientId: string,
  params: ListAccountsParams = {},
): Promise<PaginatedResponse<Account>> {
  return request<PaginatedResponse<Account>>(
    `${apiPath(`/clients/${clientId}/accounts`)}${buildQuery(params as Record<string, unknown>)}`,
  );
}

export async function getAccountIntelligenceSummary(
  caseId?: string,
): Promise<AccountIntelligenceSummary> {
  const query = caseId ? `?case_id=${caseId}` : '';
  return request<AccountIntelligenceSummary>(
    `${apiPath('/accounts/intelligence/summary')}${query}`,
  );
}

export async function generateAccountLlmRecommendation(
  accountId: string,
): Promise<AccountLlmRecommendation> {
  return request<AccountLlmRecommendation>(apiPath(`/accounts/${accountId}/llm-recommendation`), {
    method: 'POST',
  });
}
