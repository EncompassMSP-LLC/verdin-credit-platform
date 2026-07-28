import type { RealtorPermission } from '@/lib/realtor/types';

export type RealtorNavIcon = 'dashboard' | 'referrals' | 'pipeline';

export type RealtorNavItem = {
  href: string;
  label: string;
  icon: RealtorNavIcon;
  permission: RealtorPermission;
};

/** Restricted realtor nav — no lender admin, readiness export, CRM, or borrower portal. */
export const realtorNav: RealtorNavItem[] = [
  {
    href: '/realtor/dashboard',
    label: 'Dashboard',
    icon: 'dashboard',
    permission: 'dashboard.view',
  },
  {
    href: '/realtor/referrals',
    label: 'My referrals',
    icon: 'referrals',
    permission: 'referrals.view',
  },
  {
    href: '/realtor/pipeline',
    label: 'Coarse status',
    icon: 'pipeline',
    permission: 'pipeline.view',
  },
];
