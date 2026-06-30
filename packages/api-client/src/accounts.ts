import type {
  AccountBureau,
  AccountStatus,
  AccountType,
  DisputeStatus,
  PaginatedResponse,
  PaymentStatus,
} from '@verdin/shared';

import type { Task } from './tasks';
import { apiPath, request } from './http';

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
}

export interface AccountDisputeDraft {
  account_id: string;
  case_id: string;
  bureau: AccountBureau;
  recipient_type: 'credit_bureau';
  template_id: string;
  subject: string;
  body: string;
  disputed_items: string[];
  requested_action: string;
  evidence_checklist: string[];
  compliance_notes: string[];
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

export async function getAccountDisputeDraft(accountId: string): Promise<AccountDisputeDraft> {
  return request<AccountDisputeDraft>(apiPath(`/accounts/${accountId}/dispute-draft`));
}

export async function createAccountDisputeDraftReviewTask(accountId: string): Promise<Task> {
  return request<Task>(apiPath(`/accounts/${accountId}/dispute-draft/review-task`), {
    method: 'POST',
  });
}

export async function createAccountDisputeLetterDraft(accountId: string): Promise<DisputeLetter> {
  return request<DisputeLetter>(apiPath(`/accounts/${accountId}/dispute-draft/letters`), {
    method: 'POST',
  });
}

export async function listAccountDisputeLetters(accountId: string): Promise<DisputeLetter[]> {
  return request<DisputeLetter[]>(apiPath(`/accounts/${accountId}/dispute-letters`));
}

export async function createAccountDisputeLetterReviewTask(
  accountId: string,
  letterId: string,
): Promise<Task> {
  return request<Task>(apiPath(`/accounts/${accountId}/dispute-letters/${letterId}/review-task`), {
    method: 'POST',
  });
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

export async function getAccountIntelligenceSummary(
  caseId?: string,
): Promise<AccountIntelligenceSummary> {
  const query = caseId ? `?case_id=${caseId}` : '';
  return request<AccountIntelligenceSummary>(
    `${apiPath('/accounts/intelligence/summary')}${query}`,
  );
}
