'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

const flyers = [
  {
    id: 'didnt-qualify',
    headline: 'Didn’t Qualify?',
    support: '“Not yet” can still have a clear plan—while your loan officer stays informed.',
    bullets: ['Education', 'Structured tasks', 'Partner updates'],
    cta: 'Talk to your loan officer about Lending Readiness Partners',
  },
  {
    id: 'ninety-days',
    headline: 'Building Toward Mortgage Ready',
    support:
      'Many files need weeks or months—not miracles. Ask about a structured readiness focus period with prioritized tasks.',
    note: 'A structured focus period—not a promise of readiness in 90 days.',
    bullets: ['Prioritized plan', 'Weekly progress framing', 'Dignity-first coaching'],
    cta: 'Ask your LO about Lending Readiness Partners',
  },
  {
    id: 'credit-holding',
    headline: 'Credit Holding You Back?',
    support:
      'Let’s organize the work: utilization, collections, documentation, and next steps—with dignity.',
    bullets: ['Clear next steps', 'Staff-mediated support where needed', 'Claim-safe language'],
    cta: 'Scan the partner kit or ask your LO',
  },
  {
    id: 'homeownership',
    headline: 'Preparing for Homeownership',
    support:
      'Credit education, budgeting habits, and document readiness—so your next financing conversation is clearer.',
    bullets: ['Borrower education', 'Document checklist', 'Partner visibility'],
    cta: 'Start with your loan officer',
  },
  {
    id: 'partner',
    headline: 'Partner With Us',
    support:
      'Mortgage Readiness Partnership for lenders and realtors—advisory progress visibility, staff-mediated process, claim-safe marketing.',
    bullets: ['Pipeline visibility', 'Referral SLA', 'Co-branded leave-behinds'],
    cta: `${siteConfig.url}/lenders`,
  },
];

export default function FlyersPrintPage() {
  return (
    <PrintDocument title="Marketing Flyers (5)" maxWidthClass="max-w-2xl">
      {flyers.map((flyer, index) => (
        <div key={flyer.id}>
          {index > 0 ? <PrintPageBreak /> : null}
          <article className="rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:border-0 print:p-8 print:shadow-none min-h-[10in]">
            <PrintBrandHeader />
            <div className="mt-12 flex flex-col justify-center">
              <h2 className="font-display text-4xl leading-tight text-navy-900">
                {flyer.headline}
              </h2>
              <p className="mt-6 text-lg leading-relaxed text-ink-700">{flyer.support}</p>
              {'note' in flyer && flyer.note ? (
                <p className="mt-3 text-sm font-medium text-gold-800">{flyer.note}</p>
              ) : null}
              <ul className="mt-8 space-y-2 text-base text-ink-700">
                {flyer.bullets.map((b) => (
                  <li key={b} className="flex gap-2">
                    <span className="text-gold-600">▸</span>
                    {b}
                  </li>
                ))}
              </ul>
              <p className="mt-12 rounded-md bg-navy-900 px-5 py-4 text-center text-sm font-semibold text-white">
                {flyer.cta}
              </p>
            </div>
            <footer className="mt-16 border-t border-navy-900/10 pt-4 text-xs text-ink-600">
              {ADVISORY_DISCLAIMER_SHORT}
              <br />
              {siteConfig.tagline} · {siteConfig.email}
            </footer>
          </article>
        </div>
      ))}
    </PrintDocument>
  );
}
