import { apiPath, request } from './http';

export type PartnerOrgType = 'lender' | 'realtor' | 'broker' | 'operator' | 'other';
export type PartnershipStatus = 'pending' | 'active' | 'paused' | 'ended';
export type PartnerRole =
  'lender_admin' | 'loan_officer' | 'credit_ops' | 'underwriter_view' | 'read_only' | 'realtor';
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

export type CrmAppointmentType = 'consultation' | 'call' | 'meeting' | 'follow_up' | 'review';

export type CrmAppointmentStatus = 'scheduled' | 'completed' | 'cancelled' | 'no_show';

export interface CrmAppointment {
  id: string;
  organization_id: string;
  case_id: string | null;
  title: string;
  appointment_type: CrmAppointmentType;
  status: CrmAppointmentStatus;
  starts_at: string;
  ends_at: string;
  location: string | null;
  meeting_url: string | null;
  related_name: string | null;
  owner_user_id: string | null;
  borrower_name: string | null;
  borrower_email: string | null;
  borrower_phone: string | null;
  referring_lo_email: string | null;
  referring_lo_name: string | null;
  tcpa_consent: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrmAppointmentCreateInput {
  title: string;
  appointment_type?: CrmAppointmentType;
  starts_at: string;
  ends_at: string;
  case_id?: string | null;
  location?: string | null;
  meeting_url?: string | null;
  related_name?: string | null;
  owner_user_id?: string | null;
  borrower_name?: string | null;
  borrower_email?: string | null;
  borrower_phone?: string | null;
  referring_lo_email?: string | null;
  referring_lo_name?: string | null;
  tcpa_consent?: boolean;
  notes?: string | null;
}

export interface AppointmentReminderRun {
  id: string;
  organization_id: string;
  appointment_id: string;
  offset_key: string;
  status: string;
  schema_version: string;
  matrix_dispatch_id: string | null;
  started_at: string;
  completed_at: string | null;
  payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AppointmentReminderProcessResult {
  processed_count: number;
  runs: AppointmentReminderRun[];
}

export function listCrmAppointments() {
  return request<CrmAppointment[]>(apiPath('/mortgage-partner/appointments'));
}

export function createCrmAppointment(body: CrmAppointmentCreateInput) {
  return request<CrmAppointment>(apiPath('/mortgage-partner/appointments'), {
    method: 'POST',
    body,
  });
}

export function processAppointmentReminders() {
  return request<AppointmentReminderProcessResult>(
    apiPath('/mortgage-partner/appointments/reminders/process'),
    { method: 'POST' },
  );
}

export function listAppointmentReminders(appointmentId?: string) {
  const query = appointmentId ? `?appointment_id=${encodeURIComponent(appointmentId)}` : '';
  return request<AppointmentReminderRun[]>(
    apiPath(`/mortgage-partner/appointments/reminders${query}`),
  );
}

export type NurtureEnrollmentStatus = 'active' | 'paused' | 'completed' | 'exited';

export interface NurtureStep {
  id: string;
  program_id: string;
  step_order: number;
  delay_days: number;
  channel: string;
  template_key: string;
  subject: string;
  body_template: string;
}

export interface NurtureProgram {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  audience: string;
  enrollment_lifecycle_stage: string;
  enabled: boolean;
  steps: NurtureStep[];
  created_at: string;
  updated_at: string;
}

export interface NurtureEnrollment {
  id: string;
  organization_id: string;
  program_id: string;
  partnership_id: string | null;
  contact_name: string;
  contact_email: string | null;
  contact_phone: string | null;
  status: NurtureEnrollmentStatus;
  current_step_order: number;
  next_run_at: string | null;
  enrolled_at: string;
  paused_at: string | null;
  completed_at: string | null;
  exited_at: string | null;
  exit_reason: string | null;
  marketing_opt_in: boolean;
  tcpa_consent: boolean;
  created_at: string;
  updated_at: string;
}

export interface NurtureEnrollmentCreateInput {
  program_id: string;
  contact_name: string;
  contact_email?: string | null;
  contact_phone?: string | null;
  partnership_id?: string | null;
  marketing_opt_in?: boolean;
  tcpa_consent?: boolean;
}

export interface NurtureEnrollmentUpdateInput {
  status?: NurtureEnrollmentStatus;
  marketing_opt_in?: boolean;
  tcpa_consent?: boolean;
  exit_reason?: string | null;
}

export interface NurtureDeliveryRun {
  id: string;
  organization_id: string;
  enrollment_id: string;
  program_id: string;
  step_id: string;
  channel: string;
  status: string;
  schema_version: string;
  attempted_at: string;
  payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface NurtureDeliveryProcessResult {
  processed_count: number;
  runs: NurtureDeliveryRun[];
}

export function listNurturePrograms() {
  return request<NurtureProgram[]>(apiPath('/mortgage-partner/nurture/programs'));
}

export function listNurtureEnrollments() {
  return request<NurtureEnrollment[]>(apiPath('/mortgage-partner/nurture/enrollments'));
}

export function createNurtureEnrollment(body: NurtureEnrollmentCreateInput) {
  return request<NurtureEnrollment>(apiPath('/mortgage-partner/nurture/enrollments'), {
    method: 'POST',
    body,
  });
}

export function updateNurtureEnrollment(enrollmentId: string, body: NurtureEnrollmentUpdateInput) {
  return request<NurtureEnrollment>(
    apiPath(`/mortgage-partner/nurture/enrollments/${enrollmentId}`),
    { method: 'PATCH', body },
  );
}

export function processNurtureDue() {
  return request<NurtureDeliveryProcessResult>(apiPath('/mortgage-partner/nurture/process'), {
    method: 'POST',
  });
}

export function listNurtureDeliveries(enrollmentId?: string) {
  const query = enrollmentId ? `?enrollment_id=${encodeURIComponent(enrollmentId)}` : '';
  return request<NurtureDeliveryRun[]>(apiPath(`/mortgage-partner/nurture/deliveries${query}`));
}

export interface WeeklyDigestSubscription {
  id: string;
  organization_id: string;
  partnership_id: string;
  recipient_name: string;
  recipient_email: string;
  enabled: boolean;
  marketing_opt_in: boolean;
  send_weekday: number;
  created_at: string;
  updated_at: string;
}

export interface WeeklyDigestSubscriptionCreateInput {
  partnership_id: string;
  recipient_name: string;
  recipient_email: string;
  send_weekday?: number;
  marketing_opt_in?: boolean;
}

export interface WeeklyDigestSubscriptionUpdateInput {
  enabled?: boolean;
  marketing_opt_in?: boolean;
  recipient_name?: string;
  send_weekday?: number;
}

export interface WeeklyDigestRun {
  id: string;
  organization_id: string;
  partnership_id: string;
  subscription_id: string;
  week_key: string;
  status: string;
  schema_version: string;
  attempted_at: string;
  payload: Record<string, unknown>;
  body_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface WeeklyDigestProcessResult {
  processed_count: number;
  week_key: string;
  runs: WeeklyDigestRun[];
}

export function listWeeklyDigestSubscriptions() {
  return request<WeeklyDigestSubscription[]>(
    apiPath('/mortgage-partner/weekly-digests/subscriptions'),
  );
}

export function createWeeklyDigestSubscription(body: WeeklyDigestSubscriptionCreateInput) {
  return request<WeeklyDigestSubscription>(
    apiPath('/mortgage-partner/weekly-digests/subscriptions'),
    { method: 'POST', body },
  );
}

export function updateWeeklyDigestSubscription(
  subscriptionId: string,
  body: WeeklyDigestSubscriptionUpdateInput,
) {
  return request<WeeklyDigestSubscription>(
    apiPath(`/mortgage-partner/weekly-digests/subscriptions/${subscriptionId}`),
    { method: 'PATCH', body },
  );
}

export function processWeeklyDigests(weekKey?: string, force = true) {
  const params = new URLSearchParams();
  if (weekKey) params.set('week_key', weekKey);
  params.set('force', String(force));
  const query = params.toString() ? `?${params.toString()}` : '';
  return request<WeeklyDigestProcessResult>(
    apiPath(`/mortgage-partner/weekly-digests/process${query}`),
    { method: 'POST' },
  );
}

export function listWeeklyDigestRuns(partnershipId?: string) {
  const query = partnershipId ? `?partnership_id=${encodeURIComponent(partnershipId)}` : '';
  return request<WeeklyDigestRun[]>(apiPath(`/mortgage-partner/weekly-digests/runs${query}`));
}

/* --- Realtor partner role + login (LRP-301) --- */

export interface RealtorSession {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  partner_role: PartnerRole;
  permissions: string[];
  membership_id: string;
  membership_active: boolean;
  partnership_id: string;
  partnership_display_name: string;
  cro_organization_id: string;
  partner_organization_id: string;
  partner_organization_name: string;
  partner_type: PartnerOrgType;
}

export interface RealtorInvite {
  id: string;
  organization_id: string;
  partnership_id: string;
  partner_organization_id: string;
  email: string;
  first_name: string;
  last_name: string;
  expires_at: string;
  accepted_at: string | null;
  revoked_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  invite_token?: string | null;
}

export interface RealtorInvitePreview {
  email: string;
  first_name: string;
  last_name: string;
  partnership_display_name: string;
  partner_organization_name: string;
  expires_at: string;
  already_accepted: boolean;
}

export interface RealtorInviteCreateInput {
  email: string;
  first_name: string;
  last_name: string;
  notes?: string | null;
}

export interface RealtorTokenResult {
  access_token: string;
  refresh_token: string;
  token_type: string;
  realtor: RealtorSession;
}

export interface RealtorPasswordResetRequestResult {
  detail: string;
  reset_token: string | null;
}

export function getRealtorMe() {
  return request<RealtorSession>(apiPath('/mortgage-partner/realtor/me'));
}

export function createRealtorInvite(partnershipId: string, body: RealtorInviteCreateInput) {
  return request<RealtorInvite>(
    apiPath(`/mortgage-partner/partnerships/${partnershipId}/realtor-invites`),
    { method: 'POST', body },
  );
}

export function disableRealtorMembership(
  partnershipId: string,
  memberId: string,
  disableUser = false,
) {
  const query = disableUser ? '?disable_user=true' : '';
  return request<RealtorSession>(
    apiPath(
      `/mortgage-partner/partnerships/${partnershipId}/realtor-members/${memberId}/disable${query}`,
    ),
    { method: 'POST' },
  );
}

export function previewRealtorInvite(token: string) {
  return request<RealtorInvitePreview>(
    apiPath(`/mortgage-partner/realtor/invites/preview?token=${encodeURIComponent(token)}`),
    { auth: false },
  );
}

export function acceptRealtorInvite(token: string, password: string) {
  return request<RealtorTokenResult>(apiPath('/mortgage-partner/realtor/invites/accept'), {
    method: 'POST',
    body: { token, password },
    auth: false,
  });
}

export function requestRealtorPasswordReset(email: string) {
  return request<RealtorPasswordResetRequestResult>(
    apiPath('/mortgage-partner/realtor/password-reset/request'),
    { method: 'POST', body: { email }, auth: false },
  );
}

export function confirmRealtorPasswordReset(token: string, password: string) {
  return request<RealtorTokenResult>(apiPath('/mortgage-partner/realtor/password-reset/confirm'), {
    method: 'POST',
    body: { token, password },
    auth: false,
  });
}

/* --- Realtor portal MVP (LRP-302) --- */

export interface RealtorReferralCard {
  referral_id: string;
  borrower_initials: string;
  pipeline_stage: LoanPipelineStage;
  referral_status: PartnerReferralStatus;
  days_in_stage: number;
  stage_changed_at: string | null;
  source_label: string | null;
  is_own_referral: boolean;
  created_at: string;
}

export interface RealtorPipelineBoard {
  partnership_id: string;
  partnership_display_name: string;
  cards: RealtorReferralCard[];
}

export interface RealtorPortalDashboard {
  partnership_id: string;
  partnership_display_name: string;
  total_referrals: number;
  own_referral_count: number;
  counts_by_stage: Record<string, number>;
  near_ready_count: number;
  mortgage_ready_count: number;
  in_underwriting_count: number;
  funded_count: number;
  declined_count: number;
  recent: RealtorReferralCard[];
  advisory_disclaimer: string;
}

export function getRealtorPortalDashboard() {
  return request<RealtorPortalDashboard>(apiPath('/mortgage-partner/realtor/dashboard'));
}

export function listRealtorReferrals() {
  return request<RealtorReferralCard[]>(apiPath('/mortgage-partner/realtor/referrals'));
}

export function getRealtorPipeline() {
  return request<RealtorPipelineBoard>(apiPath('/mortgage-partner/realtor/pipeline'));
}
