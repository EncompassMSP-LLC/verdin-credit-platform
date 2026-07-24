'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

const chapters = [
  {
    title: 'Understanding credit',
    body: 'Credit is a record of how you have borrowed and repaid money. Mortgage lenders typically review more than one bureau and more than one factor: payment history, utilization, length of history, mix of credit, new credit/inquiries, and public records or collections.',
  },
  {
    title: 'Mortgage score basics',
    body: 'People say “mortgage score” when they mean the credit picture a lender will use. Different products and lenders have different rules. Improving readiness is about habits, documentation, and time—not a magic reset. LRP’s advisory score organizes work; it does not approve loans.',
  },
  {
    title: 'Collections & charge-offs',
    body: 'Confirm the debt is yours, gather documents, and ask your coach before contacting collectors. A charge-off does not mean the debt is gone. Avoid social-media “delete overnight” promises.',
  },
  {
    title: 'Utilization & inquiries',
    body: 'Utilization is how much revolving credit you are using. Know balances and limits; prioritize high-utilization cards. Ask before applying for new credit. Coordinate rate shopping with your LO.',
  },
  {
    title: 'Identity theft',
    body: 'If accounts or inquiries appear that are not yours, document carefully, contact your coach and LO, and use official bureau freeze/fraud processes as advised. Do not post full account numbers in email or chat.',
  },
  {
    title: 'Budgeting & debt payoff',
    body: 'Map income, housing, minimums, essentials, savings, and discretionary spending. Protect on-time payments. Align extra payments with your readiness plan. We do not guarantee any payoff sequence produces a specific score or approval.',
  },
  {
    title: 'Preparing to buy & after approval',
    body: 'Work with your LO on income, assets, employment, housing history, and identity documents. If you receive an approval path from your lender, avoid new credit before closing unless your LO says otherwise, and keep paying every account on time.',
  },
  {
    title: 'Working with your LO & LRP',
    body: 'You own tasks and honesty. Your LO owns the lending path. LRP owns education, readiness plans, updates, and staff-mediated support. Ask “what do you need from me this week?” Celebrate progress without inventing score miracles.',
  },
];

export default function BorrowerGuidePrintPage() {
  return (
    <PrintDocument title="Borrower Readiness Guide">
      <article className="rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:border-0 print:shadow-none">
        <PrintBrandHeader subtitle="Mortgage Readiness Guide for Borrowers" />
        <p className="mt-6 text-sm leading-relaxed text-ink-700">
          This guide explains common credit topics in plain language. It does not promise loan
          approval, a specific score, or a closing date. Your loan officer and lender make lending
          decisions.
        </p>
        <p className="mt-4 text-xs text-ink-500">{ADVISORY_DISCLAIMER_LONG}</p>
      </article>

      {chapters.map((ch, i) => (
        <div key={ch.title}>
          <PrintPageBreak />
          <article className="rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:border-0 print:shadow-none">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
              Chapter {i + 1}
            </p>
            <h2 className="mt-3 font-display text-2xl text-navy-900">{ch.title}</h2>
            <p className="mt-6 text-sm leading-relaxed text-ink-700">{ch.body}</p>
            <footer className="mt-12 border-t border-navy-900/10 pt-3 text-[10px] text-ink-500">
              {siteConfig.tagline} · {ADVISORY_DISCLAIMER_SHORT}
            </footer>
          </article>
        </div>
      ))}
    </PrintDocument>
  );
}
