import { useQuery } from '@tanstack/react-query';
import { getPortalCase } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { Link, useParams } from 'react-router-dom';
import { PortalCaseDocuments } from '../../components/portal/PortalCaseDocuments';
import { PortalCaseMessages } from '../../components/portal/PortalCaseMessages';
import { usePortalAuth } from '../../lib/portal-auth';

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleDateString() : '—';
}

export function PortalCaseDetailPage() {
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
        <div className="mb-8 flex items-center justify-between gap-4">
          <Link to="/portal" className="text-sm font-medium text-brand-600 hover:text-brand-700">
            ← Back to cases
          </Link>
          <Button variant="secondary" onClick={logout}>
            Sign out
          </Button>
        </div>

        {isLoading ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">Loading case progress…</p>
          </Card>
        ) : null}

        {isError ? (
          <Card>
            <p className="py-8 text-center text-sm text-red-600">
              Failed to load case: {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </Card>
        ) : null}

        {data ? (
          <Card className="p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              Case Progress
            </p>
            <h1 className="mt-2 text-3xl font-bold text-gray-900">{data.title}</h1>
            <p className="mt-2 text-sm text-gray-500">
              {data.case_number ? `Case ${data.case_number}` : 'Case in progress'}
            </p>

            <dl className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-gray-500">Status</dt>
                <dd className="mt-1 text-lg font-medium capitalize text-gray-900">
                  {data.status.replace('_', ' ')}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Stage</dt>
                <dd className="mt-1 text-lg font-medium capitalize text-gray-900">
                  {data.stage.replace('_', ' ')}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Opened</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.opened_at)}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Closed</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.closed_at)}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Accounts tracked</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">{data.account_count}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Last updated</dt>
                <dd className="mt-1 text-lg font-medium text-gray-900">
                  {formatDate(data.updated_at)}
                </dd>
              </div>
            </dl>

            {Object.keys(data.dispute_accounts).length > 0 ? (
              <div className="mt-8">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
                  Dispute progress
                </h2>
                <ul className="mt-4 space-y-2">
                  {Object.entries(data.dispute_accounts).map(([status, count]) => (
                    <li
                      key={status}
                      className="flex items-center justify-between rounded-md border border-gray-200 px-4 py-3 text-sm"
                    >
                      <span className="capitalize text-gray-700">{status.replace('_', ' ')}</span>
                      <span className="font-medium text-gray-900">{count}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {caseId ? <PortalCaseDocuments caseId={caseId} /> : null}
            {caseId ? <PortalCaseMessages caseId={caseId} /> : null}
          </Card>
        ) : null}
      </div>
    </div>
  );
}
