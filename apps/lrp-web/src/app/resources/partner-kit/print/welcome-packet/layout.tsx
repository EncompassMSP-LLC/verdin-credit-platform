import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Welcome Packet — Print',
  description: 'Printable Mortgage Readiness Partnership welcome packet.',
  path: '/resources/partner-kit/print/welcome-packet',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
