'use client';

import { PrintBrandHeader, PrintDocument } from '@/components/partner-kit/PrintDocument';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

export default function LoQuickReferencePrintPage() {
  return (
    <PrintDocument title="LO Quick Reference" hideFooter>
      <article className="rounded-lg border border-navy-900/15 bg-white p-8 shadow-soft print:border-0 print:p-0 print:shadow-none">
        <PrintBrandHeader subtitle="Loan Officer Quick Reference" />

        <section className="mt-8">
          <h2 className="font-display text-xl text-navy-900">Referral workflow</h2>
          <ol className="mt-3 list-decimal space-y-1.5 pl-5 text-sm text-ink-700">
            <li>Identify near-miss / “not yet” borrower</li>
            <li>Set expectations: advisory prep—not guaranteed approval</li>
            <li>Submit referral (partner kit referral form)</li>
            <li>Confirm borrower authorization / consent</li>
            <li>Watch for LRP accept / needs-info acknowledgment</li>
            <li>Review weekly digest / portal status</li>
            <li>Re-engage financing conversation when borrower is prepared</li>
          </ol>
        </section>

        <section className="mt-8 grid gap-6 sm:grid-cols-2">
          <div>
            <h2 className="font-display text-lg text-navy-900">Typical timelines</h2>
            <p className="mt-1 text-xs text-ink-500">Directional—not promises</p>
            <ul className="mt-3 space-y-2 text-sm text-ink-700">
              <li>
                <strong>Docs-only:</strong> days–weeks
              </li>
              <li>
                <strong>Utilization / inquiries:</strong> statement cycles–months
              </li>
              <li>
                <strong>Dispute cycles:</strong> bureau / statutory clocks
              </li>
              <li>
                <strong>Complex multi-issue:</strong> often multi-month
              </li>
            </ul>
          </div>
          <div>
            <h2 className="font-display text-lg text-navy-900">Common issues</h2>
            <ul className="mt-3 space-y-2 text-sm text-ink-700">
              <li>Utilization · Collections · Charge-offs</li>
              <li>Inquiries · Late payments · Thin file</li>
              <li>Identity / mixed-file concerns</li>
            </ul>
            <p className="mt-3 text-xs text-ink-500">Do not quote fabricated point impacts.</p>
          </div>
        </section>

        <section className="mt-8 rounded-md bg-sand-100 p-5">
          <h2 className="font-display text-lg text-navy-900">Borrower readiness checklist</h2>
          <ul className="mt-3 grid gap-2 text-sm text-ink-700 sm:grid-cols-2">
            <li>□ Government ID ready</li>
            <li>□ Income path understood</li>
            <li>□ Housing history notes</li>
            <li>□ Credit portals accessible</li>
            <li>□ Known collections listed</li>
            <li>□ Goals / timeline noted</li>
            <li>□ Preferred LO confirmed</li>
            <li>□ Consents signed</li>
          </ul>
        </section>

        <section className="mt-8 grid gap-4 sm:grid-cols-2 text-sm">
          <div className="rounded-md border border-navy-900/10 p-4">
            <h3 className="font-semibold text-navy-900">Talk track — “not yet”</h3>
            <p className="mt-2 text-ink-700">
              “You’re not out of the conversation. I’m connecting you with Lending Readiness
              Partners so you have a clear plan while I stay informed.”
            </p>
          </div>
          <div className="rounded-md border border-navy-900/10 p-4">
            <h3 className="font-semibold text-navy-900">What we never claim</h3>
            <p className="mt-2 text-ink-700">
              Guaranteed approval · Replacing underwriting · Fabricated score outcomes ·
              Unsupervised bureau filing
            </p>
          </div>
        </section>

        <footer className="mt-10 border-t border-navy-900/10 pt-4 text-xs leading-relaxed text-ink-600">
          {ADVISORY_DISCLAIMER_SHORT}
          <br />
          Kit: {siteConfig.url}/resources/partner-kit/phase-3 · Referral: {siteConfig.url}
          /resources/partner-kit/referral
          <br />
          {siteConfig.email} · {siteConfig.phone}
        </footer>
      </article>
    </PrintDocument>
  );
}
