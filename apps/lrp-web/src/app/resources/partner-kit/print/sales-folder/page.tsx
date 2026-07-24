'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

export default function SalesFolderPrintPage() {
  return (
    <PrintDocument title="Sales Presentation Folder" maxWidthClass="max-w-4xl">
      {/* Front cover */}
      <article className="flex min-h-[11in] flex-col justify-between rounded-lg bg-navy-900 p-12 text-white shadow-soft print:min-h-[10in] print:rounded-none print:shadow-none">
        <div>
          <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-400">
            Mortgage Readiness Partnership
          </p>
          <h1 className="mt-8 font-sans text-4xl font-semibold uppercase tracking-[0.08em]">
            Lending Readiness Partners
          </h1>
          <p className="mt-6 font-display text-2xl italic text-gold-300">{siteConfig.tagline}</p>
        </div>
        <div className="border-t border-white/20 pt-6">
          <p className="text-sm text-white/80">Scan for digital partner kit</p>
          <p className="mt-2 break-all text-xs text-gold-300">
            {siteConfig.url}/resources/partner-kit/phase-3
          </p>
        </div>
      </article>

      <PrintPageBreak />

      {/* Back cover */}
      <article className="min-h-[11in] rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:min-h-[10in] print:border-0 print:shadow-none">
        <PrintBrandHeader />
        <h2 className="mt-10 font-display text-2xl text-navy-900">Why partners choose LRP</h2>
        <ul className="mt-6 space-y-4 text-sm text-ink-700">
          <li>
            <strong className="text-navy-900">A clear plan</strong> when the answer today is “not
            yet.”
          </li>
          <li>
            <strong className="text-navy-900">Progress visibility</strong> for loan officers—without
            underwriting confusion.
          </li>
          <li>
            <strong className="text-navy-900">Staff-mediated process</strong> with claim-safe
            communication.
          </li>
        </ul>
        <div className="mt-12 rounded-md bg-sand-100 p-5 text-sm text-ink-700">
          <p className="font-semibold text-navy-900">Partnerships</p>
          <p className="mt-2">
            {siteConfig.email} · {siteConfig.phone}
          </p>
          <p className="mt-1 break-all">{siteConfig.url}/contact?intent=lender</p>
        </div>
        <footer className="mt-10 text-xs text-ink-600">{ADVISORY_DISCLAIMER_SHORT}</footer>
      </article>

      <PrintPageBreak />

      {/* Inside flaps */}
      <article className="grid min-h-[11in] gap-8 rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft md:grid-cols-2 print:min-h-[10in] print:border-0 print:shadow-none">
        <div>
          <h2 className="font-display text-xl text-navy-900">What’s inside</h2>
          <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-ink-700">
            <li>Welcome letter</li>
            <li>Company brochure</li>
            <li>Loan officer quick reference</li>
            <li>Partnership guide</li>
            <li>Referral flyer / form</li>
            <li>Mortgage readiness checklist</li>
            <li>Business card</li>
          </ol>
          <p className="mt-8 text-xs text-ink-500">{ADVISORY_DISCLAIMER_SHORT}</p>
        </div>
        <div>
          <h2 className="font-display text-xl text-navy-900">How partnership works</h2>
          <ol className="mt-4 space-y-3 text-sm text-ink-700">
            <li>
              <strong>1. Refer</strong> — LO sends near-miss borrower
            </li>
            <li>
              <strong>2. Plan</strong> — Staff builds advisory readiness plan
            </li>
            <li>
              <strong>3. Update</strong> — Partner sees progress
            </li>
            <li>
              <strong>4. Return</strong> — Borrower resumes financing conversation when prepared
            </li>
          </ol>
          <p className="mt-8 rounded-md bg-navy-900/5 p-4 text-sm font-medium text-navy-900">
            We support readiness. Your team underwrites.
          </p>
        </div>
      </article>
    </PrintDocument>
  );
}
