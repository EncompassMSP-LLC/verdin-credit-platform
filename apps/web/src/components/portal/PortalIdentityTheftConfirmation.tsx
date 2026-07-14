import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  confirmPortalIdentityTheftAccount,
  getAccessToken,
  getPortalIdentityTheftCenter,
  type IdentityTheftConfirmation,
  type IdentityTheftFinding,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { usePortalAuth } from '../../lib/portal-auth';

const CONFIRMATION_KEYS: IdentityTheftConfirmation[] = [
  'recognize',
  'need_more_info',
  'inaccurate_reporting',
  'identity_theft',
  'mixed_file',
  'authorized_user',
  'unsure',
];

interface PortalIdentityTheftConfirmationProps {
  caseId: string;
}

export function PortalIdentityTheftConfirmation({ caseId }: PortalIdentityTheftConfirmationProps) {
  const { t } = useTranslation('portal');
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = usePortalAuth();
  const [selectedFinding, setSelectedFinding] = useState<IdentityTheftFinding | null>(null);
  const [confirmation, setConfirmation] = useState<IdentityTheftConfirmation>('need_more_info');
  const [attestation, setAttestation] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const authReady = isAuthenticated && !authLoading && Boolean(getAccessToken());

  const centerQuery = useQuery({
    queryKey: ['portal-identity-theft-center', caseId],
    queryFn: () => getPortalIdentityTheftCenter(caseId),
    enabled: authReady,
    retry: false,
  });

  const confirmMutation = useMutation({
    mutationFn: () => {
      if (!selectedFinding) {
        throw new Error(t('identityTheft.errors.selectAccount'));
      }
      if (confirmation === 'identity_theft' && !attestation) {
        throw new Error(t('identityTheft.errors.acceptAttestation'));
      }
      const documentId = centerQuery.data?.findings?.documents.find((doc) =>
        doc.findings.some(
          (finding) =>
            finding.rule_id === selectedFinding.rule_id &&
            finding.tradeline_index === selectedFinding.tradeline_index,
        ),
      )?.document_id;

      return confirmPortalIdentityTheftAccount(caseId, {
        confirmation,
        attestation_accepted: attestation,
        document_id: documentId,
        bureau: centerQuery.data?.findings?.documents[0]?.bureau,
        tradeline_index: selectedFinding.tradeline_index,
        creditor_name: selectedFinding.creditor_name,
        account_number_masked: selectedFinding.account_number_masked,
        detection_source: selectedFinding.detection_source,
        rule_id: selectedFinding.rule_id,
        confidence: selectedFinding.confidence,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-identity-theft-center', caseId] });
      setSelectedFinding(null);
      setAttestation(false);
      setError(null);
      setSuccess(t('identityTheft.success'));
    },
    onError: (mutationError) => {
      setSuccess(null);
      setError(
        mutationError instanceof Error
          ? mutationError.message
          : t('identityTheft.errors.submitFailed'),
      );
    },
  });

  const data = centerQuery.data;
  const tradelineFindings =
    data?.findings?.documents.flatMap((doc) =>
      doc.findings.filter((finding) => finding.tradeline_index != null),
    ) ?? [];

  if (centerQuery.isError) {
    const status =
      centerQuery.error instanceof ApiClientError ? centerQuery.error.status : undefined;
    if (status === 404 || status === 403) {
      return null;
    }
  }

  const hasWork =
    Boolean(data?.banner_active) ||
    tradelineFindings.length > 0 ||
    (data?.account_reviews.length ?? 0) > 0;

  if (!centerQuery.isLoading && !hasWork && !centerQuery.isError) {
    return null;
  }

  return (
    <div className="mt-8 border-t border-gray-200 pt-8">
      {data?.banner_active ? (
        <div className="mb-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3">
          <p className="text-sm font-semibold text-amber-950">
            {data.banner_title ?? t('identityTheft.bannerTitle')}
          </p>
          <p className="mt-1 text-sm text-amber-900">
            {data.banner_body ?? t('identityTheft.bannerBody')}
          </p>
        </div>
      ) : null}

      <Card title={t('identityTheft.title')}>
        <p className="text-sm text-gray-500">{t('identityTheft.subtitle')}</p>

        {centerQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">{t('identityTheft.loading')}</p>
        ) : null}

        {centerQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {centerQuery.error instanceof Error
              ? centerQuery.error.message
              : t('identityTheft.loadError')}
          </p>
        ) : null}

        {tradelineFindings.length > 0 ? (
          <ul className="mt-4 space-y-3">
            {tradelineFindings.map((finding) => (
              <li
                key={`${finding.rule_id}-${finding.tradeline_index}-${finding.creditor_name ?? ''}`}
                className="rounded-md border border-gray-200 px-4 py-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {finding.creditor_name ?? t('identityTheft.unknownCreditor')}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">{finding.title}</p>
                  </div>
                  {finding.ordinary_dispute_locked ? (
                    <Badge variant="danger">{t('identityTheft.reviewNeeded')}</Badge>
                  ) : null}
                </div>
                <p className="mt-2 text-sm text-gray-600">{finding.description}</p>
                <button
                  type="button"
                  className="mt-3 rounded-md bg-gray-200 px-3 py-1.5 text-sm font-medium text-gray-900 hover:bg-gray-300"
                  onClick={() => {
                    setSelectedFinding(finding);
                    setSuccess(null);
                    setError(null);
                  }}
                >
                  {t('identityTheft.reviewAccount')}
                </button>
              </li>
            ))}
          </ul>
        ) : null}

        {selectedFinding ? (
          <div className="mt-6 rounded-md border border-brand-200 bg-brand-50/40 p-4">
            <h4 className="text-sm font-medium text-gray-900">{t('identityTheft.confirmTitle')}</h4>
            <p className="mt-1 text-sm text-gray-600">
              {selectedFinding.creditor_name ?? t('identityTheft.unknownCreditor')}
            </p>
            <label className="mt-3 block text-xs font-medium text-gray-700">
              {t('identityTheft.confirmationLabel')}
            </label>
            <select
              className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value as IdentityTheftConfirmation)}
            >
              {CONFIRMATION_KEYS.map((key) => (
                <option key={key} value={key}>
                  {t(`identityTheft.options.${key}`)}
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
                <span>{data?.attestation_text ?? t('identityTheft.attestationFallback')}</span>
              </label>
            ) : null}
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                disabled={confirmMutation.isPending}
                onClick={() => confirmMutation.mutate()}
              >
                {confirmMutation.isPending
                  ? t('identityTheft.saving')
                  : t('identityTheft.saveConfirmation')}
              </button>
              <button
                type="button"
                className="rounded-md bg-gray-200 px-3 py-1.5 text-sm font-medium text-gray-900 hover:bg-gray-300"
                onClick={() => {
                  setSelectedFinding(null);
                  setAttestation(false);
                }}
              >
                {t('identityTheft.cancel')}
              </button>
            </div>
          </div>
        ) : null}

        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        {success ? <p className="mt-3 text-sm text-green-700">{success}</p> : null}

        {data && data.account_reviews.length > 0 ? (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-900">{t('identityTheft.priorReviews')}</h4>
            <ul className="mt-2 space-y-2 text-sm text-gray-700">
              {data.account_reviews.map((review) => (
                <li key={review.id} className="rounded-md border border-gray-200 px-3 py-2">
                  {review.creditor_name ?? t('identityTheft.unknownCreditor')}
                  {review.consumer_confirmation
                    ? ` · ${t(`identityTheft.options.${review.consumer_confirmation}`)}`
                    : ''}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
