import { apiPath, request } from './http';

export type PartnerOrgType = 'lender' | 'realtor' | 'broker' | 'operator' | 'other';
export type PartnershipStatus = 'pending' | 'active' | 'paused' | 'ended';
export type PartnerRole =
  'lender_admin' | 'loan_officer' | 'credit_ops' | 'underwriter_view' | 'read_only';
export type PartnerReferralStatus = 'new' | 'accepted' | 'in_progress' | 'completed' | 'declined';
export type LoanPipelineStage =
  | 'referred'
  | 'intake'
  | 'in_repair'
  | 'near_ready'
  | 'mortgage_ready'
  | 'in_underwriting'
  | 'funded'
  | 'declined'
  | 'withdrawn';
export type PartnerAccessAction =
  | 'partnership_view'
  | 'referral_list'
  | 'referral_view'
  | 'member_list'
  | 'member_create'
  | 'partnership_create'
  | 'referral_create'
  | 'referral_update'
  | 'pipeline_view'
  | 'pipeline_update'
  | 'milestone_update'
  | 'readiness_view'
  | 'readiness_export'
  | 'contact_list'
  | 'contact_create'
  | 'contact_update';

export type PartnerContactRole =
  'loan_officer' | 'realtor' | 'branch_manager' | 'executive' | 'operations' | 'other';

export interface MortgagePartnerStatus {
  mortgage_partner_enabled: boolean;
  capabilities: string[];
  deferred_capabilities: string[];
}

export interface Partnership {
  id: string;
  cro_organization_id: string;
  partner_organization_id: string;
  partner_type: PartnerOrgType;
  status: PartnershipStatus;
  display_name: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  primary_contact_name?: string | null;
  primary_contact_email?: string | null;
  active_referral_count?: number;
}

export interface PartnerContact {
  id: string;
  partnership_id: string;
  cro_organization_id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  job_title: string | null;
  contact_role: PartnerContactRole;
  is_primary: boolean;
  is_active: boolean;
  user_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PartnerContactCreateInput {
  first_name: string;
  last_name: string;
  email?: string | null;
  phone?: string | null;
  job_title?: string | null;
  contact_role?: PartnerContactRole;
  is_primary?: boolean;
  is_active?: boolean;
  user_id?: string | null;
  notes?: string | null;
}

export interface PartnerContactUpdateInput {
  first_name?: string;
  last_name?: string;
  email?: string | null;
  phone?: string | null;
  job_title?: string | null;
  contact_role?: PartnerContactRole;
  is_primary?: boolean;
  is_active?: boolean;
  user_id?: string | null;
  notes?: string | null;
}

export interface PartnershipCreateInput {
  partner_organization_id: string;
  display_name: string;
  partner_type?: PartnerOrgType;
  status?: PartnershipStatus;
  notes?: string | null;
}

export interface PartnershipMember {
  id: string;
  partnership_id: string;
  organization_id: string;
  user_id: string;
  partner_role: PartnerRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PartnershipMemberCreateInput {
  user_id: string;
  partner_role?: PartnerRole;
  is_active?: boolean;
}

export interface PartnerLoanMilestone {
  id: string;
  referral_id: string;
  organization_id: string;
  label: string;
  sort_order: number;
  complete: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MilestoneReplaceItem {
  label: string;
  sort_order?: number;
  complete?: boolean;
}

export interface MilestoneReplacePayload {
  milestones: MilestoneReplaceItem[];
}

export interface PartnerReferral {
  id: string;
  partnership_id: string;
  cro_organization_id: string;
  client_id: string;
  case_id: string | null;
  status: PartnerReferralStatus;
  pipeline_stage: LoanPipelineStage;
  pipeline_stage_changed_at: string | null;
  source_label: string | null;
  notes: string | null;
  referred_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  /** CRO client display name for lender pipeline tables. */
  client_display_name?: string | null;
  milestones: PartnerLoanMilestone[];
}

export interface PartnerReferralCreateInput {
  client_id: string;
  case_id?: string | null;
  status?: PartnerReferralStatus;
  pipeline_stage?: LoanPipelineStage;
  source_label?: string | null;
  notes?: string | null;
}

export interface PartnerReferralUpdateInput {
  status?: PartnerReferralStatus;
  pipeline_stage?: LoanPipelineStage;
  notes?: string | null;
}

export interface PipelineCard {
  referral_id: string;
  client_id: string;
  client_display_name: string | null;
  pipeline_stage: LoanPipelineStage;
  referral_status: PartnerReferralStatus;
  days_in_stage: number;
  stage_changed_at: string | null;
  notes: string | null;
  source_label: string | null;
}

export interface PartnerDashboardSummary {
  total_referrals: number;
  counts_by_stage: Record<string, number>;
  near_ready_count: number;
  mortgage_ready_count: number;
  in_underwriting_count: number;
  funded_count: number;
  declined_count: number;
}

export interface PartnerAccessAudit {
  id: string;
  cro_organization_id: string;
  partnership_id: string | null;
  actor_user_id: string;
  action: PartnerAccessAction;
  resource_type: string;
  resource_id: string | null;
  detail: string | null;
  occurred_at: string;
  created_at: string;
}

export interface PartnerRoleMatrixItem {
  role: PartnerRole;
  permissions: string[];
}

export interface PartnerRoleMatrix {
  roles: PartnerRoleMatrixItem[];
}

export function getMortgagePartnerStatus() {
  return request<MortgagePartnerStatus>(apiPath('/mortgage-partner/status'));
}

export function getPartnerRoleMatrix() {
  return request<PartnerRoleMatrix>(apiPath('/mortgage-partner/roles'));
}

export function listPartnerAccessAudits() {
  return request<PartnerAccessAudit[]>(apiPath('/mortgage-partner/access-audits'));
}

export function createPartnership(body: PartnershipCreateInput) {
  return request<Partnership>(apiPath('/mortgage-partner/partnerships'), {
    method: 'POST',
    body,
  });
}

export function listPartnerships() {
  return request<Partnership[]>(apiPath('/mortgage-partner/partnerships'));
}

export function getPartnership(partnershipId: string) {
  return request<Partnership>(apiPath(`/mortgage-partner/partnerships/${partnershipId}`));
}

export function getPartnershipPipeline(partnershipId: string) {
  return request<PipelineCard[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/pipeline`),
  );
}

export function getPartnerDashboardSummary(partnershipId: string) {
  return request<PartnerDashboardSummary>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/dashboard-summary`),
  );
}

export function addPartnershipMember(partnershipId: string, body: PartnershipMemberCreateInput) {
  return request<PartnershipMember>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/members`),
    { method: 'POST', body },
  );
}

export function listPartnershipMembers(partnershipId: string) {
  return request<PartnershipMember[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/members`),
  );
}

export function listPartnerContacts(partnershipId: string) {
  return request<PartnerContact[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/contacts`),
  );
}

export function createPartnerContact(partnershipId: string, body: PartnerContactCreateInput) {
  return request<PartnerContact>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/contacts`),
    { method: 'POST', body },
  );
}

export function updatePartnerContact(
  partnershipId: string,
  contactId: string,
  body: PartnerContactUpdateInput,
) {
  return request<PartnerContact>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/contacts/${contactId}`),
    { method: 'PATCH', body },
  );
}

export function createPartnerReferral(partnershipId: string, body: PartnerReferralCreateInput) {
  return request<PartnerReferral>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals`),
    { method: 'POST', body },
  );
}

export function listPartnerReferrals(partnershipId: string) {
  return request<PartnerReferral[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals`),
  );
}

export function getPartnerReferral(partnershipId: string, referralId: string) {
  return request<PartnerReferral>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}`),
  );
}

export function updatePartnerReferral(
  partnershipId: string,
  referralId: string,
  body: PartnerReferralUpdateInput,
) {
  return request<PartnerReferral>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}`),
    { method: 'PATCH', body },
  );
}

export function listReferralMilestones(partnershipId: string, referralId: string) {
  return request<PartnerLoanMilestone[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}/milestones`),
  );
}

export function replaceReferralMilestones(
  partnershipId: string,
  referralId: string,
  body: MilestoneReplacePayload,
) {
  return request<PartnerLoanMilestone[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}/milestones`),
    { method: 'PUT', body },
  );
}

// ---------------------------------------------------------------------------
// Readiness reports (slice 4)
// ---------------------------------------------------------------------------

export interface ReadinessDimension {
  key: string;
  label: string;
  score: number;
  weight: number;
}

export interface ReadinessBlocker {
  id: string;
  title: string;
  impact: string;
  action: string;
}

export interface ReadinessPriorityTask {
  id: string;
  label: string;
  complete: boolean;
  completed_at: string | null;
}

export interface MortgageReadinessReport {
  referral_id: string;
  case_id: string;
  credit_analysis_run_id: string;
  client_display_name: string | null;
  mortgage_readiness_score: number;
  band: string;
  generated_at: string;
  dimensions: ReadinessDimension[];
  blockers: ReadinessBlocker[];
  priority_tasks: ReadinessPriorityTask[];
  docs_status: string;
  partner_notes: string | null;
  formula_version: string;
  score_version: string;
  /** Lending Readiness Score™ is an advisory tool for organizing credit and
   *  documentation work toward a mortgage conversation. It is not a credit score
   *  from a consumer reporting agency, not an underwriting decision, and not a
   *  guarantee of loan approval or terms. */
  disclaimer: string;
}

export interface ReadinessReportSummary {
  referral_id: string;
  case_id: string;
  credit_analysis_run_id: string;
  client_display_name: string | null;
  mortgage_readiness_score: number;
  band: string;
  generated_at: string;
  formula_version: string;
  score_version: string;
  disclaimer: string;
}

export function listPartnershipReadinessReports(partnershipId: string) {
  return request<ReadinessReportSummary[]>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/readiness-reports`),
  );
}

export function getReferralReadinessReport(partnershipId: string, referralId: string) {
  return request<MortgageReadinessReport>(
    apiPath(
      `/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}/readiness-report`,
    ),
  );
}

export function getReferralReadinessReportExportUrl(
  partnershipId: string,
  referralId: string,
  format: 'text' | 'pdf' = 'pdf',
): string {
  return apiPath(
    `/mortgage-partner/partnerships/${partnershipId}/referrals/${referralId}/readiness-report/export?format=${format}`,
  );
}

export interface ReferralIntakeStatus {
  referral_intake_enabled: boolean;
  organization_slug: string | null;
  blockers: string[];
}

export interface ReferralIntakeInput {
  partner_org_name: string;
  lo_name: string;
  lo_email: string;
  lo_phone?: string | null;
  borrower_name: string;
  borrower_email?: string | null;
  borrower_phone?: string | null;
  product_intent?: string | null;
  known_gaps?: string | null;
  notes?: string | null;
  consent_attested: boolean;
  partnership_id?: string | null;
}

export interface ReferralIntakeResult {
  intake_id: string;
  status: string;
  partnership_id: string | null;
  referral_id: string | null;
  client_id: string | null;
  case_id: string | null;
  task_id: string | null;
  message: string;
  quarantine_reason?: string | null;
}

export function getReferralIntakeStatus(): Promise<ReferralIntakeStatus> {
  return request<ReferralIntakeStatus>(apiPath('/mortgage-partner/referral-intake/status'), {
    auth: false,
  });
}

export function submitReferralIntake(input: ReferralIntakeInput): Promise<ReferralIntakeResult> {
  return request<ReferralIntakeResult>(apiPath('/mortgage-partner/referral-intake'), {
    method: 'POST',
    body: input,
    auth: false,
  });
}

export type CrmAutomationTrigger =
  | 'stage_enter'
  | 'referral_created'
  | 'task_overdue'
  | 'score_band_change'
  | 'document_uploaded'
  | 'manual';

export type CrmAutomationChannel = 'task' | 'email' | 'sms' | 'notification' | 'stage';

export interface CrmAutomationRule {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  enabled: boolean;
  trigger: CrmAutomationTrigger;
  action: string;
  channel: CrmAutomationChannel;
  last_fired_at: string | null;
  fire_count: number;
  created_at: string;
  updated_at: string;
}

export interface CrmAutomationRuleCreateInput {
  name: string;
  description?: string | null;
  enabled?: boolean;
  trigger: CrmAutomationTrigger;
  action: string;
  channel: CrmAutomationChannel;
}

export interface CrmAutomationRuleUpdateInput {
  name?: string;
  description?: string | null;
  enabled?: boolean;
  trigger?: CrmAutomationTrigger;
  action?: string;
  channel?: CrmAutomationChannel;
}

export function listCrmAutomationRules() {
  return request<CrmAutomationRule[]>(apiPath('/mortgage-partner/automation-rules'));
}

export function createCrmAutomationRule(body: CrmAutomationRuleCreateInput) {
  return request<CrmAutomationRule>(apiPath('/mortgage-partner/automation-rules'), {
    method: 'POST',
    body,
  });
}

export function updateCrmAutomationRule(ruleId: string, body: CrmAutomationRuleUpdateInput) {
  return request<CrmAutomationRule>(apiPath(`/mortgage-partner/automation-rules/${ruleId}`), {
    method: 'PATCH',
    body,
  });
}
