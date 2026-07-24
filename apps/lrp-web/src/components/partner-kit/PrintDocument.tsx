'use client';

import Image from 'next/image';
import Link from 'next/link';
import type { ReactNode } from 'react';
import { Container } from '@/components/ui/Container';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { siteConfig } from '@/lib/site';

type PrintDocumentProps = {
  title: string;
  backHref?: string;
  backLabel?: string;
  children: ReactNode;
  /** Hide default brand footer (page supplies its own). */
  hideFooter?: boolean;
  maxWidthClass?: string;
};

/**
 * Browser → PDF shell for Phase 3 partner collateral.
 * Use the Print button or Ctrl/Cmd+P; print CSS hides chrome.
 */
export function PrintDocument({
  title,
  backHref = '/resources/partner-kit/phase-3',
  backLabel = '← Phase 3 kit',
  children,
  hideFooter = false,
  maxWidthClass = 'max-w-3xl',
}: PrintDocumentProps) {
  return (
    <div className="min-h-screen bg-sand-50 py-10 print:bg-white print:py-0">
      <Container className={maxWidthClass}>
        <div className="mb-6 flex flex-wrap items-center gap-4 print:hidden">
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700"
          >
            Print / Save as PDF
          </button>
          <Link href={backHref} className="text-sm text-teal-700 hover:underline">
            {backLabel}
          </Link>
          <span className="text-xs text-ink-500">{title}</span>
        </div>
        {children}
        {hideFooter ? null : (
          <p className="mt-8 text-center text-[10px] leading-relaxed text-ink-500 print:mt-6">
            Lending Readiness Partners · {siteConfig.tagline}
            <br />
            {ADVISORY_DISCLAIMER_SHORT}
          </p>
        )}
      </Container>
    </div>
  );
}

export function PrintBrandHeader({
  eyebrow = 'Mortgage Readiness Partnership',
  subtitle,
}: {
  eyebrow?: string;
  subtitle?: string;
}) {
  return (
    <header className="border-b border-gold-500/40 pb-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">{eyebrow}</p>
          <h1 className="mt-3 font-sans text-2xl font-semibold uppercase tracking-[0.06em] text-navy-900 sm:text-3xl">
            Lending Readiness Partners
          </h1>
          {subtitle ? <p className="mt-2 text-base font-medium text-navy-800">{subtitle}</p> : null}
          <p className="mt-3 font-display text-lg italic text-ink-700">{siteConfig.tagline}</p>
        </div>
        <Image
          src="/brand/logo-stacked-on-ivory.png"
          alt="Lending Readiness Partners"
          width={120}
          height={120}
          className="h-20 w-auto object-contain"
          priority
        />
      </div>
    </header>
  );
}

export function PrintPageBreak() {
  return (
    <div className="my-10 border-t border-dashed border-navy-900/20 print:my-0 print:break-before-page print:border-0" />
  );
}
