'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { useLenderAuth } from '@/lib/lender/auth';
import { monthlyReports } from '@/lib/lender/data';
import { exportTextReport } from '@/lib/lender/export';
import type { MonthlyReport } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

function buildReportText(report: MonthlyReport): string {
  const lines = [
    report.title,
    `Generated ${formatDate(report.generatedAt)}`,
    '',
    'Highlights:',
    ...report.highlights.map((h) => `- ${h}`),
    '',
    'Metrics:',
    ...report.metrics.map((m) => `- ${m.label}: ${m.value}`),
    '',
    'Disclaimer: Readiness metrics are advisory composites for partner operations—not underwriting decisions or funding guarantees.',
  ];
  return lines.join('\n');
}

export default function ReportsPage() {
  const { can } = useLenderAuth();

  return (
    <RoleGate permission="reports.view">
      <div>
        <PageHeader
          eyebrow="Monthly reports"
          title="Partner readiness reports"
          description="Executive summaries for production and credit stakeholders. Export requires reports.export permission."
        />

        <div className="space-y-4">
          {monthlyReports.map((report) => (
            <PortalCard
              key={report.id}
              title={report.title}
              description={`${report.month} · Generated ${formatDate(report.generatedAt)}`}
              action={
                can('reports.export') ? (
                  <button
                    type="button"
                    onClick={() =>
                      exportTextReport(
                        `${report.month}-partner-report.txt`,
                        buildReportText(report),
                      )
                    }
                    className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:border-gold-500/50 dark:border-white/15"
                  >
                    Export text
                  </button>
                ) : null
              }
            >
              <div className="grid gap-6 lg:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Highlights
                  </p>
                  <ul className="mt-2 space-y-2 text-sm text-navy-900 dark:text-white">
                    {report.highlights.map((item) => (
                      <li key={item} className="flex gap-2">
                        <span className="text-gold-600">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Metrics
                  </p>
                  <dl className="mt-2 grid grid-cols-2 gap-3">
                    {report.metrics.map((metric) => (
                      <div
                        key={metric.label}
                        className="rounded-md border border-navy-900/8 bg-[#F8FAFC] px-3 py-2 dark:border-white/10 dark:bg-navy-900/40"
                      >
                        <dt className="text-[0.65rem] uppercase tracking-wider text-slate-500">
                          {metric.label}
                        </dt>
                        <dd className="mt-1 text-lg font-semibold tabular-nums">{metric.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              </div>
            </PortalCard>
          ))}
        </div>
      </div>
    </RoleGate>
  );
}
