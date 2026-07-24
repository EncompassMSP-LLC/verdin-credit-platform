import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Company Brochure — Print',
  description: 'Printable digital brochure for Lending Readiness Partners.',
  path: '/resources/partner-kit/print/brochure',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
