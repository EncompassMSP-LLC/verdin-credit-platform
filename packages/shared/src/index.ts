export const APP_NAME = 'Verdin Credit Platform';
export const APP_VERSION = '4.2.0';

export type UserRole = 'owner' | 'admin' | 'case_manager' | 'reviewer' | 'read_only';

export const USER_ROLES: UserRole[] = ['owner', 'admin', 'case_manager', 'reviewer', 'read_only'];

export const ROLE_LABELS: Record<UserRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  case_manager: 'Case Manager',
  reviewer: 'Reviewer',
  read_only: 'Read Only',
};

export type CaseStatus = 'open' | 'active' | 'on_hold' | 'resolved' | 'closed';

export type CaseStage =
  | 'intake'
  | 'review'
  | 'evidence_gathering'
  | 'dispute_preparation'
  | 'awaiting_response'
  | 'monitoring'
  | 'complete';

export type CasePriority = 'low' | 'medium' | 'high' | 'critical';

export const CASE_STATUSES: CaseStatus[] = ['open', 'active', 'on_hold', 'resolved', 'closed'];

export const CASE_STAGES: CaseStage[] = [
  'intake',
  'review',
  'evidence_gathering',
  'dispute_preparation',
  'awaiting_response',
  'monitoring',
  'complete',
];

export const CASE_PRIORITIES: CasePriority[] = ['low', 'medium', 'high', 'critical'];

export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  open: 'Open',
  active: 'Active',
  on_hold: 'On Hold',
  resolved: 'Resolved',
  closed: 'Closed',
};

export const CASE_STAGE_LABELS: Record<CaseStage, string> = {
  intake: 'Intake',
  review: 'Review',
  evidence_gathering: 'Evidence Gathering',
  dispute_preparation: 'Dispute Preparation',
  awaiting_response: 'Awaiting Response',
  monitoring: 'Monitoring',
  complete: 'Complete',
};

export const CASE_PRIORITY_LABELS: Record<CasePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export type AccountBureau = 'equifax' | 'experian' | 'transunion' | 'innovis' | 'unknown';

export type AccountType =
  | 'mortgage'
  | 'auto'
  | 'credit_card'
  | 'collection'
  | 'personal_loan'
  | 'student_loan'
  | 'medical'
  | 'utility'
  | 'telecom'
  | 'other';

export type AccountStatus =
  | 'open'
  | 'closed'
  | 'collection'
  | 'charge_off'
  | 'repossession'
  | 'foreclosure'
  | 'transferred'
  | 'paid'
  | 'settled'
  | 'deleted'
  | 'unknown';

export type PaymentStatus =
  | 'current'
  | 'late_30'
  | 'late_60'
  | 'late_90'
  | 'late_120'
  | 'charge_off'
  | 'collection'
  | 'repossession'
  | 'foreclosure'
  | 'unknown';

export type DisputeStatus =
  | 'not_started'
  | 'evidence_needed'
  | 'ready_for_dispute'
  | 'dispute_sent'
  | 'awaiting_response'
  | 'verified'
  | 'corrected'
  | 'deleted'
  | 'escalated'
  | 'monitoring';

export type InvestigationStatus = 'none' | 'pending' | 'completed' | 'overdue' | 'escalated';

export const ACCOUNT_BUREAUS: AccountBureau[] = [
  'equifax',
  'experian',
  'transunion',
  'innovis',
  'unknown',
];

export const ACCOUNT_TYPES: AccountType[] = [
  'mortgage',
  'auto',
  'credit_card',
  'collection',
  'personal_loan',
  'student_loan',
  'medical',
  'utility',
  'telecom',
  'other',
];

export const ACCOUNT_STATUSES: AccountStatus[] = [
  'open',
  'closed',
  'collection',
  'charge_off',
  'repossession',
  'foreclosure',
  'transferred',
  'paid',
  'settled',
  'deleted',
  'unknown',
];

export const PAYMENT_STATUSES: PaymentStatus[] = [
  'current',
  'late_30',
  'late_60',
  'late_90',
  'late_120',
  'charge_off',
  'collection',
  'repossession',
  'foreclosure',
  'unknown',
];

export const DISPUTE_STATUSES: DisputeStatus[] = [
  'not_started',
  'evidence_needed',
  'ready_for_dispute',
  'dispute_sent',
  'awaiting_response',
  'verified',
  'corrected',
  'deleted',
  'escalated',
  'monitoring',
];

export const BUREAU_LABELS: Record<AccountBureau, string> = {
  equifax: 'Equifax',
  experian: 'Experian',
  transunion: 'TransUnion',
  innovis: 'Innovis',
  unknown: 'Unknown',
};

export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  mortgage: 'Mortgage',
  auto: 'Auto',
  credit_card: 'Credit Card',
  collection: 'Collection',
  personal_loan: 'Personal Loan',
  student_loan: 'Student Loan',
  medical: 'Medical',
  utility: 'Utility',
  telecom: 'Telecom',
  other: 'Other',
};

export const ACCOUNT_STATUS_LABELS: Record<AccountStatus, string> = {
  open: 'Open',
  closed: 'Closed',
  collection: 'Collection',
  charge_off: 'Charge Off',
  repossession: 'Repossession',
  foreclosure: 'Foreclosure',
  transferred: 'Transferred',
  paid: 'Paid',
  settled: 'Settled',
  deleted: 'Deleted',
  unknown: 'Unknown',
};

export const PAYMENT_STATUS_LABELS: Record<PaymentStatus, string> = {
  current: 'Current',
  late_30: '30 Days Late',
  late_60: '60 Days Late',
  late_90: '90 Days Late',
  late_120: '120+ Days Late',
  charge_off: 'Charge Off',
  collection: 'Collection',
  repossession: 'Repossession',
  foreclosure: 'Foreclosure',
  unknown: 'Unknown',
};

export const DISPUTE_STATUS_LABELS: Record<DisputeStatus, string> = {
  not_started: 'Not Started',
  evidence_needed: 'Evidence Needed',
  ready_for_dispute: 'Ready for Dispute',
  dispute_sent: 'Dispute Sent',
  awaiting_response: 'Awaiting Response',
  verified: 'Verified',
  corrected: 'Corrected',
  deleted: 'Deleted',
  escalated: 'Escalated',
  monitoring: 'Monitoring',
};

export type TaskStatus = 'open' | 'in_progress' | 'blocked' | 'completed' | 'canceled';

export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

export const TASK_STATUSES: TaskStatus[] = [
  'open',
  'in_progress',
  'blocked',
  'completed',
  'canceled',
];

export const TASK_PRIORITIES: TaskPriority[] = ['low', 'medium', 'high', 'critical'];

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  open: 'Open',
  in_progress: 'In Progress',
  blocked: 'Blocked',
  completed: 'Completed',
  canceled: 'Canceled',
};

export const TASK_PRIORITY_LABELS: Record<TaskPriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export type DocumentProcessingStatus =
  'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'skipped';

export const DOCUMENT_PROCESSING_STATUSES: DocumentProcessingStatus[] = [
  'pending',
  'queued',
  'processing',
  'completed',
  'failed',
  'skipped',
];

export const DOCUMENT_PROCESSING_STATUS_LABELS: Record<DocumentProcessingStatus, string> = {
  pending: 'Pending',
  queued: 'Queued',
  processing: 'Processing',
  completed: 'OCR Complete',
  failed: 'OCR Failed',
  skipped: 'Not applicable',
};

export type MetadataStatus = 'pending' | 'extracted' | 'failed';

export const METADATA_STATUSES: MetadataStatus[] = ['pending', 'extracted', 'failed'];

export const METADATA_STATUS_LABELS: Record<MetadataStatus, string> = {
  pending: 'Pending',
  extracted: 'Extracted',
  failed: 'Failed',
};

export type ResolutionStatus = 'matched' | 'ambiguous' | 'unmatched' | 'confirmed' | 'rejected';

export const RESOLUTION_STATUSES: ResolutionStatus[] = [
  'matched',
  'ambiguous',
  'unmatched',
  'confirmed',
  'rejected',
];

export const RESOLUTION_STATUS_LABELS: Record<ResolutionStatus, string> = {
  matched: 'Matched',
  ambiguous: 'Needs review',
  unmatched: 'Unmatched',
  confirmed: 'Confirmed',
  rejected: 'Rejected',
};

export type MatchedEntityType = 'case' | 'account' | 'organization' | 'person';

export const MATCHED_ENTITY_TYPE_LABELS: Record<MatchedEntityType, string> = {
  case: 'Case',
  account: 'Account',
  organization: 'Organization',
  person: 'Person',
};

export type ExtractionMethod = 'rules' | 'ai' | 'parser';
export type ResolutionMethod = 'rules' | 'manual' | 'ai';
