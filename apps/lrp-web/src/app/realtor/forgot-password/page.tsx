import { RealtorForgotPasswordForm } from '@/components/realtor/RealtorPasswordForms';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Realtor Password Reset',
  description: 'Request a password reset for your realtor workspace account.',
  path: '/realtor/forgot-password',
  noIndex: true,
});

export default function RealtorForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-lrp-surface px-5 py-14">
      <div className="w-full max-w-md rounded-md border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
        <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
          Realtor workspace
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-navy-900">Forgot password</h1>
        <p className="mt-2 text-sm text-slate-500">
          We issue a reset only for active realtor partnership memberships.
        </p>
        <div className="mt-6">
          <RealtorForgotPasswordForm />
        </div>
      </div>
    </div>
  );
}
