import type { ReactNode } from 'react';
import { RealtorProviders } from '@/components/providers/RealtorProviders';

export default function RealtorRootLayout({ children }: { children: ReactNode }) {
  return <RealtorProviders>{children}</RealtorProviders>;
}
