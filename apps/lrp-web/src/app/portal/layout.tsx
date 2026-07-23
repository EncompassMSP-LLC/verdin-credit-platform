import type { ReactNode } from 'react';
import { PortalProviders } from '@/components/providers/PortalProviders';

export default function PortalRootLayout({ children }: { children: ReactNode }) {
  return <PortalProviders>{children}</PortalProviders>;
}
