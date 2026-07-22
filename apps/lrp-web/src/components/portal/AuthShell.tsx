import type { ReactNode } from 'react';
import { AdvisoryDisclaimer } from '@/components/ui/AdvisoryDisclaimer';

export function AuthShell({
  children,
  title,
  subtitle,
}: {
  children: ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="min-h-screen bg-lrp-surface">
      <div className="mx-auto grid min-h-screen max-w-6xl grid-cols-1 lg:grid-cols-2">
        <section className="relative hidden overflow-hidden bg-path-gradient px-10 py-16 text-white lg:flex lg:flex-col lg:justify-between">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(194,158,91,0.2),transparent_50%)]"
          />
          <div className="relative">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-400">
              Borrower Portal
            </p>
            <h2 className="mt-4 max-w-md font-sans text-4xl font-semibold uppercase leading-tight tracking-wide">
              {title}
            </h2>
            <div className="mt-5 h-px w-24 bg-gold-500" aria-hidden />
            <p className="mt-5 max-w-md font-display text-lg italic text-white/80">{subtitle}</p>
          </div>
          <div className="relative space-y-4">
            <ul className="space-y-2 text-sm text-white/70">
              <li>Readiness score & blockers</li>
              <li>Tasks, documents, and messages</li>
              <li>Staff-mediated dispute visibility</li>
            </ul>
            <AdvisoryDisclaimer variant="footer" />
          </div>
        </section>

        <section className="relative flex items-center px-5 py-14 sm:px-10">
          <div className="mx-auto w-full max-w-md rounded-brand border border-lrp-border bg-lrp-surface-elevated p-6 shadow-soft sm:p-8">
            {children}
          </div>
        </section>
      </div>
    </div>
  );
}
