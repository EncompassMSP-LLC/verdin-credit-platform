import type { LenderPermission } from '@/lib/lender/types';

export type LenderNavIcon =
  | 'dashboard'
  | 'referrals'
  | 'borrowers'
  | 'readiness'
  | 'pipeline'
  | 'documents'
  | 'messages'
  | 'analytics'
  | 'reports'
  | 'admin'
  | 'permissions'
  | 'notifications'
  | 'exports';

export type LenderNavItem = {
  href: string;
  label: string;
  icon: LenderNavIcon;
  permission: LenderPermission;
  group: 'operations' | 'insights' | 'governance';
};

export const lenderNav: LenderNavItem[] = [
  {
    href: '/lender/dashboard',
    label: 'Dashboard',
    icon: 'dashboard',
    permission: 'dashboard.view',
    group: 'operations',
  },
  {
    href: '/lender/referrals',
    label: 'Referral Management',
    icon: 'referrals',
    permission: 'referrals.manage',
    group: 'operations',
  },
  {
    href: '/lender/borrowers',
    label: 'Borrower Tracking',
    icon: 'borrowers',
    permission: 'borrowers.view',
    group: 'operations',
  },
  {
    href: '/lender/readiness',
    label: 'Readiness Reports',
    icon: 'readiness',
    permission: 'readiness.view',
    group: 'operations',
  },
  {
    href: '/lender/analysis',
    label: 'AI Credit Analysis',
    icon: 'readiness',
    permission: 'readiness.view',
    group: 'operations',
  },
  {
    href: '/lender/pipeline',
    label: 'Pipeline',
    icon: 'pipeline',
    permission: 'pipeline.view',
    group: 'operations',
  },
  {
    href: '/lender/documents',
    label: 'Documents',
    icon: 'documents',
    permission: 'documents.view',
    group: 'operations',
  },
  {
    href: '/lender/messages',
    label: 'Messages',
    icon: 'messages',
    permission: 'messages.view',
    group: 'operations',
  },
  {
    href: '/lender/analytics',
    label: 'Analytics',
    icon: 'analytics',
    permission: 'analytics.view',
    group: 'insights',
  },
  {
    href: '/lender/reports',
    label: 'Monthly Reports',
    icon: 'reports',
    permission: 'reports.view',
    group: 'insights',
  },
  {
    href: '/lender/exports',
    label: 'Export Reports',
    icon: 'exports',
    permission: 'reports.export',
    group: 'insights',
  },
  {
    href: '/lender/notifications',
    label: 'Notifications',
    icon: 'notifications',
    permission: 'notifications.view',
    group: 'governance',
  },
  {
    href: '/lender/admin',
    label: 'Admin Panel',
    icon: 'admin',
    permission: 'admin.manage',
    group: 'governance',
  },
  {
    href: '/lender/permissions',
    label: 'Role Permissions',
    icon: 'permissions',
    permission: 'permissions.manage',
    group: 'governance',
  },
];

export const STAGE_LABELS: Record<string, string> = {
  referred: 'Referred',
  intake: 'Intake',
  in_repair: 'In repair',
  near_ready: 'Near ready',
  mortgage_ready: 'Mortgage ready',
  in_underwriting: 'In underwriting',
  funded: 'Funded',
  declined: 'Declined',
  withdrawn: 'Withdrawn',
};

export const PIPELINE_BOARD_STAGES = [
  'referred',
  'intake',
  'in_repair',
  'near_ready',
  'mortgage_ready',
  'in_underwriting',
] as const;
