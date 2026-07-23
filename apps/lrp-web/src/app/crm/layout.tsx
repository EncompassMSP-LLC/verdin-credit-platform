import type { ReactNode } from 'react';
import { CrmProviders } from '@/components/providers/CrmProviders';

export default function CrmRootLayout({ children }: { children: ReactNode }) {
  return <CrmProviders>{children}</CrmProviders>;
}
