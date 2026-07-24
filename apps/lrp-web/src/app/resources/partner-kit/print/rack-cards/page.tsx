'use client';

import { PrintDocument, PrintPageBreak } from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

const cards = [
  {
    audience: 'Lender / LO',
    headline: 'Keep more borrowers in the conversation',
    support: 'Mortgage Readiness Partnership—advisory plans and partner visibility.',
    back: 'Refer → Plan → Update → Return. We support readiness. Your team underwrites.',
    href: `${siteConfig.url}/lenders`,
  },
  {
    audience: 'Realtor',
    headline: 'When financing needs more time',
    support:
      'Keep buyers engaged with a dignity-first readiness path alongside your preferred lender.',
    back: 'Shared stages. No shame narratives. Claim-safe scripts your agents can defend.',
    href: `${siteConfig.url}/realtors`,
  },
  {
    audience: 'Borrower',
    headline: 'A clear plan for “not yet”',
    support: 'Education and next steps toward your next financing conversation.',
    back: 'Ask your loan officer about Lending Readiness Partners. No approval promises—just a plan.',
    href: `${siteConfig.url}/resources/partner-kit/phase-3`,
  },
];

export default function RackCardsPrintPage() {
  return (
    <PrintDocument title="Rack Cards (4×9)" maxWidthClass="max-w-4xl">
      <p className="mb-6 text-sm text-ink-600 print:hidden">
        Each card is sized for a 4″×9″ rack insert. Print double-sided; trim to size.
      </p>
      {cards.map((card, index) => (
        <div key={card.audience}>
          {index > 0 ? <PrintPageBreak /> : null}
          <div className="grid gap-8 md:grid-cols-2 print:gap-4">
            {/* Front */}
            <article className="mx-auto flex w-full max-w-[4in] flex-col justify-between rounded-lg border border-navy-900/20 bg-navy-900 p-6 text-white shadow-soft print:min-h-[9in] print:rounded-none print:shadow-none">
              <div>
                <p className="text-[10px] font-medium uppercase tracking-eyebrow text-gold-400">
                  {card.audience}
                </p>
                <h2 className="mt-6 font-display text-2xl leading-snug">{card.headline}</h2>
                <p className="mt-4 text-sm leading-relaxed text-white/85">{card.support}</p>
              </div>
              <div>
                <p className="font-display text-sm italic text-gold-300">{siteConfig.tagline}</p>
                <p className="mt-4 text-[10px] text-white/60">Lending Readiness Partners</p>
              </div>
            </article>
            {/* Back */}
            <article className="mx-auto flex w-full max-w-[4in] flex-col justify-between rounded-lg border border-navy-900/15 bg-white p-6 shadow-soft print:min-h-[9in] print:rounded-none print:shadow-none">
              <div>
                <p className="text-[10px] font-medium uppercase tracking-eyebrow text-gold-700">
                  How it works
                </p>
                <p className="mt-6 text-sm leading-relaxed text-ink-700">{card.back}</p>
                <p className="mt-6 break-all text-xs text-teal-800">{card.href}</p>
              </div>
              <p className="text-[9px] leading-relaxed text-ink-500">{ADVISORY_DISCLAIMER_SHORT}</p>
            </article>
          </div>
        </div>
      ))}
    </PrintDocument>
  );
}
