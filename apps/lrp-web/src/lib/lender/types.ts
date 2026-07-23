/** Lender workspace domain types — shaped for future Mortgage Partner APIs. */

export type LenderRole =
  'lender_admin' | 'loan_officer' | 'credit_ops' | 'underwriter_view' | 'read_only';

export type LenderPermission =
  | 'dashboard.view'
  | 'referrals.manage'
  | 'borrowers.view'
  | 'borrowers.edit'
  | 'readiness.view'
  | 'readiness.export'
  | 'pipeline.view'
  | 'pipeline.edit'
  | 'documents.view'
  | 'documents.upload'
  | 'messages.view'
  | 'messages.send'
  | 'analytics.view'
  | 'reports.view'
  | 'reports.export'
  | 'admin.manage'
  | 'permissions.manage'
  | 'notifications.view';

export type PipelineStage =
  | 'referred'
  | 'intake'
  | 'in_repair'
  | 'near_ready'
  | 'mortgage_ready'
  | 'in_underwriting'
  | 'funded'
  | 'declined'
  | 'withdrawn';

export type ReferralStatus = 'new' | 'accepted' | 'in_progress' | 'completed' | 'declined';

export type DocumentStatus = 'pending' | 'in_review' | 'verified' | 'rejected';

export interface LenderUser {
  id: string;
  email: string;
  displayName: string;
  role: LenderRole;
  organizationId: string;
  organizationName: string;
  title: string;
}

export interface Referral {
  id: string;
  borrowerName: string;
  borrowerEmail: string;
  source: string;
  loName: string;
  status: ReferralStatus;
  referredAt: string;
  targetProduct: string;
  notes: string;
  borrowerId: string | null;
}

export interface Borrower {
  id: string;
  displayName: string;
  email: string;
  phone: string;
  loName: string;
  stage: PipelineStage;
  readinessScore: number;
  readinessBand: string;
  estimatedReadyDate: string | null;
  progressPct: number;
  lastActivityAt: string;
  referralId: string | null;
  blockers: string[];
  milestones: BorrowerMilestone[];
  loanAmountTarget: number | null;
  propertyState: string | null;
}

export interface BorrowerMilestone {
  id: string;
  label: string;
  complete: boolean;
  completedAt: string | null;
}

export interface ReadinessReport {
  id: string;
  borrowerId: string;
  borrowerName: string;
  overall: number;
  band: string;
  generatedAt: string;
  estimatedReadyDate: string | null;
  dimensions: { key: string; label: string; score: number }[];
  blockers: { title: string; impact: string; action: string }[];
  disclaimer: string;
}

export interface PipelineCard {
  id: string;
  borrowerId: string;
  borrowerName: string;
  stage: PipelineStage;
  readinessScore: number;
  estimatedReadyDate: string | null;
  loName: string;
  daysInStage: number;
}

export interface LenderDocument {
  id: string;
  borrowerId: string;
  borrowerName: string;
  name: string;
  category: string;
  status: DocumentStatus;
  uploadedAt: string;
  sizeLabel: string;
}

export interface LenderThread {
  id: string;
  borrowerId: string;
  borrowerName: string;
  subject: string;
  updatedAt: string;
  unread: number;
  preview: string;
  messages: { id: string; from: string; body: string; at: string; mine: boolean }[];
}

export interface AnalyticsSnapshot {
  periodLabel: string;
  referralsAccepted: number;
  avgDaysToNearReady: number;
  mortgageReadyCount: number;
  fundedCount: number;
  pullThroughRate: number;
  stageDistribution: { stage: PipelineStage; count: number }[];
  readinessBands: { band: string; count: number }[];
  monthlyTrend: { month: string; referred: number; ready: number; funded: number }[];
}

export interface MonthlyReport {
  id: string;
  month: string;
  title: string;
  generatedAt: string;
  highlights: string[];
  metrics: { label: string; value: string }[];
}

export interface LenderNotification {
  id: string;
  title: string;
  body: string;
  at: string;
  read: boolean;
  href: string;
  severity: 'info' | 'warn' | 'success';
}

export interface RoleDefinition {
  role: LenderRole;
  label: string;
  description: string;
  permissions: LenderPermission[];
}

export interface OrgAdminSettings {
  organizationName: string;
  partnerCode: string;
  brandingPrimary: string;
  readinessExportEnabled: boolean;
  notifyOnStageChange: boolean;
  notifyOnReady: boolean;
  defaultLoId: string;
  retentionDays: number;
}
