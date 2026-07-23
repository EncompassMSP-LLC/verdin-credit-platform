import type { LenderPermission, LenderRole, RoleDefinition } from '@/lib/lender/types';

const ALL: LenderPermission[] = [
  'dashboard.view',
  'referrals.manage',
  'borrowers.view',
  'borrowers.edit',
  'readiness.view',
  'readiness.export',
  'pipeline.view',
  'pipeline.edit',
  'documents.view',
  'documents.upload',
  'messages.view',
  'messages.send',
  'analytics.view',
  'reports.view',
  'reports.export',
  'admin.manage',
  'permissions.manage',
  'notifications.view',
];

export const ROLE_DEFINITIONS: RoleDefinition[] = [
  {
    role: 'lender_admin',
    label: 'Lender Admin',
    description: 'Full partner workspace control, including users and export policy.',
    permissions: ALL,
  },
  {
    role: 'loan_officer',
    label: 'Loan Officer',
    description: 'Owns referrals, borrower tracking, messaging, and readiness exports.',
    permissions: [
      'dashboard.view',
      'referrals.manage',
      'borrowers.view',
      'borrowers.edit',
      'readiness.view',
      'readiness.export',
      'pipeline.view',
      'pipeline.edit',
      'documents.view',
      'documents.upload',
      'messages.view',
      'messages.send',
      'analytics.view',
      'reports.view',
      'reports.export',
      'notifications.view',
    ],
  },
  {
    role: 'credit_ops',
    label: 'Credit Operations',
    description: 'Pipeline and document operations with readiness visibility.',
    permissions: [
      'dashboard.view',
      'borrowers.view',
      'readiness.view',
      'pipeline.view',
      'pipeline.edit',
      'documents.view',
      'documents.upload',
      'messages.view',
      'messages.send',
      'reports.view',
      'notifications.view',
    ],
  },
  {
    role: 'underwriter_view',
    label: 'Underwriter (view)',
    description: 'Read-only readiness and document review for credit judgment support.',
    permissions: [
      'dashboard.view',
      'borrowers.view',
      'readiness.view',
      'readiness.export',
      'pipeline.view',
      'documents.view',
      'reports.view',
      'reports.export',
      'notifications.view',
    ],
  },
  {
    role: 'read_only',
    label: 'Read Only',
    description: 'Dashboard and borrower visibility without mutation or export.',
    permissions: [
      'dashboard.view',
      'borrowers.view',
      'readiness.view',
      'pipeline.view',
      'documents.view',
      'analytics.view',
      'reports.view',
      'notifications.view',
    ],
  },
];

const byRole = Object.fromEntries(
  ROLE_DEFINITIONS.map((def) => [def.role, new Set(def.permissions)]),
) as Record<LenderRole, Set<LenderPermission>>;

export function roleHasPermission(role: LenderRole, permission: LenderPermission): boolean {
  return byRole[role]?.has(permission) ?? false;
}

export function permissionsForRole(role: LenderRole): LenderPermission[] {
  return ROLE_DEFINITIONS.find((d) => d.role === role)?.permissions ?? [];
}

export const PERMISSION_LABELS: Record<LenderPermission, string> = {
  'dashboard.view': 'View dashboard',
  'referrals.manage': 'Manage referrals',
  'borrowers.view': 'View borrowers',
  'borrowers.edit': 'Edit borrower tracking',
  'readiness.view': 'View readiness reports',
  'readiness.export': 'Export readiness reports',
  'pipeline.view': 'View pipeline',
  'pipeline.edit': 'Move pipeline stages',
  'documents.view': 'View documents',
  'documents.upload': 'Upload documents',
  'messages.view': 'View messages',
  'messages.send': 'Send messages',
  'analytics.view': 'View analytics',
  'reports.view': 'View monthly reports',
  'reports.export': 'Export reports',
  'admin.manage': 'Admin panel',
  'permissions.manage': 'Manage role permissions',
  'notifications.view': 'View notifications',
};
