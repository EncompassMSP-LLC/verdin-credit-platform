import Link from 'next/link';
import { AuthShell } from '@/components/portal/AuthShell';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Request Portal Access',
  description: 'Borrower portal accounts are provisioned by your credit readiness partner.',
  path: '/portal/signup',
  noIndex: true,
});

export default function PortalSignupPage() {
  return (
    <AuthShell
      title="Access is partner-provisioned."
      subtitle="For security and compliance, borrower accounts are created by staff—not self-serve signup."
    >
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold text-navy-900 dark:text-white">
          Request borrower access
        </h1>
        <p className="text-sm text-slate-500 dark:text-white/65">
          Your credit operator or lender partner provisions a portal user on your client record in
          the Ultimate Credit Repair platform. Once issued, sign in here with that email and
          password.
        </p>
        <ol className="list-decimal space-y-2 pl-5 text-sm text-slate-500 dark:text-white/65">
          <li>Ask your advisor to open your Client record.</li>
          <li>Have them create Portal credentials (Client → Portal user).</li>
          <li>
            Confirm <code className="text-navy-900 dark:text-white">ENABLE_CLIENT_PORTAL=true</code>{' '}
            on the API.
          </li>
          <li>Return to sign in.</li>
        </ol>
        <div className="flex flex-col gap-2 pt-2">
          <Link
            href="/portal/login"
            className="inline-flex items-center justify-center rounded-brand bg-gold-500 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400"
          >
            Go to sign in
          </Link>
          <Link href="/contact" className="text-sm text-gold-700 dark:text-gold-400">
            Contact Lending Readiness Partners
          </Link>
        </div>
      </div>
    </AuthShell>
  );
}
