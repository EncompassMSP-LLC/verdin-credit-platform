import Link from 'next/link';
import { Suspense } from 'react';
import { RealtorLoginForm } from '@/components/realtor/RealtorLoginForm';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Realtor Workspace Login',
  description: 'Sign in to the Lending Readiness Partners realtor workspace.',
  path: '/realtor/login',
  noIndex: true,
});

export default function RealtorLoginPage() {
  return (
    <div className="min-h-screen bg-lrp-surface">
      <div className="mx-auto grid min-h-screen max-w-6xl grid-cols-1 lg:grid-cols-2">
        <section className="relative hidden overflow-hidden bg-[#00133E] px-10 py-16 text-white lg:flex lg:flex-col lg:justify-between">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(194,158,91,0.18),transparent_55%)]"
          />
          <div className="relative">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-400">
              Lending Readiness Partners
            </p>
            <h2 className="mt-4 max-w-md font-sans text-4xl font-semibold uppercase leading-tight tracking-wide">
              Realtor Partner Workspace
            </h2>
            <div className="mt-5 h-px w-24 bg-gold-500" aria-hidden />
            <p className="mt-5 max-w-md font-display text-lg italic text-white/80">
              Track your referred borrowers with coarse status only—no tradelines, dispute letters,
              or lender underwriting surfaces.
            </p>
          </div>
          <ul className="relative space-y-2 text-sm text-white/70">
            <li>Invitation-based activation</li>
            <li>Partnership-isolated referrals</li>
            <li>Separate from lender, borrower, and staff CRM shells</li>
          </ul>
        </section>

        <section className="relative flex items-center px-5 py-14 sm:px-10">
          <div className="mx-auto w-full max-w-md rounded-md border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
              Realtor workspace
            </p>
            <h1 className="mt-2 text-2xl font-semibold text-navy-900">Partner sign in</h1>
            <p className="mt-2 text-sm text-slate-500">
              Access is limited to your realtor partnership membership.
            </p>
            <div className="mt-6">
              <Suspense fallback={<p className="text-sm text-slate-500">Loading sign-in…</p>}>
                <RealtorLoginForm />
              </Suspense>
            </div>
            <Link
              href="/realtors"
              className="mt-6 inline-block text-sm font-medium text-gold-700 hover:underline dark:text-gold-400"
            >
              ← Back to realtor overview
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
