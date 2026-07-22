import type { CrmPermission } from '@/lib/crm/types';

export type CrmNavIcon =
  | 'dashboard'
  | 'partners'
  | 'borrowers'
  | 'lenders'
  | 'realtors'
  | 'tasks'
  | 'workflow'
  | 'pipeline'
  | 'automations'
  | 'sms'
  | 'email'
  | 'reporting'
  | 'referrals'
  | 'calendar'
  | 'documents'
  | 'notes'
  | 'admin'
  | 'permissions';

export type CrmNavItem = {
  href: string;
  label: string;
  icon: CrmNavIcon;
  permission: CrmPermission;
  group: 'relationships' | 'operations' | 'engagement' | 'insights' | 'governance';
};

export const crmNav: CrmNavItem[] = [
  {
    href: '/crm/dashboard',
    label: 'Dashboard',
    icon: 'dashboard',
    permission: 'dashboard.view',
    group: 'operations',
  },
  {
    href: '/crm/partners',
    label: 'Partners',
    icon: 'partners',
    permission: 'partners.view',
    group: 'relationships',
  },
  {
    href: '/crm/borrowers',
    label: 'Borrowers',
    icon: 'borrowers',
    permission: 'borrowers.view',
    group: 'relationships',
  },
  {
    href: '/crm/lenders',
    label: 'Lenders',
    icon: 'lenders',
    permission: 'lenders.view',
    group: 'relationships',
  },
  {
    href: '/crm/realtors',
    label: 'Realtors',
    icon: 'realtors',
    permission: 'realtors.view',
    group: 'relationships',
  },
  {
    href: '/crm/referrals',
    label: 'Referral Tracking',
    icon: 'referrals',
    permission: 'referrals.view',
    group: 'relationships',
  },
  {
    href: '/crm/tasks',
    label: 'Tasks',
    icon: 'tasks',
    permission: 'tasks.view',
    group: 'operations',
  },
  {
    href: '/crm/workflow',
    label: 'Workflow',
    icon: 'workflow',
    permission: 'workflow.view',
    group: 'operations',
  },
  {
    href: '/crm/pipeline',
    label: 'Pipeline',
    icon: 'pipeline',
    permission: 'pipeline.view',
    group: 'operations',
  },
  {
    href: '/crm/automations',
    label: 'Automations',
    icon: 'automations',
    permission: 'automations.view',
    group: 'operations',
  },
  {
    href: '/crm/calendar',
    label: 'Calendar',
    icon: 'calendar',
    permission: 'calendar.view',
    group: 'operations',
  },
  {
    href: '/crm/documents',
    label: 'Documents',
    icon: 'documents',
    permission: 'documents.view',
    group: 'operations',
  },
  {
    href: '/crm/notes',
    label: 'Notes',
    icon: 'notes',
    permission: 'notes.view',
    group: 'operations',
  },
  {
    href: '/crm/sms',
    label: 'SMS',
    icon: 'sms',
    permission: 'sms.view',
    group: 'engagement',
  },
  {
    href: '/crm/email',
    label: 'Email',
    icon: 'email',
    permission: 'email.view',
    group: 'engagement',
  },
  {
    href: '/crm/reporting',
    label: 'Reporting',
    icon: 'reporting',
    permission: 'reporting.view',
    group: 'insights',
  },
  {
    href: '/crm/admin',
    label: 'Admin',
    icon: 'admin',
    permission: 'admin.manage',
    group: 'governance',
  },
  {
    href: '/crm/permissions',
    label: 'Role Permissions',
    icon: 'permissions',
    permission: 'permissions.manage',
    group: 'governance',
  },
];

export const STAGE_LABELS: Record<string, string> = {
  lead: 'Lead',
  qualified: 'Qualified',
  referred: 'Referred',
  intake: 'Intake',
  in_repair: 'In repair',
  near_ready: 'Near ready',
  mortgage_ready: 'Mortgage ready',
  in_underwriting: 'In underwriting',
  funded: 'Funded',
  lost: 'Lost',
};

export const PIPELINE_BOARD_STAGES = [
  'lead',
  'qualified',
  'referred',
  'intake',
  'in_repair',
  'near_ready',
  'mortgage_ready',
  'in_underwriting',
] as const;
