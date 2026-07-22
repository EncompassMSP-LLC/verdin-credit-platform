import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  downloadAccountDisputeLetterExport,
  downloadCaseDisputeMailPackets,
  downloadCaseDisputeReportExcerpts,
  getCaseCreditReportDiscrepancies,
  listAccountDisputeLetters,
  listCaseAccounts,
  prepareCaseCreditReportDisputes,
  type CrossBureauDiscrepancy,
  type PreparedCreditReportDisputeItem,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ClientConsentGapsBanner } from '../compliance/ClientConsentGapsBanner';
import { useCaseClientConsentGaps } from '../../hooks/useCaseClientConsentGaps';
import { matchKeyFromSource } from '../../lib/findingDeepLink';

function formatCurrency(value: number | null | undefined) {
  if (value === null || value === undefined) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function formatMutationError(error: unknown) {
  if (error instanceof ApiClientError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Failed to prepare dispute workflow.';
}

function formatBureauList(bureaus: string[]) {
  if (bureaus.length === 0) return '—';
  return bureaus
    .map((bureau) => bureau.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()))
    .join(', ');
}

function classificationVariant(
  workflowTier: CrossBureauDiscrepancy['workflow_tier'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (workflowTier === 'none') return 'success';
  if (workflowTier === 'investigation') return 'warning';
  return 'danger';
}

function likelihoodLabel(
  likelihood: CrossBureauDiscrepancy['possible_causes'][number]['likelihood'],
) {
  if (likelihood === 'most_likely') return 'Most likely';
  if (likelihood === 'less_likely') return 'Less likely';
  return 'Possible';
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function openBlobInNewTab(blob: Blob) {
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank', 'noopener,noreferrer');
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

function normalizeCreditorName(value: string) {
  return value.trim().toLowerCase();
}

type DisputePreviewTarget = {
  accountId: string;
  letterId: string;
};

function PreviewReportPageButton({
  target,
  size = 'sm',
  consentBlocked = false,
}: {
  target: DisputePreviewTarget | null;
  size?: 'sm' | 'md';
  consentBlocked?: boolean;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!target) {
    return null;
  }

  const handlePreview = async () => {
    if (consentBlocked) {
      setError('Signed client consent is required before previewing report pages.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const { blob } = await downloadAccountDisputeLetterExport(
        target.accountId,
        target.letterId,
        'report-excerpt',
      );
      openBlobInNewTab(blob);
    } catch (previewError) {
      setError(formatMutationError(previewError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Button
        size={size}
        variant="secondary"
        loading={loading}
        disabled={consentBlocked}
        title={
          consentBlocked
            ? 'Signed CROA and FCRA consents are required before previewing report pages'
            : undefined
        }
        onClick={() => void handlePreview()}
      >
        Preview report page
      </Button>
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
    </div>
  );
}

function DiscrepancyRow({
  caseId,
  discrepancy,
  onPrepared,
  disputePreview,
  consentBlocked,
  highlighted,
}: {
  caseId: string;
  discrepancy: CrossBureauDiscrepancy;
  onPrepared: () => void;
  disputePreview: DisputePreviewTarget | null;
  consentBlocked: boolean;
  highlighted?: boolean;
}) {
  const prepareMutation = useMutation({
    mutationFn: () =>
      prepareCaseCreditReportDisputes(caseId, { match_keys: [discrepancy.match_key] }),
    onSuccess: onPrepared,
  });

  const preparedPreview: DisputePreviewTarget | null =
    prepareMutation.data?.prepared[0]?.account_id &&
    prepareMutation.data.prepared[0].dispute_letter_id
      ? {
          accountId: prepareMutation.data.prepared[0].account_id,
          letterId: prepareMutation.data.prepared[0].dispute_letter_id,
        }
      : null;

  const previewTarget = preparedPreview ?? disputePreview;

  return (
    <tr
      className={`align-top ${highlighted ? 'bg-brand-50/70 ring-2 ring-inset ring-brand-200' : ''}`}
    >
      <td className="px-3 py-3">
        <p className="font-medium text-gray-900">{discrepancy.creditor_name}</p>
        <p className="mt-1 text-xs text-gray-500">{discrepancy.account_number_masked ?? '—'}</p>
        {highlighted ? (
          <p className="mt-1">
            <Badge variant="success">from playbook</Badge>
          </p>
        ) : null}
      </td>
      <td className="px-3 py-3">
        <div className="space-y-2">
          <Badge variant={classificationVariant(discrepancy.workflow_tier)}>
            {discrepancy.classification_label}
          </Badge>
          {discrepancy.workflow_tier !== 'none' ? (
            <p className="text-xs text-gray-600">
              Confidence: <span className="font-medium">{discrepancy.confidence_score}%</span>
            </p>
          ) : null}
          {discrepancy.workflow_tier !== 'none' ? (
            <div className="text-xs text-gray-600">
              <p>
                <span className="font-medium text-gray-700">Present:</span>{' '}
                {formatBureauList(discrepancy.bureaus_reporting)}
              </p>
              {discrepancy.bureaus_missing.length > 0 ? (
                <p className="mt-1">
                  <span className="font-medium text-gray-700">Missing:</span>{' '}
                  {formatBureauList(discrepancy.bureaus_missing)}
                </p>
              ) : null}
            </div>
          ) : null}
        </div>
      </td>
      <td className="px-3 py-3 text-sm text-gray-700">
        {discrepancy.bureau_snapshots.map((snapshot) => (
          <div key={`${snapshot.bureau}-${snapshot.document_id}`} className="mb-2 last:mb-0">
            <span className="font-medium capitalize">{snapshot.bureau}</span>
            <span className="text-gray-500">
              {' '}
              · {formatCurrency(snapshot.balance)} · {snapshot.payment_status ?? 'No status'}
            </span>
          </div>
        ))}
      </td>
      <td className="px-3 py-3 text-sm text-gray-700">
        <p>{discrepancy.recommended_next_step}</p>
        {discrepancy.possible_causes.length > 0 ? (
          <div className="mt-3">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Possible causes
            </p>
            <ul className="mt-1 space-y-1 text-xs text-gray-600">
              {discrepancy.possible_causes.map((cause) => (
                <li key={cause.label}>
                  <span className="font-medium text-gray-700">
                    {likelihoodLabel(cause.likelihood)}:
                  </span>{' '}
                  {cause.label}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </td>
      <td className="px-3 py-3">
        {discrepancy.dispute_ready ? (
          <Button
            size="sm"
            variant="secondary"
            loading={prepareMutation.isPending}
            onClick={() => prepareMutation.mutate()}
          >
            Prepare dispute
          </Button>
        ) : discrepancy.requires_investigation ? (
          <span className="text-xs text-amber-800">Investigation recommended</span>
        ) : (
          <span className="text-xs text-gray-500">No action needed</span>
        )}
        {prepareMutation.isError ? (
          <p className="mt-2 text-xs text-red-600">{formatMutationError(prepareMutation.error)}</p>
        ) : null}
        {prepareMutation.data?.prepared[0] ? (
          <div className="mt-2 space-y-2 text-xs">
            <Link
              to={`/accounts/${prepareMutation.data.prepared[0].account_id}`}
              className="block text-brand-600 hover:underline"
            >
              Open account
            </Link>
            <PreviewReportPageButton target={previewTarget} consentBlocked={consentBlocked} />
          </div>
        ) : previewTarget ? (
          <div className="mt-2">
            <PreviewReportPageButton target={previewTarget} consentBlocked={consentBlocked} />
          </div>
        ) : null}
      </td>
    </tr>
  );
}

function PreparedDisputePreviewList({
  prepared,
  consentBlocked,
}: {
  prepared: PreparedCreditReportDisputeItem[];
  consentBlocked: boolean;
}) {
  const previewItems = prepared.filter((item) => item.dispute_letter_id);

  if (previewItems.length === 0) {
    return null;
  }

  return (
    <ul className="mt-3 space-y-2 border-t border-green-200 pt-3">
      {previewItems.map((item) => (
        <li
          key={item.match_key}
          className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
        >
          <span className="font-medium text-green-900">{item.creditor_name}</span>
          <div className="flex flex-wrap items-center gap-2">
            <PreviewReportPageButton
              target={{
                accountId: item.account_id,
                letterId: item.dispute_letter_id!,
              }}
              consentBlocked={consentBlocked}
            />
            <Link
              to={`/accounts/${item.account_id}`}
              className="text-sm font-medium text-brand-700 hover:underline"
            >
              Open account
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function CrossBureauDiscrepancyPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const highlightMatchKey = matchKeyFromSource(searchParams.get('finding_source'));
  const consentGaps = useCaseClientConsentGaps(caseId);
  const consentBlocked = consentGaps.requiresConsent && consentGaps.hasGaps;
  const [downloadingPackets, setDownloadingPackets] = useState(false);
  const [downloadingExcerpts, setDownloadingExcerpts] = useState(false);
  const [downloadPacketsError, setDownloadPacketsError] = useState<string | null>(null);
  const [downloadExcerptsError, setDownloadExcerptsError] = useState<string | null>(null);
  const discrepanciesQuery = useQuery({
    queryKey: ['case-credit-report-discrepancies', caseId],
    queryFn: () => getCaseCreditReportDiscrepancies(caseId),
    retry: false,
  });

  const caseDisputesQuery = useQuery({
    queryKey: ['case-dispute-previews', caseId],
    queryFn: async () => {
      const accounts = await listCaseAccounts(caseId, { page_size: 100 });
      const entries = await Promise.all(
        accounts.items.map(async (account) => {
          const letters = await listAccountDisputeLetters(account.id);
          if (letters.length === 0) {
            return null;
          }
          return {
            creditorName: account.creditor_name,
            accountId: account.id,
            letterId: letters[0].id,
          };
        }),
      );
      return entries.filter((entry): entry is NonNullable<typeof entry> => entry !== null);
    },
    retry: false,
  });

  const disputePreviewByCreditor = useMemo(() => {
    const map = new Map<string, DisputePreviewTarget>();
    for (const entry of caseDisputesQuery.data ?? []) {
      map.set(normalizeCreditorName(entry.creditorName), {
        accountId: entry.accountId,
        letterId: entry.letterId,
      });
    }
    return map;
  }, [caseDisputesQuery.data]);

  const prepareAllMutation = useMutation({
    mutationFn: () => prepareCaseCreditReportDisputes(caseId, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['case-credit-report-discrepancies', caseId] });
      queryClient.invalidateQueries({ queryKey: ['case-dispute-previews', caseId] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['case-credit-report-discrepancies', caseId] });
    queryClient.invalidateQueries({ queryKey: ['case-dispute-previews', caseId] });
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
  };

  const data = discrepanciesQuery.data;
  const disputeReady = data?.discrepancies.filter((item) => item.dispute_ready) ?? [];
  const investigationNeeded =
    data?.discrepancies.filter((item) => item.requires_investigation) ?? [];

  const handleDownloadAllMailPackets = async () => {
    if (consentBlocked) {
      setDownloadPacketsError('Signed client consent is required before downloading mail packets.');
      return;
    }
    setDownloadingPackets(true);
    setDownloadPacketsError(null);
    try {
      const { blob, filename } = await downloadCaseDisputeMailPackets(caseId);
      downloadBlob(blob, filename);
    } catch (error) {
      setDownloadPacketsError(formatMutationError(error));
    } finally {
      setDownloadingPackets(false);
    }
  };

  const handleDownloadAllReportExcerpts = async () => {
    if (consentBlocked) {
      setDownloadExcerptsError('Signed client consent is required before previewing report pages.');
      return;
    }
    setDownloadingExcerpts(true);
    setDownloadExcerptsError(null);
    try {
      const { blob, filename } = await downloadCaseDisputeReportExcerpts(caseId);
      downloadBlob(blob, filename);
    } catch (error) {
      setDownloadExcerptsError(formatMutationError(error));
    } finally {
      setDownloadingExcerpts(false);
    }
  };

  return (
    <div id={id} className={className}>
      <Card title="Cross-bureau discrepancies" className="w-full">
        <div className="mb-4 flex justify-end">
          <Link
            to={`/guides/dispute-workflow?case_id=${caseId}`}
            className="text-sm font-medium text-brand-600 hover:underline"
          >
            Dispute workflow guide →
          </Link>
        </div>
        {discrepanciesQuery.isLoading ? (
          <p className="text-sm text-gray-500">Comparing bureau reports...</p>
        ) : discrepanciesQuery.isError ? (
          <p className="text-sm text-gray-600">
            Upload at least two bureau credit reports on this case to compare Experian, Equifax, and
            TransUnion tradelines for inconsistencies.
          </p>
        ) : data ? (
          <div className="space-y-4">
            <ClientConsentGapsBanner caseId={caseId} />
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  Compared {data.reports_compared.map((bureau) => bureau.toUpperCase()).join(', ')}{' '}
                  reports for tradelines that disagree across bureaus. Investigation-first review
                  separates reporting differences from dispute-ready inconsistencies.
                </p>
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  <Badge variant="warning">{data.summary.investigation_needed} investigation</Badge>
                  <Badge variant="danger">{data.summary.dispute_ready} dispute-ready</Badge>
                  <Badge variant="success">{data.summary.consistent} consistent</Badge>
                  <Badge variant="default">{data.summary.missing_from_bureau} missing bureau</Badge>
                  <Badge variant="default">{data.summary.balance_mismatch} balance</Badge>
                  <Badge variant="default">{data.summary.status_mismatch} status</Badge>
                </div>
              </div>
              <div className="flex flex-col items-stretch gap-2 sm:items-end">
                {disputeReady.length > 0 ? (
                  <Button
                    size="sm"
                    loading={prepareAllMutation.isPending}
                    onClick={() => prepareAllMutation.mutate()}
                  >
                    Prepare disputes ({disputeReady.length})
                  </Button>
                ) : null}
                {investigationNeeded.length > 0 && disputeReady.length === 0 ? (
                  <p className="max-w-xs text-right text-xs text-amber-800">
                    {investigationNeeded.length} tradeline
                    {investigationNeeded.length === 1 ? '' : 's'} need verification before dispute
                    prep.
                  </p>
                ) : null}
                <Button
                  size="sm"
                  variant="secondary"
                  loading={downloadingExcerpts}
                  disabled={consentBlocked}
                  title={
                    consentBlocked
                      ? 'Signed CROA and FCRA consents are required before previewing report pages'
                      : undefined
                  }
                  onClick={() => void handleDownloadAllReportExcerpts()}
                >
                  Preview all report pages
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  loading={downloadingPackets}
                  disabled={consentBlocked}
                  title={
                    consentBlocked
                      ? 'Signed CROA and FCRA consents are required before downloading mail packets'
                      : undefined
                  }
                  onClick={() => void handleDownloadAllMailPackets()}
                >
                  Download all mail packets
                </Button>
              </div>
            </div>

            {downloadExcerptsError ? (
              <p className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                {downloadExcerptsError}
              </p>
            ) : null}

            {downloadPacketsError ? (
              <p className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                {downloadPacketsError}
              </p>
            ) : null}

            {prepareAllMutation.isError ? (
              <p className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                {formatMutationError(prepareAllMutation.error)}
              </p>
            ) : null}

            {prepareAllMutation.data ? (
              <div className="rounded-md bg-green-50 p-3 text-sm text-green-800">
                <p>
                  Prepared {prepareAllMutation.data.prepared.length} account
                  {prepareAllMutation.data.prepared.length === 1 ? '' : 's'} with mail-ready dispute
                  packets. Download the ZIP to print labels, letters, and checklists for each
                  creditor.
                </p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <button
                    type="button"
                    className="font-medium text-brand-700 hover:underline"
                    onClick={() => void handleDownloadAllReportExcerpts()}
                  >
                    Preview all report pages →
                  </button>
                  <button
                    type="button"
                    className="font-medium text-brand-700 hover:underline"
                    onClick={() => void handleDownloadAllMailPackets()}
                  >
                    Download all mail packets →
                  </button>
                  <Link
                    to={`/cases/${caseId}/accounts`}
                    className="font-medium text-brand-600 hover:underline"
                  >
                    View case accounts →
                  </Link>
                </div>
                <PreparedDisputePreviewList
                  prepared={prepareAllMutation.data.prepared}
                  consentBlocked={consentBlocked}
                />
                {(prepareAllMutation.data.locked?.length ?? 0) > 0 ? (
                  <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
                    <p className="font-medium">
                      {prepareAllMutation.data.locked?.length} tradeline(s) were skipped for
                      identity-theft review. Resolve these in the Identity Theft Case Center (§605B)
                      rather than mixing identity-theft and accuracy theories:
                    </p>
                    <ul className="mt-1 space-y-0.5">
                      {prepareAllMutation.data.locked?.map((item) => (
                        <li key={item.match_key}>{item.creditor_name ?? item.match_key}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : null}

            <div className="overflow-x-auto">
              <table className="w-full min-w-[960px] divide-y divide-gray-200 text-sm">
                <thead>
                  <tr className="text-left text-gray-500">
                    <th className="w-[16%] px-3 py-2 font-medium">Tradeline</th>
                    <th className="w-[18%] px-3 py-2 font-medium">Classification</th>
                    <th className="w-[22%] px-3 py-2 font-medium">By bureau</th>
                    <th className="w-[28%] px-3 py-2 font-medium">Recommended next step</th>
                    <th className="w-[16%] px-3 py-2 font-medium">Next steps</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.discrepancies.map((discrepancy) => (
                    <DiscrepancyRow
                      key={discrepancy.match_key}
                      caseId={caseId}
                      discrepancy={discrepancy}
                      onPrepared={invalidate}
                      consentBlocked={consentBlocked}
                      highlighted={
                        highlightMatchKey != null && discrepancy.match_key === highlightMatchKey
                      }
                      disputePreview={
                        disputePreviewByCreditor.get(
                          normalizeCreditorName(discrepancy.creditor_name),
                        ) ?? null
                      }
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
