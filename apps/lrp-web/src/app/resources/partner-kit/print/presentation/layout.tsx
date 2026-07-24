import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Partner Presentation — Print / PDF',
  description: 'HTML partner presentation deck printable to PDF.',
  path: '/resources/partner-kit/print/presentation',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
