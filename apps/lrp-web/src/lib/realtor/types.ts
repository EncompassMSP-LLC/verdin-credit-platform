/** Realtor workspace types (LRP-301) — restricted vs lender surfaces. */

export type RealtorPermission =
  'dashboard.view' | 'referrals.view' | 'referrals.create' | 'pipeline.view';

export interface RealtorUser {
  id: string;
  email: string;
  displayName: string;
  organizationId: string;
  organizationName: string;
  partnershipId: string;
  partnershipDisplayName: string;
  permissions: RealtorPermission[];
  title: string;
}
