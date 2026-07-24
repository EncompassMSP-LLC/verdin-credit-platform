'use client';

import {
  PrintBrandHeader,
  PrintDocument,
  PrintPageBreak,
} from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

export default function SalesPlaybookPrintPage() {
  return (
    <PrintDocument title="Sales Scripts & Objections">
      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:shadow-none">
        <PrintBrandHeader subtitle="Sales Scripts & Objection Handling" />

        <h2 className="mt-8 font-display text-xl text-navy-900">Elevator pitch (15 sec)</h2>
        <p className="mt-3 text-sm text-ink-700">
          “Lending Readiness Partners helps more borrowers become lending ready—with advisory plans
          and partner updates—without guarantee culture.”
        </p>

        <h2 className="mt-8 font-display text-xl text-navy-900">Cold call open</h2>
        <p className="mt-3 text-sm text-ink-700">
          “Hi [Name], this is [You] with Lending Readiness Partners. We help loan officers keep
          near-miss borrowers in the conversation with a structured mortgage readiness plan—and
          partner visibility. Do you have two minutes?”
        </p>

        <h2 className="mt-8 font-display text-xl text-navy-900">Voicemail</h2>
        <p className="mt-3 text-sm text-ink-700">
          “Hi [Name], [You] with Lending Readiness Partners. We partner with loan officers on
          mortgage readiness—advisory plans when the answer is ‘not yet,’ with progress updates for
          your team. I’ll email a leave-behind. My number is [phone].”
        </p>
      </article>

      <PrintPageBreak />

      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:shadow-none">
        <h2 className="font-display text-xl text-navy-900">Objection responses</h2>
        <dl className="mt-6 space-y-6 text-sm text-ink-700">
          <div>
            <dt className="font-semibold text-navy-900">“How long will this take?”</dt>
            <dd className="mt-1">
              It depends on the file. We prioritize tasks and keep you updated on a set cadence. We
              don’t guarantee a calendar date.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-navy-900">“How much does it cost?”</dt>
            <dd className="mt-1">
              Partnership and consumer engagement terms are reviewed in the briefing so we match
              scope. We’re transparent; we don’t sell miracle packages.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-navy-900">“Can you guarantee results?”</dt>
            <dd className="mt-1">
              No—and you should be cautious of anyone who does. We don’t guarantee score changes,
              approvals, or funding.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-navy-900">“Why shouldn’t I use another company?”</dt>
            <dd className="mt-1">
              Evaluate fit. We emphasize partner visibility, advisory readiness—not underwriting
              cosplay—and compliance-minded communication.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-navy-900">“Will this delay my closing?”</dt>
            <dd className="mt-1">
              If a borrower isn’t ready, forcing an application can create worse outcomes. Our job
              is preparation—not sitting on a clear-to-close file.
            </dd>
          </div>
        </dl>
        <footer className="mt-10 border-t border-navy-900/10 pt-4 text-xs text-ink-600">
          {ADVISORY_DISCLAIMER_SHORT}
          <br />
          Kit: {siteConfig.url}/resources/partner-kit/phase-3
        </footer>
      </article>
    </PrintDocument>
  );
}
