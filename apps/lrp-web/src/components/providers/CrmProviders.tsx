'use client';

import type { ReactNode } from 'react';
import { CrmAuthProvider } from '@/lib/crm/auth';

export function CrmProviders({ children }: { children: ReactNode }) {
  return <CrmAuthProvider>{children}</CrmAuthProvider>;
}
