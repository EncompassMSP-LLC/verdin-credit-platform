'use client';

import Link from 'next/link';
import { Container } from '@/components/ui/Container';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

/**
 * Print-optimized LO leave-behind.
 * Spec: Vol 07 partner-kit phase-2/17-leave-behind-folder.md
 */
export default function LeaveBehindPrintPage() {
  return (
    <div className="min-h-screen bg-sand-50 py-10 print:bg-white print:py-0">
      <Container className="max-w-3xl">
        <div className="mb-6 flex flex-wrap items-center gap-4 print:hidden">
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white"
          >
            Print leave-behind
          </button>
          <Link
            href="/resources/partner-kit/phase-2"
            className="text-sm text-teal-700 hover:underline"
          >
            ← Phase 2 hub
          </Link>
        </div>

        <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:p-0 print:shadow-none">
          <header className="border-b border-gold-500/40 pb-6">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
              Mortgage Readiness Partnership
            </p>
            <h1 className="mt-3 font-sans text-3xl font-semibold uppercase tracking-[0.06em] text-navy-900">
              Lending Readiness Partners
            </h1>
            <p className="mt-3 font-display text-lg italic text-ink-700">{siteConfig.tagline}</p>
          </header>

          <section className="mt-8">
            <h2 className="font-display text-xl text-navy-900">For loan officers</h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-700">
              When a borrower is not ready yet, refer them for a clear plan—and stay informed on
              progress. We support advisory readiness, education, and staff-mediated workflows—not
              underwriting decisions.
            </p>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-ink-700">
              <li>Dedicated mortgage specialist</li>
              <li>Partner-visible progress updates</li>
              <li>Borrower portal for tasks and documents</li>
              <li>Claim-safe communication your compliance team can defend</li>
            </ul>
          </section>

          <section className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-md bg-sand-100 p-4">
              <h3 className="text-sm font-semibold text-navy-900">Full partner kit</h3>
              <p className="mt-2 break-all text-xs text-ink-700">
                {siteConfig.url}/resources/partner-kit
              </p>
            </div>
            <div className="rounded-md bg-sand-100 p-4">
              <h3 className="text-sm font-semibold text-navy-900">Refer a borrower</h3>
              <p className="mt-2 break-all text-xs text-ink-700">
                {siteConfig.url}/resources/partner-kit/referral
              </p>
            </div>
          </section>

          <footer className="mt-10 border-t border-navy-900/10 pt-4 text-xs leading-relaxed text-ink-600">
            {ADVISORY_DISCLAIMER_SHORT} We do not guarantee loan approval, terms, or funding.
            <br />
            {siteConfig.email} · {siteConfig.phone}
          </footer>
        </article>
      </Container>
    </div>
  );
}
