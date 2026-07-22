'use client';

import type { ReactNode } from 'react';
import { useCrmAuth } from '@/lib/crm/auth';
import type { CrmPermission } from '@/lib/crm/types';

export function RoleGate({
  permission,
  children,
  fallback = null,
}: {
  permission: CrmPermission;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const { can } = useCrmAuth();
  if (!can(permission)) return <>{fallback}</>;
  return <>{children}</>;
}
