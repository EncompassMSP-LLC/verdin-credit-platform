'use client';

import type { ReactNode } from 'react';
import { useLenderAuth } from '@/lib/lender/auth';
import type { LenderPermission } from '@/lib/lender/types';

export function RoleGate({
  permission,
  children,
  fallback = (
    <p className="rounded-md border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
      You do not have permission to view this surface. Contact your lender admin.
    </p>
  ),
}: {
  permission: LenderPermission;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const { can } = useLenderAuth();
  if (!can(permission)) return <>{fallback}</>;
  return <>{children}</>;
}
