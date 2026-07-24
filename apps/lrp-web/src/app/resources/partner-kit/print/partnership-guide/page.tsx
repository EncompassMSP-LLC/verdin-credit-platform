'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

const pages: { title: string; body: string[] }[] = [
  {
    title: 'Letter from partnerships',
    body: [
      'Thank you for considering a Mortgage Readiness Partnership with Lending Readiness Partners (LRP).',
      'Every week, motivated borrowers pause—not because they lack intent, but because preventable credit and documentation gaps stand between them and a productive financing conversation.',
      'LRP extends your team with advisory readiness support: education, structured plans, staff-mediated workflows where required, and partner visibility—without confusing anyone about who underwrites.',
      'We do not guarantee approval, rates, or funding. We help borrowers prepare for the next financing conversation.',
    ],
  },
  {
    title: 'About us',
    body: [
      'Category: Mortgage Readiness Solutions / AI-powered Borrower Readiness Platform.',
      'For: lenders, loan officers, credit operators, realtors.',
      'Unlike: guarantee-culture credit-repair mills, consumer score apps that over-promise, or tools that try to replace underwriting.',
    ],
  },
  {
    title: 'Why borrowers are declined or delayed',
    body: [
      'High utilization · Recent inquiries · Collections / charge-offs · Thin or young credit · Identity / mixed-file issues · Documentation gaps · Derogatories still reporting.',
      'LRP does not decide eligibility. Lenders and underwriters do. We help borrowers and partners understand the work ahead.',
    ],
  },
  {
    title: 'How our process works',
    body: [
      '1. Refer — LO or realtor sends a near-miss borrower',
      '2. Intake — LRP reviews completeness',
      '3. Plan — Education + prioritized tasks',
      '4. Work — Staff-mediated support where required',
      '5. Update — Partner receives scoped progress',
      '6. Signal — Advisory Lending Readiness Score™ when appropriate',
      '7. Return — Borrower resumes the financing conversation with their LO',
    ],
  },
  {
    title: 'Lending Readiness Score™',
    body: [
      ADVISORY_DISCLAIMER_LONG,
      'Credit is multi-bureau and multi-factor. Underwriting uses overlays and product rules beyond any single number.',
    ],
  },
  {
    title: 'What we can and cannot do',
    body: [
      'Can: educate, build plans, provide partner-visible status, support staff-reviewed dispute workflows, prepare files for partner-requested rescore conversations.',
      'Cannot: guarantee score changes or loan approval, replace underwriting, promise closing dates, file unsupervised with bureaus, sell borrower lists across tenants.',
    ],
  },
  {
    title: 'Compliance & consumer protection',
    body: [
      'High-risk actions are staff-mediated. Public copy follows the claim library. No unsupervised bureau filing. Audit trails for partner access. Privacy minimization in digests. Co-branded marketing requires LRP review.',
    ],
  },
  {
    title: 'Timeline expectations',
    body: [
      'Documentation-only gaps: often days to a few weeks. Utilization / inquiry timing: statement cycles to months. Dispute cycles: statutory and bureau timelines. Complex files: multi-month structured work is common.',
      'Script: “We’ll prioritize the work and keep you updated. Timelines depend on the file—not a guaranteed calendar.”',
    ],
  },
  {
    title: 'FAQ',
    body: [
      'How long? It depends—we set priorities and update on a cadence. No guaranteed dates.',
      'Cost? Reviewed in the briefing—no miracle pricing claims.',
      'Guarantee results? No. We do not guarantee score changes, approvals, or funding.',
      'Delay closing? If a borrower is not ready, rushing can create more harm. We prepare—we do not force calendars.',
      'Replace underwriter? No. We support readiness. Your team underwrites.',
    ],
  },
  {
    title: 'How to start',
    body: [
      `Briefing: ${siteConfig.url}/contact?intent=lender`,
      `Lender overview: ${siteConfig.url}/lenders`,
      `Partner workspace: ${siteConfig.url}/lender/login`,
      `Digital kit: ${siteConfig.url}/resources/partner-kit/phase-3`,
      `Referral form: ${siteConfig.url}/resources/partner-kit/referral`,
    ],
  },
];

export default function PartnershipGuidePrintPage() {
  return (
    <PrintDocument title="Partnership Guide">
      <article className="rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:border-0 print:shadow-none">
        <PrintBrandHeader subtitle="Mortgage Partnership Guide" />
        <p className="mt-8 text-sm text-ink-600">
          Leave-behind for lender and LO meetings · Confidential
        </p>
        <p className="mt-4 text-xs text-ink-500">{ADVISORY_DISCLAIMER_SHORT}</p>
      </article>

      {pages.map((page, i) => (
        <div key={page.title}>
          <PrintPageBreak />
          <article className="rounded-lg border border-navy-900/15 bg-white p-10 shadow-soft print:border-0 print:shadow-none">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
              Page {i + 2}
            </p>
            <h2 className="mt-3 font-display text-2xl text-navy-900">{page.title}</h2>
            <div className="mt-6 space-y-4 text-sm leading-relaxed text-ink-700">
              {page.body.map((para) => (
                <p key={para.slice(0, 40)}>{para}</p>
              ))}
            </div>
            <footer className="mt-12 border-t border-navy-900/10 pt-3 text-[10px] text-ink-500">
              Lending Readiness Partners · {siteConfig.tagline} · {ADVISORY_DISCLAIMER_SHORT}
            </footer>
          </article>
        </div>
      ))}
    </PrintDocument>
  );
}
