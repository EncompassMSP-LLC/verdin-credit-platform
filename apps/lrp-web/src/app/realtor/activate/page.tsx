import { Suspense } from 'react';
import { RealtorActivateForm } from '@/components/realtor/RealtorActivateForm';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Activate Realtor Invite',
  description: 'Activate your Lending Readiness Partners realtor workspace invite.',
  path: '/realtor/activate',
  noIndex: true,
});

export default function RealtorActivatePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-lrp-surface px-5 py-14">
      <div className="w-full max-w-md rounded-md border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
        <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
          Realtor activation
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-navy-900">Accept your invite</h1>
        <p className="mt-2 text-sm text-slate-500">
          Set a password to activate your partnership-scoped realtor account.
        </p>
        <div className="mt-6">
          <Suspense fallback={<p className="text-sm text-slate-500">Loading…</p>}>
            <RealtorActivateForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
