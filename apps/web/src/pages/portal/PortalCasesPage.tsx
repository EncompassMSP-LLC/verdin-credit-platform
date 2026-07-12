import { useQuery } from '@tanstack/react-query';
import { listPortalCases } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { translatePortalKey } from '../../i18n/portalLabels';
import { usePortalAuth } from '../../lib/portal-auth';

function formatDate(value: string, locale: string) {
  return new Date(value).toLocaleDateString(locale);
}

export function PortalCasesPage() {
  const { t, i18n } = useTranslation('portal');
  const { t: tCommon } = useTranslation('common');
  const { user, logout } = usePortalAuth();

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['portal-cases'],
    queryFn: listPortalCases,
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              {t('brand')}
            </p>
            <h1 className="mt-1 text-3xl font-bold text-gray-900">{t('cases.title')}</h1>
            <p className="mt-2 text-gray-600">
              {t('cases.welcome', { name: user?.client_display_name ?? '' })}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <LanguageSwitcher compact />
            <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? tCommon('refreshing') : tCommon('refresh')}
            </Button>
            <Button variant="secondary" onClick={logout}>
              {tCommon('signOut')}
            </Button>
          </div>
        </div>

        {isLoading ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">{t('cases.loading')}</p>
          </Card>
        ) : null}

        {isError ? (
          <Card>
            <p className="py-8 text-center text-sm text-red-600">
              {t('cases.loadError')}:{' '}
              {error instanceof Error ? error.message : tCommon('unknownError')}
            </p>
          </Card>
        ) : null}

        {data && data.items.length === 0 ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">{t('cases.empty')}</p>
          </Card>
        ) : null}

        {data && data.items.length > 0 ? (
          <div className="space-y-4">
            {data.items.map((item) => (
              <Card key={item.id} className="p-6">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">{item.title}</h2>
                    <p className="mt-1 text-sm text-gray-500">
                      {item.case_number
                        ? t('cases.caseNumber', { number: item.case_number })
                        : t('cases.caseInProgress')}
                    </p>
                    <p className="mt-2 text-sm text-gray-600">
                      {t('cases.status')}:{' '}
                      <span className="font-medium">
                        {translatePortalKey(t, 'status', item.status)}
                      </span>
                      {' · '}
                      {t('cases.stage')}:{' '}
                      <span className="font-medium">
                        {translatePortalKey(t, 'stage', item.stage)}
                      </span>
                    </p>
                    <p className="mt-1 text-xs text-gray-400">
                      {t('cases.opened', {
                        date: formatDate(item.opened_at, i18n.language),
                      })}
                    </p>
                  </div>
                  <Link to={`/portal/cases/${item.id}`}>
                    <Button>{t('cases.viewProgress')}</Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
