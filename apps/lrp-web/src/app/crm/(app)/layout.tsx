import type { ReactNode } from 'react';
import { CrmShell } from '@/components/crm/CrmShell';

export default function CrmAppLayout({ children }: { children: ReactNode }) {
  return <CrmShell>{children}</CrmShell>;
}
