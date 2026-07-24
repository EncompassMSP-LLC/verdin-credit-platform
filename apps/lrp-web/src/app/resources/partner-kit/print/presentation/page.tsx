'use client';

import { PrintDocument, PrintPageBreak } from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

const slides = [
  {
    title: 'Lending Readiness Partners',
    body: `Mortgage Readiness Partnership\n${siteConfig.tagline}`,
  },
  { title: 'Agenda', body: 'Opportunity · Model · Benefits · Journey · Compliance · Next steps' },
  {
    title: 'Company overview',
    body: 'Mortgage Readiness Solutions for lenders, LOs, operators, and realtors.',
  },
  { title: 'The near-miss problem', body: 'Relationships walk when “not yet” has no plan.' },
  { title: 'Who we serve', body: 'Lenders · LOs · Realtors · Borrowers · Operators' },
  { title: 'Partnership model', body: 'Refer → Plan → Update → Return' },
  { title: 'What partners see', body: 'Pipeline, digests, portal—scoped and auditable.' },
  { title: 'What borrowers experience', body: 'Education, tasks, dignity-first coaching.' },
  { title: 'Lending Readiness Score™', body: ADVISORY_DISCLAIMER_SHORT },
  { title: 'Benefits for lenders', body: 'Retention, clarity, claim-safe channel.' },
  { title: 'Benefits for LOs', body: 'Specialist path without becoming a repair shop.' },
  { title: 'Client journey', body: 'Swimlane: LO / Borrower / LRP' },
  { title: 'Timeline expectations', body: 'Directional ranges—never promised calendars.' },
  { title: 'Compliance posture', body: 'Staff-mediated · claim library · no unsupervised filing' },
  { title: 'Consumer protection', body: 'Privacy · consents · audit trails' },
  { title: 'Case vignette A', body: 'Fictional composite—process story only. No fabricated FICO.' },
  { title: 'Case vignette B', body: 'Fictional composite—shared vocabulary, dignity-first.' },
  { title: 'Objections', body: 'Guarantees / timing / cost — see sales playbook.' },
  { title: 'Pilot shape', body: '90-day design partner: seats, digests, first referrals.' },
  { title: 'Onboarding', body: 'Kickoff → partnership record → LO seats → live referrals' },
  { title: 'Digital kit & portal', body: `${siteConfig.url}/resources/partner-kit/phase-3` },
  {
    title: 'Pricing discussion',
    body: 'Reviewed live / under NDA—transparent, no miracle packages.',
  },
  { title: 'Q&A', body: 'Questions welcome. We stay claim-safe.' },
  { title: 'Close', body: `${siteConfig.email} · ${siteConfig.phone}\n${siteConfig.tagline}` },
  {
    title: 'Disclaimer',
    body: `${ADVISORY_DISCLAIMER_SHORT}\nWe do not guarantee loan approval, terms, or funding.`,
  },
];

export default function PresentationPrintPage() {
  return (
    <PrintDocument title="Partner Presentation (~25 slides)" maxWidthClass="max-w-4xl">
      <p className="mb-6 text-sm text-ink-600 print:hidden">
        Present full-screen in the browser, or Print → Save as PDF for a leave-behind deck.
      </p>
      {slides.map((slide, i) => (
        <div key={`${slide.title}-${i}`}>
          {i > 0 ? <PrintPageBreak /> : null}
          <article className="flex min-h-[7.5in] flex-col justify-between rounded-lg border border-navy-900/15 bg-white p-12 shadow-soft print:min-h-[7in] print:border-0 print:shadow-none">
            <div>
              <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
                Slide {i + 1} / {slides.length}
              </p>
              <h2 className="mt-8 font-display text-3xl text-navy-900">{slide.title}</h2>
              <p className="mt-8 whitespace-pre-line text-lg leading-relaxed text-ink-700">
                {slide.body}
              </p>
            </div>
            <p className="text-xs text-ink-400">Lending Readiness Partners</p>
          </article>
        </div>
      ))}
    </PrintDocument>
  );
}
