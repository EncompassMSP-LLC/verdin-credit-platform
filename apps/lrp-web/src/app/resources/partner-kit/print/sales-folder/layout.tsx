import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Sales Presentation Folder — Print',
  description: 'Printable front, back, and inside flaps for the LRP sales presentation folder.',
  path: '/resources/partner-kit/print/sales-folder',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
