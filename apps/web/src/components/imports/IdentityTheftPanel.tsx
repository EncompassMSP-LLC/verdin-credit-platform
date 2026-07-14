import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  confirmIdentityTheftAccount,
  getCaseIdentityTheftCenter,
  type IdentityTheftConfirmation,
  type IdentityTheftFinding,
  type IdentityTheftFindingSummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';
import { useState } from 'react';

function severityVariant(
  severity: IdentityTheftFinding['severity'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (severity === 'high') return 'danger';
  if (severity === 'medium') return 'warning';
  return 'info';
}

function SummaryBadges({ summary }: { summary: IdentityTheftFindingSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.tradelines_evaluated} tradelines</Badge>
      <Badge variant="danger">{summary.report_level_indicators} report</Badge>
      <Badge variant="warning">{summary.tradeline_indicators} tradeline</Badge>
      <Badge variant="danger">{summary.ordinary_dispute_locked_count} locked</Badge>
      <Badge variant="default">{summary.total} total</Badge>
    </div>
  );
}

const CONFIRMATION_LABELS: Record<IdentityTheftConfirmation, string> = {
  recognize: 'I recognize this account',
  need_more_info: 'I do not recognize it, but I need more information',
  inaccurate_reporting: 'This is my account, but the reporting is inaccurate',
  identity_theft: 'I believe this account resulted from identity theft',
  mixed_file: 'This account belongs to another person with similar identifying information',
  authorized_user: 'I am an authorized user only',
  unsure: 'Unsure — request documentation first',
};

function FindingsList({ findings }: { findings: IdentityTheftFinding[] }) {
  if (findings.length === 0) {
    return (
      <p className="mt-3 text-sm text-gray-500">No identity-theft indicators on this report.</p>
    );
  }
  return (
    <ul className="mt-4 space-y-3">
      {findings.map((finding) => (
        <li
          key={`${finding.rule_id}-${finding.tradeline_index ?? 'report'}-${finding.creditor_name ?? ''}`}
          className="rounded-md border border-gray-200 px-4 py-3"
        >
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <p className="text-sm font-medium text-gray-900">{finding.title}</p>
              <p className="mt-1 text-xs text-gray-500">{finding.rule_id}</p>
            </div>
            <div className="flex flex-wrap gap-1">
              <Badge variant="info">{finding.detection_source}</Badge>
              <Badge variant={severityVariant(finding.severity)}>{finding.severity}</Badge>
              {finding.ordinary_dispute_locked ? (
                <Badge variant="danger">dispute paused</Badge>
              ) : null}
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-700">{finding.description}</p>
          {finding.tradeline_index != null ? (
            <p className="mt-2 text-sm text-gray-600">
              {finding.creditor_name ?? 'Unknown creditor'}
              {finding.account_number_masked ? ` · ${finding.account_number_masked}` : ''}
              {` · tradeline #${finding.tradeline_index + 1}`}
            </p>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

export function CaseIdentityTheftPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const queryClient = useQueryClient();
  const [selectedFinding, setSelectedFinding] = useState<IdentityTheftFinding | null>(null);
  const [confirmation, setConfirmation] = useState<IdentityTheftConfirmation>('need_more_info');
  const [attestation, setAttestation] = useState(false);

  const centerQuery = useQuery({
    queryKey: ['case-identity-theft-center', caseId],
    queryFn: () => getCaseIdentityTheftCenter(caseId),
    retry: false,
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      confirmIdentityTheftAccount(caseId, {
        confirmation,
        attestation_accepted: attestation,
        document_id: centerQuery.data?.findings?.documents[0]?.document_id,
        bureau: centerQuery.data?.findings?.documents[0]?.bureau,
        tradeline_index: selectedFinding?.tradeline_index,
        creditor_name: selectedFinding?.creditor_name,
        account_number_masked: selectedFinding?.account_number_masked,
        detection_source: selectedFinding?.detection_source ?? 'CONSUMER_CONFIRMATION',
        rule_id: selectedFinding?.rule_id,
        confidence: selectedFinding?.confidence ?? 1,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['case-identity-theft-center', caseId] });
      setSelectedFinding(null);
      setAttestation(false);
    },
  });

  const data = centerQuery.data;

  return (
    <div id={id} className={className}>
      {data?.banner_active ? (
        <div className="mb-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3">
          <p className="text-sm font-semibold text-amber-950">
            {data.banner_title ?? 'Identity-Theft Protection Indicator Detected'}
          </p>
          <p className="mt-1 text-sm text-amber-900">
            {data.banner_body ??
              'This report contains a fraud alert, freeze, victim statement, or identity-theft block. Review the Identity Theft Case Center before sending ordinary credit disputes.'}
          </p>
        </div>
      ) : null}

      <Card title="Identity Theft Case Center">
        <p className="text-sm text-gray-500">
          Phase 8 of the Compliance Intelligence Engine. Indicators never auto-label accounts as
          identity theft — consumer confirmation and attestation are required before §605B
          workflows.
        </p>
        <p className="mt-2 text-xs text-gray-500">{data?.disclaimer}</p>

        {centerQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading identity-theft center…</p>
        ) : null}

        {centerQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {centerQuery.error instanceof ApiClientError && centerQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : centerQuery.error instanceof Error
                ? centerQuery.error.message
                : 'Failed to load identity-theft center'}
          </p>
        ) : null}

        {data?.findings ? (
          <div className="mt-4 space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">
                Reports evaluated:{' '}
                {data.findings.reports_evaluated.length > 0
                  ? data.findings.reports_evaluated.join(', ')
                  : 'none'}
              </p>
              <SummaryBadges summary={data.findings.summary} />
            </div>

            {data.findings.documents.map((documentFindings) => (
              <div
                key={documentFindings.document_id}
                className="rounded-md border border-gray-200 p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="text-sm font-medium capitalize text-gray-900">
                      {documentFindings.bureau}
                    </h4>
                    <Link
                      to={`/documents/${documentFindings.document_id}`}
                      className="mt-1 inline-block text-xs text-brand-600 hover:underline"
                    >
                      Open report document
                    </Link>
                  </div>
                  <SummaryBadges summary={documentFindings.summary} />
                </div>
                <FindingsList findings={documentFindings.findings} />
                <div className="mt-3 flex flex-wrap gap-2">
                  {documentFindings.findings
                    .filter((f) => f.tradeline_index != null)
                    .map((finding) => (
                      <button
                        key={`${finding.rule_id}-${finding.tradeline_index}`}
                        type="button"
                        className="rounded-md bg-gray-200 px-3 py-1.5 text-sm font-medium text-gray-900 hover:bg-gray-300"
                        onClick={() => setSelectedFinding(finding)}
                      >
                        Review:{' '}
                        {finding.creditor_name ??
                          `Tradeline #${(finding.tradeline_index ?? 0) + 1}`}
                      </button>
                    ))}
                </div>
              </div>
            ))}
          </div>
        ) : null}

        {selectedFinding ? (
          <div className="mt-6 rounded-md border border-brand-200 bg-brand-50/40 p-4">
            <h4 className="text-sm font-medium text-gray-900">Consumer confirmation</h4>
            <p className="mt-1 text-sm text-gray-600">
              {selectedFinding.creditor_name ?? 'Selected tradeline'} — choose the truthful theory.
              Ordinary accuracy disputes stay paused until confirmation unlocks them (or an
              identity-theft case is opened).
            </p>
            <label className="mt-3 block text-xs font-medium text-gray-700">Confirmation</label>
            <select
              className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value as IdentityTheftConfirmation)}
            >
              {(Object.keys(CONFIRMATION_LABELS) as IdentityTheftConfirmation[]).map((key) => (
                <option key={key} value={key}>
                  {CONFIRMATION_LABELS[key]}
                </option>
              ))}
            </select>
            {confirmation === 'identity_theft' ? (
              <label className="mt-3 flex items-start gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={attestation}
                  onChange={(event) => setAttestation(event.target.checked)}
                />
                <span>{data?.attestation_text}</span>
              </label>
            ) : null}
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                disabled={confirmMutation.isPending}
                onClick={() => confirmMutation.mutate()}
              >
                {confirmMutation.isPending ? 'Saving…' : 'Save confirmation'}
              </button>
              <button
                type="button"
                className="rounded-md bg-gray-200 px-3 py-1.5 text-sm font-medium text-gray-900 hover:bg-gray-300"
                onClick={() => {
                  setSelectedFinding(null);
                  setAttestation(false);
                }}
              >
                Cancel
              </button>
            </div>
            {confirmMutation.isError ? (
              <p className="mt-2 text-sm text-red-600">
                {confirmMutation.error instanceof Error
                  ? confirmMutation.error.message
                  : 'Confirmation failed'}
              </p>
            ) : null}
          </div>
        ) : null}

        {data?.incident ? (
          <div className="mt-6 rounded-md border border-gray-200 p-4">
            <h4 className="text-sm font-medium text-gray-900">Incident profile</h4>
            <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-gray-500">Status</dt>
                <dd className="capitalize">{data.incident.status.replace('_', ' ')}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Recovery step</dt>
                <dd>
                  {data.incident.recovery_step} / {data.recovery_workflow_steps.length}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">FTC report</dt>
                <dd>{data.incident.ftc_report_status}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Discovered</dt>
                <dd>{data.incident.discovered_at ?? '—'}</dd>
              </div>
            </dl>
            {data.fcra_605b ? (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-900">{data.fcra_605b.remedy_type}</p>
                <p className="text-xs text-gray-500">Not an ordinary accuracy dispute</p>
                <p className="mt-1 text-sm text-gray-700">
                  Packet readiness: {data.fcra_605b.packet_readiness}%
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-700">
                  {data.fcra_605b.items.map((item) => (
                    <li key={item.item_id}>
                      {item.status === 'present' ? '✓' : item.required ? '△' : '○'} {item.label}
                      {!item.required ? ' (supporting)' : null}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}

        {data && data.protections.length > 0 ? (
          <div className="mt-6 overflow-x-auto">
            <h4 className="text-sm font-medium text-gray-900">Fraud-alert and freeze tracking</h4>
            <table className="mt-2 min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-gray-500">
                  <th className="py-2 pr-4 font-medium">Protection</th>
                  <th className="py-2 pr-4 font-medium">Status</th>
                  <th className="py-2 pr-4 font-medium">Date placed</th>
                  <th className="py-2 font-medium">Expiration</th>
                </tr>
              </thead>
              <tbody>
                {data.protections.map((row) => (
                  <tr key={row.id} className="border-b border-gray-100">
                    <td className="py-2 pr-4 capitalize">
                      {row.protection_type.replaceAll('_', ' ')}
                    </td>
                    <td className="py-2 pr-4 capitalize">{row.status}</td>
                    <td className="py-2 pr-4">{row.placed_at ?? '—'}</td>
                    <td className="py-2">{row.expires_at ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {data && data.account_reviews.length > 0 ? (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-900">Account reviews</h4>
            <ul className="mt-2 space-y-2 text-sm text-gray-700">
              {data.account_reviews.map((review) => (
                <li key={review.id} className="rounded-md border border-gray-200 px-3 py-2">
                  {review.creditor_name ?? 'Account'} · {review.consumer_confirmation ?? 'pending'}{' '}
                  · {review.issue_type}
                  {review.ordinary_dispute_locked ? ' · ordinary disputes locked' : ''}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
