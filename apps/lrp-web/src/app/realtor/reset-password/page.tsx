import { Suspense } from 'react';
import { RealtorResetPasswordForm } from '@/components/realtor/RealtorPasswordForms';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Reset Realtor Password',
  description: 'Choose a new password for your realtor workspace account.',
  path: '/realtor/reset-password',
  noIndex: true,
});

export default function RealtorResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-lrp-surface px-5 py-14">
      <div className="w-full max-w-md rounded-md border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
        <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
          Realtor workspace
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-navy-900">Reset password</h1>
        <p className="mt-2 text-sm text-slate-500">Enter your reset token and a new password.</p>
        <div className="mt-6">
          <Suspense fallback={<p className="text-sm text-slate-500">Loading…</p>}>
            <RealtorResetPasswordForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
