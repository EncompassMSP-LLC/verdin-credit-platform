import Link from 'next/link';
import { Suspense } from 'react';
import { CrmLoginForm } from '@/components/crm/CrmLoginForm';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'CRM Login',
  description: 'Sign in to the Lending Readiness Partners enterprise CRM.',
  path: '/crm/login',
  noIndex: true,
});

export default function CrmLoginPage() {
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
              Enterprise CRM
            </h2>
            <div className="mt-5 h-px w-24 bg-gold-500" aria-hidden />
            <p className="mt-5 max-w-md font-display text-lg italic text-white/80">
              Partners, borrowers, pipeline, automations, and referral attribution—on the shared
              platform, not a forked product.
            </p>
          </div>
          <ul className="relative space-y-2 text-sm text-white/70">
            <li>Relationship directories for partners, lenders, and realtors</li>
            <li>Workflow, tasks, SMS/email, calendar, and documents</li>
            <li>Role-scoped access with enterprise permission matrix</li>
          </ul>
        </section>

        <section className="relative flex items-center px-5 py-14 sm:px-10">
          <div className="mx-auto w-full max-w-md rounded-md border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
              Enterprise CRM
            </p>
            <h1 className="mt-2 text-2xl font-semibold text-navy-900">Sign in</h1>
            <p className="mt-2 text-sm text-slate-500">
              Operator workspace for Lending Readiness Partners.
            </p>
            <div className="mt-6">
              <Suspense fallback={<p className="text-sm text-slate-500">Loading sign-in…</p>}>
                <CrmLoginForm />
              </Suspense>
            </div>
            <Link
              href="/partners"
              className="mt-6 inline-block text-sm font-medium text-gold-700 hover:underline dark:text-gold-400"
            >
              ← Back to partners overview
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
