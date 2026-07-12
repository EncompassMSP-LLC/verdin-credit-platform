import { useQuery } from '@tanstack/react-query';
import { getPortalCase } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { PortalCaseConsents } from '../../components/portal/PortalCaseConsents';
import { PortalCaseDocuments } from '../../components/portal/PortalCaseDocuments';
import { PortalCaseMessages } from '../../components/portal/PortalCaseMessages';
import { PortalEnrollmentOnboarding } from '../../components/portal/PortalEnrollmentOnboarding';
import { PortalPushPanel } from '../../components/portal/PortalPushPanel';
import { translatePortalKey } from '../../i18n/portalLabels';
import { usePortalAuth } from '../../lib/portal-auth';

function formatDate(value: string | null, locale: string, empty: string) {
  return value ? new Date(value).toLocaleDateString(locale) : empty;
}

export function PortalCaseDetailPage() {
  const { t, i18n } = useTranslation('portal');
  const { t: tCommon } = useTranslation('common');
  const { caseId } = useParams<{ caseId: string }>();
  const { logout } = usePortalAuth();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['portal-case', caseId],
    queryFn: () => getPortalCase(caseId!),
    enabled: Boolean(caseId),
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <Link to="/portal" className="text-sm font-medium text-brand-600 hover:text-brand-700">
            {t('caseDetail.back')}
          </Link>
          <div className="flex flex-wrap items-center gap-2">
            <LanguageSwitcher compact />
            <Button variant="secondary" onClick={logout}>
              {tCommon('signOut')}
            </Button>
          </div>
        </div>

        {isLoading ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">{t('caseDetail.loading')}</p>
          </Card>
        ) : null}

        {isError ? (
          <Card>
            <p className="py-8 text-center text-sm text-red-600">
              {t('caseDetail.loadError')}:{' '}
              {error instanceof Error ? error.message : tCommon('unknownError')}
            </p>
          </Card>
        ) : null}

        {data ? (
          <Card className="p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              {t('caseDetail.progressLabel')}
            </p>
            <h1 className="mt-2 text-3xl font-bold text-gray-900">{data.title}</h1>
            <p className="mt-2 text-sm text-gray-500">
              {data.case_number
                ? t('caseDetail.caseNumber', { number: data.case_number })
                : t('caseDetail.caseInProgress')}
            </p>

            <dl className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.status')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {translatePortalKey(t, 'status', data.status)}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.stage')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {translatePortalKey(t, 'stage', data.stage)}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.opened')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.opened_at, i18n.language, tCommon('emDash'))}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.closed')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.closed_at, i18n.language, tCommon('emDash'))}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.accountsTracked')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">{data.account_count}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">{t('caseDetail.lastUpdated')}</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.updated_at, i18n.language, tCommon('emDash'))}
                </dd>
              </div>
            </dl>

            {Object.keys(data.dispute_accounts).length > 0 ? (
              <div className="mt-8">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
                  {t('caseDetail.disputeProgress')}
                </h2>
                <ul className="mt-4 space-y-2">
                  {Object.entries(data.dispute_accounts).map(([status, count]) => (
                    <li
                      key={status}
                      className="flex items-center justify-between rounded-md border border-gray-200 px-4 py-3 text-sm"
                    >
                      <span className="text-gray-700">
                        {translatePortalKey(t, 'disputeStatus', status)}
                      </span>
                      <span className="font-medium text-gray-900">{count}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            <PortalEnrollmentOnboarding annualCreditReportUrl="https://www.annualcreditreport.com/index.action" />

            {caseId ? <PortalCaseConsents caseId={caseId} /> : null}
            {caseId ? <PortalCaseDocuments caseId={caseId} /> : null}
            <PortalPushPanel />
            {caseId ? <PortalCaseMessages caseId={caseId} /> : null}
          </Card>
        ) : null}
      </div>
    </div>
  );
}
