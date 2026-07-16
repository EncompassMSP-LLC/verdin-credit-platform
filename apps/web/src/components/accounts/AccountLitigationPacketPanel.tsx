import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  downloadAccountLitigationPacket,
  getAccountLitigationPacket,
  type LitigationStrength,
} from '@verdin/api-client';

const STRENGTH_LABELS: Record<LitigationStrength, string> = {
  strong: 'Strong',
  moderate: 'Moderate',
  weak: 'Weak',
  not_ready: 'Not ready',
};

const STRENGTH_STYLES: Record<LitigationStrength, string> = {
  strong: 'bg-red-100 text-red-800',
  moderate: 'bg-amber-100 text-amber-800',
  weak: 'bg-yellow-50 text-yellow-700',
  not_ready: 'bg-gray-100 text-gray-600',
};

function formatDate(value: string | null): string {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

interface AccountLitigationPacketPanelProps {
  accountId: string;
}

export function AccountLitigationPacketPanel({ accountId }: AccountLitigationPacketPanelProps) {
  const packetQuery = useQuery({
    queryKey: ['account-litigation-packet', accountId],
    queryFn: () => getAccountLitigationPacket(accountId),
    enabled: false,
  });

  const packet = packetQuery.data;
  const [downloading, setDownloading] = useState<'text' | 'pdf' | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async (format: 'text' | 'pdf') => {
    setDownloading(format);
    setDownloadError(null);
    try {
      const { blob, filename } = await downloadAccountLitigationPacket(accountId, format);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setDownloadError(error instanceof Error ? error.message : 'Download failed');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="mt-6 border-t border-gray-100 pt-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-gray-900">Litigation-readiness packet</h3>
        <div className="flex items-center gap-2">
          {packet ? (
            <>
              <button
                type="button"
                className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                onClick={() => handleDownload('text')}
                disabled={downloading !== null}
              >
                {downloading === 'text' ? 'Preparing…' : 'Download .txt'}
              </button>
              <button
                type="button"
                className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                onClick={() => handleDownload('pdf')}
                disabled={downloading !== null}
              >
                {downloading === 'pdf' ? 'Preparing…' : 'Download .pdf'}
              </button>
            </>
          ) : null}
          <button
            type="button"
            className="rounded-md border border-brand-600 px-3 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-50 disabled:opacity-50"
            onClick={() => packetQuery.refetch()}
            disabled={packetQuery.isFetching}
          >
            {packetQuery.isFetching ? 'Assembling…' : packet ? 'Refresh packet' : 'Assemble packet'}
          </button>
        </div>
      </div>
      <p className="mt-1 text-xs text-gray-500">
        Bundles the reinvestigation evidence trail and an advisory §611/§623 willful-noncompliance
        grade for a licensed attorney to review. The platform never files suit, drafts pleadings, or
        transmits anything to a court or attorney.
      </p>

      {packetQuery.isError ? (
        <p className="mt-3 text-xs text-red-600">
          Could not assemble the packet (write permission required).
        </p>
      ) : null}

      {downloadError ? <p className="mt-3 text-xs text-red-600">{downloadError}</p> : null}

      {packet ? (
        <div className="mt-4 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STRENGTH_STYLES[packet.assessment.strength]}`}
            >
              {STRENGTH_LABELS[packet.assessment.strength]} · score {packet.assessment.score}
            </span>
            {packet.assessment.eligible ? (
              <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-800">
                Eligible for attorney handoff
              </span>
            ) : (
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                Not yet eligible
              </span>
            )}
            <span className="text-xs text-gray-500">
              Clock: {packet.clock_state}
              {packet.clock_extended ? ' · 45-day window' : ''}
            </span>
          </div>

          <p className="text-sm text-gray-700">{packet.assessment.summary}</p>

          {packet.assessment.indicators.length > 0 ? (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Willful-noncompliance indicators
              </h4>
              <ul className="mt-1 list-disc space-y-1 pl-5 text-xs text-gray-700">
                {packet.assessment.indicators.map((indicator) => (
                  <li key={indicator}>{indicator}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {packet.cross_bureau.compared_bureaus.length > 0 ? (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Cross-bureau discrepancies
                <span className="ml-1 font-normal normal-case text-gray-400">
                  (vs {packet.cross_bureau.compared_bureaus.join(', ')})
                </span>
              </h4>
              {packet.cross_bureau.discrepancies.length === 0 ? (
                <p className="mt-1 text-xs text-gray-500">
                  No divergences found across the compared bureaus.
                </p>
              ) : (
                <ul className="mt-1 space-y-1 text-xs text-gray-700">
                  {packet.cross_bureau.discrepancies.map((discrepancy) => (
                    <li
                      key={`${discrepancy.kind}-${discrepancy.bureau}-${discrepancy.detail}`}
                      className="flex items-start gap-2"
                    >
                      <span
                        className={`mt-0.5 shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-medium ${
                          discrepancy.kind === 'outcome_conflict'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {discrepancy.kind.replace(/_/g, ' ')}
                      </span>
                      <span>{discrepancy.detail}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : null}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Dispute rounds mailed ({packet.letters.length})
              </h4>
              {packet.letters.length === 0 ? (
                <p className="mt-1 text-xs text-gray-500">No dispute letters on file.</p>
              ) : (
                <ul className="mt-1 divide-y divide-gray-100 rounded-md border border-gray-100">
                  {packet.letters.map((letter) => (
                    <li key={letter.id} className="px-3 py-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">{letter.subject}</span>
                        <span className="text-gray-500">{letter.status}</span>
                      </div>
                      <span className="text-gray-500">Sent {formatDate(letter.sent_at)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Recorded responses ({packet.responses.length})
              </h4>
              {packet.responses.length === 0 ? (
                <p className="mt-1 text-xs text-gray-500">No responses recorded.</p>
              ) : (
                <ul className="mt-1 divide-y divide-gray-100 rounded-md border border-gray-100">
                  {packet.responses.map((response) => (
                    <li key={response.id} className="px-3 py-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">{response.outcome}</span>
                        <span className="text-gray-500">
                          {formatDate(response.response_date)} · {response.response_method}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <p className="rounded-md bg-gray-50 px-3 py-2 text-xs italic text-gray-500">
            {packet.disclaimer}
          </p>
        </div>
      ) : null}
    </div>
  );
}
