import type { RealtorPermission } from '@/lib/realtor/types';

export const REALTOR_PERMISSIONS: RealtorPermission[] = [
  'dashboard.view',
  'referrals.view',
  'referrals.create',
  'pipeline.view',
];

const API_TO_UI: Record<string, RealtorPermission | undefined> = {
  'partnership.view': 'dashboard.view',
  'referrals.view': 'referrals.view',
  'referrals.create': 'referrals.create',
  'pipeline.view': 'pipeline.view',
};

export function mapApiPermissions(apiPermissions: string[]): RealtorPermission[] {
  const mapped = new Set<RealtorPermission>();
  for (const p of apiPermissions) {
    const ui = API_TO_UI[p];
    if (ui) mapped.add(ui);
  }
  // Always include dashboard when partnership.view is present
  if (apiPermissions.includes('partnership.view')) mapped.add('dashboard.view');
  return [...mapped];
}

export function roleHasPermission(
  permissions: RealtorPermission[],
  permission: RealtorPermission,
): boolean {
  return permissions.includes(permission);
}
