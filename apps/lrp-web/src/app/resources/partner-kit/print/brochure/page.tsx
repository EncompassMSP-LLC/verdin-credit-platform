'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

export default function BrochurePrintPage() {
  return (
    <PrintDocument title="Company Brochure" maxWidthClass="max-w-5xl">
      <p className="mb-6 text-sm text-ink-600 print:hidden">
        Digital brochure panels — print as a multi-page PDF or fold as a tri-fold mockup.
      </p>

      {/* Cover */}
      <article className="flex min-h-[9in] flex-col justify-between rounded-lg bg-navy-900 p-12 text-white print:rounded-none">
        <div>
          <p className="text-xs uppercase tracking-eyebrow text-gold-400">
            Mortgage Readiness Program
          </p>
          <h1 className="mt-8 font-sans text-3xl font-semibold uppercase tracking-[0.06em]">
            Lending Readiness Partners
          </h1>
          <p className="mt-6 font-display text-xl italic text-gold-300">{siteConfig.tagline}</p>
          <p className="mt-4 max-w-md text-sm text-white/80">
            Education, strategy, and progress for the next financing opportunity.
          </p>
        </div>
        <p className="text-xs text-white/60">{siteConfig.url}/lenders</p>
      </article>

      <PrintPageBreak />

      <article className="grid gap-8 rounded-lg border border-navy-900/15 bg-white p-10 md:grid-cols-3 print:border-0">
        <section>
          <h2 className="font-display text-lg text-navy-900">Why partner</h2>
          <ul className="mt-4 list-disc space-y-2 pl-4 text-sm text-ink-700">
            <li>Priority mortgage-intent referrals</li>
            <li>Personalized credit & documentation plans</li>
            <li>Regular partner progress updates</li>
            <li>Advisory readiness—not underwriting</li>
            <li>Secure borrower & partner portals</li>
          </ul>
        </section>
        <section>
          <h2 className="font-display text-lg text-navy-900">How it works</h2>
          <ol className="mt-4 list-decimal space-y-2 pl-4 text-sm text-ink-700">
            <li>Borrower referred</li>
            <li>Gaps identified</li>
            <li>Plan & education begin</li>
            <li>Partner updates</li>
            <li>Advisory Lending Ready signal</li>
            <li>Return to LO</li>
          </ol>
        </section>
        <section>
          <h2 className="font-display text-lg text-navy-900">What you get</h2>
          <ul className="mt-4 list-disc space-y-2 pl-4 text-sm text-ink-700">
            <li>Referral status you can explain</li>
            <li>Borrower tasks in a portal</li>
            <li>Staff-mediated dispute support</li>
            <li>Claim-safe co-marketing</li>
          </ul>
          <p className="mt-6 text-sm font-medium text-navy-900">
            We support readiness. Your team underwrites.
          </p>
        </section>
      </article>

      <PrintPageBreak />

      <article className="rounded-lg border border-navy-900/15 bg-white p-10 print:border-0">
        <PrintBrandHeader subtitle="When “not yet” needs a plan" />
        <p className="mt-6 text-sm leading-relaxed text-ink-700">
          Motivated borrowers stall when credit and documentation gaps are unclear. Lending
          Readiness Partners helps organize the path forward—while keeping loan officers and
          realtors informed.
        </p>
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          <div className="rounded-md bg-sand-100 p-4 text-sm">
            <p className="font-semibold text-navy-900">Book a briefing</p>
            <p className="mt-2 break-all text-xs">{siteConfig.url}/contact?intent=lender</p>
          </div>
          <div className="rounded-md bg-sand-100 p-4 text-sm">
            <p className="font-semibold text-navy-900">Digital kit</p>
            <p className="mt-2 break-all text-xs">{siteConfig.url}/resources/partner-kit/phase-3</p>
          </div>
        </div>
        <footer className="mt-10 text-xs text-ink-600">{ADVISORY_DISCLAIMER_SHORT}</footer>
      </article>
    </PrintDocument>
  );
}
