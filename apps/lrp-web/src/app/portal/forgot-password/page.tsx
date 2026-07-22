import Link from 'next/link';
import { AuthShell } from '@/components/portal/AuthShell';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Reset Portal Password',
  description:
    'Password resets for borrower portal accounts are handled by your readiness partner.',
  path: '/portal/forgot-password',
  noIndex: true,
});

export default function ForgotPasswordPage() {
  return (
    <AuthShell
      title="Password help"
      subtitle="Portal passwords are managed through your partner’s staff tools on the shared platform."
    >
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold text-navy-900 dark:text-white">
          Reset your password
        </h1>
        <p className="text-sm text-slate-500 dark:text-white/65">
          Self-serve email reset is not enabled on the platform portal JWT realm yet. Contact your
          case manager or operator and ask them to update your portal password on your Client
          record.
        </p>
        <Link
          href="/portal/login"
          className="inline-flex rounded-brand bg-gold-500 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400"
        >
          Back to sign in
        </Link>
      </div>
    </AuthShell>
  );
}
