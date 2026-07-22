/** Enterprise CRM domain types — shaped for future platform partner / CRM APIs. */

export type CrmRole =
  | 'crm_admin'
  | 'partner_manager'
  | 'loan_officer'
  | 'realtor_liaison'
  | 'ops_coordinator'
  | 'read_only';

export type CrmPermission =
  | 'dashboard.view'
  | 'partners.view'
  | 'partners.manage'
  | 'borrowers.view'
  | 'borrowers.manage'
  | 'lenders.view'
  | 'lenders.manage'
  | 'realtors.view'
  | 'realtors.manage'
  | 'tasks.view'
  | 'tasks.manage'
  | 'workflow.view'
  | 'workflow.manage'
  | 'pipeline.view'
  | 'pipeline.manage'
  | 'automations.view'
  | 'automations.manage'
  | 'sms.view'
  | 'sms.send'
  | 'email.view'
  | 'email.send'
  | 'reporting.view'
  | 'reporting.export'
  | 'referrals.view'
  | 'referrals.manage'
  | 'calendar.view'
  | 'calendar.manage'
  | 'documents.view'
  | 'documents.manage'
  | 'notes.view'
  | 'notes.manage'
  | 'admin.manage'
  | 'permissions.manage';

export type PartnerType = 'lender' | 'realtor' | 'broker' | 'operator' | 'other';
export type PartnerStatus = 'prospect' | 'active' | 'paused' | 'churned';

export type PipelineStage =
  | 'lead'
  | 'qualified'
  | 'referred'
  | 'intake'
  | 'in_repair'
  | 'near_ready'
  | 'mortgage_ready'
  | 'in_underwriting'
  | 'funded'
  | 'lost';

export type TaskStatus = 'open' | 'in_progress' | 'blocked' | 'done' | 'canceled';
export type TaskPriority = 'low' | 'normal' | 'high' | 'urgent';

export type AutomationTrigger =
  | 'stage_enter'
  | 'referral_created'
  | 'task_overdue'
  | 'score_band_change'
  | 'document_uploaded'
  | 'manual';

export type ChannelStatus = 'queued' | 'sent' | 'delivered' | 'failed' | 'opened' | 'replied';

export interface CrmUser {
  id: string;
  email: string;
  displayName: string;
  role: CrmRole;
  organizationId: string;
  organizationName: string;
  title: string;
}

export interface RoleDefinition {
  role: CrmRole;
  label: string;
  description: string;
  permissions: CrmPermission[];
}

export interface PartnerOrg {
  id: string;
  name: string;
  type: PartnerType;
  status: PartnerStatus;
  primaryContact: string;
  email: string;
  phone: string;
  market: string;
  activeReferrals: number;
  fundedYtd: number;
  ownerName: string;
  lastActivityAt: string;
  notes: string;
}

export interface BorrowerRecord {
  id: string;
  displayName: string;
  email: string;
  phone: string;
  stage: PipelineStage;
  readinessScore: number;
  readinessBand: string;
  lenderId: string | null;
  lenderName: string | null;
  realtorId: string | null;
  realtorName: string | null;
  partnerId: string | null;
  loName: string;
  estimatedReadyDate: string | null;
  progressPct: number;
  loanGoal: string;
  source: string;
  lastActivityAt: string;
  blockers: string[];
}

export interface LenderContact {
  id: string;
  organizationId: string;
  organizationName: string;
  displayName: string;
  email: string;
  phone: string;
  title: string;
  nmls: string | null;
  activeBorrowers: number;
  openReferrals: number;
  market: string;
  status: 'active' | 'inactive';
}

export interface RealtorContact {
  id: string;
  brokerage: string;
  displayName: string;
  email: string;
  phone: string;
  market: string;
  activeBorrowers: number;
  openReferrals: number;
  status: 'active' | 'inactive';
  preferredLender: string | null;
}

export interface CrmTask {
  id: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueAt: string | null;
  assigneeName: string;
  relatedType: 'borrower' | 'partner' | 'referral' | 'lender' | 'realtor' | 'internal';
  relatedName: string;
  relatedId: string | null;
  createdAt: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  stage: PipelineStage;
  slaDays: number;
  ownerRole: string;
  automations: number;
  description: string;
}

export interface PipelineCard {
  id: string;
  borrowerId: string;
  borrowerName: string;
  stage: PipelineStage;
  readinessScore: number;
  loName: string;
  partnerName: string;
  daysInStage: number;
  estimatedReadyDate: string | null;
}

export interface AutomationRule {
  id: string;
  name: string;
  enabled: boolean;
  trigger: AutomationTrigger;
  action: string;
  channel: 'task' | 'email' | 'sms' | 'notification' | 'stage';
  lastFiredAt: string | null;
  fireCount: number;
  description: string;
}

export interface SmsMessage {
  id: string;
  toName: string;
  toPhone: string;
  body: string;
  status: ChannelStatus;
  sentAt: string;
  direction: 'outbound' | 'inbound';
  relatedBorrower: string | null;
}

export interface EmailMessage {
  id: string;
  toName: string;
  toEmail: string;
  subject: string;
  preview: string;
  status: ChannelStatus;
  sentAt: string;
  direction: 'outbound' | 'inbound';
  relatedBorrower: string | null;
}

export interface CrmReportMetric {
  label: string;
  value: string;
  delta: string;
  tone: 'up' | 'down' | 'flat';
}

export interface ReferralRecord {
  id: string;
  borrowerName: string;
  borrowerEmail: string;
  sourceType: 'lender' | 'realtor' | 'partner' | 'direct' | 'web';
  sourceName: string;
  loName: string;
  status: 'new' | 'accepted' | 'in_progress' | 'completed' | 'declined';
  referredAt: string;
  attributedPartnerId: string | null;
  borrowerId: string | null;
  notes: string;
  conversionValue: number | null;
}

export interface CalendarEvent {
  id: string;
  title: string;
  startsAt: string;
  endsAt: string;
  type: 'call' | 'meeting' | 'deadline' | 'follow_up' | 'review';
  relatedName: string;
  ownerName: string;
  location: string | null;
}

export interface CrmDocument {
  id: string;
  name: string;
  category: string;
  relatedType: 'borrower' | 'partner' | 'referral' | 'internal';
  relatedName: string;
  status: 'pending' | 'in_review' | 'verified' | 'rejected';
  uploadedAt: string;
  sizeLabel: string;
}

export interface CrmNote {
  id: string;
  body: string;
  authorName: string;
  createdAt: string;
  pinned: boolean;
  relatedType: 'borrower' | 'partner' | 'lender' | 'realtor' | 'referral' | 'internal';
  relatedName: string;
  relatedId: string | null;
}

export interface CrmReportingSnapshot {
  periodLabel: string;
  metrics: CrmReportMetric[];
  funnel: { stage: PipelineStage; count: number }[];
  referralBySource: { source: string; count: number; converted: number }[];
  partnerLeaderboard: { partner: string; referrals: number; funded: number }[];
}
