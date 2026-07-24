import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Sales Scripts & Objections — Print',
  description: 'Printable sales scripts and objection handling guide.',
  path: '/resources/partner-kit/print/sales-playbook',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
