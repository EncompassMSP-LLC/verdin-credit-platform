import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'LO Quick Reference — Print',
  description: 'Printable loan officer quick reference for Mortgage Readiness Partnerships.',
  path: '/resources/partner-kit/print/lo-quick-reference',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
