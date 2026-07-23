import { Suspense } from 'react';
import { AuthShell } from '@/components/portal/AuthShell';
import { BorrowerAuthForm } from '@/components/portal/BorrowerAuthForm';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Borrower Portal Login',
  description: 'Sign in to the Lending Readiness Partners borrower portal.',
  path: '/portal/login',
  noIndex: true,
});

export default function PortalLoginPage() {
  return (
    <AuthShell
      title="Helping More Borrowers Become Lending Ready."
      subtitle="Sign in with your platform portal account—same credentials and database as the client portal."
    >
      <Suspense fallback={<p className="text-sm text-slate-500">Loading sign-in…</p>}>
        <BorrowerAuthForm />
      </Suspense>
    </AuthShell>
  );
}
