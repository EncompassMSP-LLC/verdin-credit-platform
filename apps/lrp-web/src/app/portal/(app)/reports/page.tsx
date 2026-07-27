'use client';

import Link from 'next/link';
import { useState } from 'react';
import { getAccessToken, getPortalCaseReadinessReportExportUrl } from '@verdin/api-client';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { usePrimaryCase } from '@/lib/platform/hooks';
import { usePortalReadinessReport } from '@/lib/platform/readiness-hooks';
import { readinessBandClass, readinessBandLabel } from '@/lib/portal/readiness-display';
import { formatDate } from '@/lib/utils';

/**
 * Spec: Vol 19 · pages/reports.md + LRP-106 readiness report view/export.
 * Band-first; borrower download of advisory text/PDF (no bureau raw PDFs).
 */
export default function PortalReportsPage() {
  const { primary } = usePrimaryCase();
  const reportQuery = usePortalReadinessReport(primary?.id);
  const report = reportQuery.data;
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<'text' | 'pdf' | null>(null);

  async function download(format: 'text' | 'pdf') {
    if (!primary?.id) return;
    setDownloadError(null);
    setDownloading(format);
    try {
      const token = getAccessToken();
      const url = getPortalCaseReadinessReportExportUrl(primary.id, format);
      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) {
        throw new Error(`Export failed (${response.status})`);
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = objectUrl;
      anchor.download =
        format === 'pdf' ? `lending-readiness-report.pdf` : `lending-readiness-report.txt`;
      anchor.click();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setDownloadError('Could not download readiness report.');
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Reports"
        title="Your readiness report"
        description={ADVISORY_DISCLAIMER_SHORT}
        actions={
          report ? (
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={downloading !== null}
                onClick={() => void download('pdf')}
                className="rounded-brand bg-navy-900 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
              >
                {downloading === 'pdf' ? 'Downloading…' : 'Download PDF'}
              </button>
              <button
                type="button"
                disabled={downloading !== null}
                onClick={() => void download('text')}
                className="rounded-brand border border-lrp-border bg-lrp-surface-elevated px-3 py-2 text-sm font-semibold text-navy-900 disabled:opacity-60"
              >
                {downloading === 'text' ? 'Downloading…' : 'Download text'}
              </button>
            </div>
          ) : null
        }
      />

      <p className="mb-4 text-xs leading-relaxed text-slate-500">{ADVISORY_DISCLAIMER_LONG}</p>
      {downloadError ? <p className="mb-4 text-sm text-critical">{downloadError}</p> : null}

      {!primary ? (
        <p className="rounded-brand border border-lrp-border bg-lrp-surface px-4 py-3 text-sm text-slate-600">
          Link a case to your client record to view reports.
        </p>
      ) : reportQuery.isLoading ? (
        <p className="text-sm text-slate-500">Loading readiness report…</p>
      ) : reportQuery.isError || !report ? (
        <PortalCard>
          <p className="text-sm text-slate-600">
            Your advisor has not published a readiness report yet. Check readiness status or ask a
            question via Messages.
          </p>
          <div className="mt-3 flex flex-wrap gap-3 text-sm font-medium">
            <Link href="/portal/readiness" className="text-gold-700">
              View readiness →
            </Link>
            <Link href="/portal/messages" className="text-gold-700">
              Ask a question →
            </Link>
          </div>
        </PortalCard>
      ) : (
        <>
          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <PortalCard>
              <div className="flex flex-col items-center py-6 text-center">
                <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
                  Lending Readiness Score™
                </p>
                <span
                  className={`mt-4 inline-flex rounded-brand px-4 py-2 text-2xl font-semibold ${readinessBandClass(report.band)}`}
                >
                  {readinessBandLabel(report.band)}
                </span>
                <p className="mt-3 text-xs text-slate-500">
                  Generated {formatDate(report.generated_at)} · {report.reports_evaluated} bureau
                  reports · {report.tradelines_evaluated} tradelines
                </p>
                <Link
                  href="/portal/tasks"
                  className="mt-6 inline-flex rounded-brand bg-gold-500 px-4 py-2.5 text-sm font-semibold text-navy-900"
                >
                  Open action plan
                </Link>
              </div>
            </PortalCard>

            <PortalCard title="What drives this band" description="Qualitative drivers only.">
              <ul className="space-y-3">
                {report.dimensions.map((dimension) => {
                  const score = typeof dimension.score === 'number' ? dimension.score : 0;
                  const label =
                    score >= 70 ? 'On track' : score >= 40 ? 'Needs attention' : 'Priority';
                  return (
                    <li
                      key={dimension.key ?? dimension.label}
                      className="flex items-center justify-between gap-3 text-sm"
                    >
                      <span className="font-medium text-navy-900">
                        {dimension.label ?? dimension.key}
                      </span>
                      <StatusPill tone="info">{label}</StatusPill>
                    </li>
                  );
                })}
              </ul>
            </PortalCard>
          </div>

          <PortalCard
            className="mt-6"
            title="Current blockers"
            description="Resolve these with your advisor — summaries only, not bureau PDF dumps."
          >
            {report.blockers.length === 0 ? (
              <p className="text-sm text-slate-500">No high-priority blockers listed.</p>
            ) : (
              <ul className="grid gap-3 md:grid-cols-2">
                {report.blockers.map((blocker) => (
                  <li
                    key={blocker.id ?? blocker.title}
                    className="rounded-brand border border-lrp-border bg-lrp-surface p-4"
                  >
                    <p className="font-medium text-navy-900">{blocker.title}</p>
                    <p className="mt-2 text-sm text-slate-500">{blocker.impact}</p>
                    <p className="mt-2 text-xs font-medium text-gold-700">{blocker.action}</p>
                  </li>
                ))}
              </ul>
            )}
          </PortalCard>

          <p className="mt-4 text-xs text-slate-500">{report.disclaimer}</p>
        </>
      )}
    </div>
  );
}
