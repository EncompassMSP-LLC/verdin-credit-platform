import { apiPath, request } from './http';

export type PartnerOrgType = 'lender' | 'realtor' | 'broker' | 'operator' | 'other';
export type PartnershipStatus = 'pending' | 'active' | 'paused' | 'ended';
export type PartnerRole =
  'lender_admin' | 'loan_officer' | 'credit_ops' | 'underwriter_view' | 'read_only';
export type PartnerReferralStatus = 'new' | 'accepted' | 'in_progress' | 'completed' | 'declined';
export type PartnerAccessAction =
  | 'partnership_view'
  | 'referral_list'
  | 'referral_view'
  | 'member_list'
  | 'member_create'
  | 'partnership_create'
  | 'referral_create'
  | 'referral_update';

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

export interface PartnerReferral {
  id: string;
  partnership_id: string;
  cro_organization_id: string;
  client_id: string;
  case_id: string | null;
  status: PartnerReferralStatus;
  source_label: string | null;
  notes: string | null;
  referred_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  /** CRO client display name for lender pipeline tables (Vol 20). */
  client_display_name?: string | null;
}

export interface PartnerReferralCreateInput {
  client_id: string;
  case_id?: string | null;
  status?: PartnerReferralStatus;
  source_label?: string | null;
  notes?: string | null;
}

export interface PartnerReferralUpdateInput {
  status: PartnerReferralStatus;
  notes?: string | null;
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
