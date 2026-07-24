'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

export default function WelcomePacketPrintPage() {
  return (
    <PrintDocument title="Welcome Packet">
      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:shadow-none">
        <PrintBrandHeader subtitle="Partner Welcome Packet" />
        <section className="mt-8 prose-sm max-w-none text-ink-700">
          <h2 className="font-display text-xl text-navy-900">Welcome letter</h2>
          <p className="mt-3 text-sm leading-relaxed">
            Welcome to the Mortgage Readiness Partnership with Lending Readiness Partners (LRP). You
            referred us because motivated borrowers sometimes need a clearer path when today’s
            answer is “not yet.” Our role is to help those borrowers organize credit education,
            documentation, and next steps—while keeping your team visible on progress.
          </p>
          <p className="mt-3 text-sm leading-relaxed">
            We are an extension of your team for advisory readiness support. We are not a substitute
            for underwriting, credit decisioning, or loan approval.
          </p>
        </section>
      </article>

      <PrintPageBreak />

      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:shadow-none">
        <h2 className="font-display text-xl text-navy-900">Who we are</h2>
        <p className="mt-3 text-sm leading-relaxed text-ink-700">
          Lending Readiness Partners is a Mortgage Readiness Solutions provider. We help credit
          operators, lenders, loan officers, and realtors give near-miss borrowers a dignified,
          structured path toward the next financing conversation.
        </p>
        <h3 className="mt-8 text-sm font-semibold uppercase tracking-eyebrow text-gold-700">
          Mission
        </h3>
        <p className="mt-2 text-sm text-ink-700">
          Help more borrowers become lending ready—through education, structured work, and partner
          visibility—without guarantee culture.
        </p>
        <h3 className="mt-8 text-sm font-semibold uppercase tracking-eyebrow text-gold-700">
          Values
        </h3>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-ink-700">
          <li>Dignity first — “not yet” with a plan</li>
          <li>Partner trust — clear SLAs, scoped data</li>
          <li>Compliance-minded ops — staff-mediated high-risk actions</li>
          <li>Clarity over hype — advisory scores only</li>
          <li>Shared accountability — borrowers work; lenders decide</li>
        </ul>
      </article>

      <PrintPageBreak />

      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:shadow-none">
        <h2 className="font-display text-xl text-navy-900">What to expect</h2>
        <table className="mt-4 w-full text-left text-sm text-ink-700">
          <thead>
            <tr className="border-b border-navy-900/15 text-navy-900">
              <th className="py-2 pr-4">Cadence</th>
              <th className="py-2">What you receive</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-navy-900/10">
              <td className="py-2 pr-4 font-medium">Per referral</td>
              <td className="py-2">Accept / decline acknowledgment</td>
            </tr>
            <tr className="border-b border-navy-900/10">
              <td className="py-2 pr-4 font-medium">Weekly</td>
              <td className="py-2">Progress digest (PII minimized)</td>
            </tr>
            <tr className="border-b border-navy-900/10">
              <td className="py-2 pr-4 font-medium">As needed</td>
              <td className="py-2">Escalations when borrower stalls</td>
            </tr>
            <tr>
              <td className="py-2 pr-4 font-medium">Quarterly</td>
              <td className="py-2">Partnership review</td>
            </tr>
          </tbody>
        </table>

        <h3 className="mt-10 font-display text-lg text-navy-900">Service boundaries</h3>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 text-sm">
          <div className="rounded-md bg-sand-100 p-4">
            <p className="font-semibold text-navy-900">We can</p>
            <ul className="mt-2 list-disc space-y-1 pl-4 text-ink-700">
              <li>Educate and organize readiness work</li>
              <li>Provide advisory readiness signals</li>
              <li>Support staff-reviewed dispute workflows</li>
              <li>Share scoped progress with partners</li>
            </ul>
          </div>
          <div className="rounded-md bg-sand-100 p-4">
            <p className="font-semibold text-navy-900">We cannot</p>
            <ul className="mt-2 list-disc space-y-1 pl-4 text-ink-700">
              <li>Guarantee scores, approvals, or closing dates</li>
              <li>Replace underwriting or AUS</li>
              <li>File unsupervised with bureaus</li>
              <li>Operate a cross-tenant marketplace</li>
            </ul>
          </div>
        </div>

        <footer className="mt-10 border-t border-navy-900/10 pt-4 text-xs text-ink-600">
          {ADVISORY_DISCLAIMER_SHORT}
          <br />
          Partner workspace: {siteConfig.url}/lender/login · Kit: {siteConfig.url}
          /resources/partner-kit/phase-3
        </footer>
      </article>
    </PrintDocument>
  );
}
