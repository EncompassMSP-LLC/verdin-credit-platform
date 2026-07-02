import { useQuery } from '@tanstack/react-query';
import { listPortalCases } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';
import { usePortalAuth } from '../../lib/portal-auth';

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

export function PortalCasesPage() {
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
              Client Portal
            </p>
            <h1 className="mt-1 text-3xl font-bold text-gray-900">Your Cases</h1>
            <p className="mt-2 text-gray-600">
              Welcome, {user?.client_display_name}. Track progress on your credit repair cases.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? 'Refreshing…' : 'Refresh'}
            </Button>
            <Button variant="secondary" onClick={logout}>
              Sign out
            </Button>
          </div>
        </div>

        {isLoading ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">Loading your cases…</p>
          </Card>
        ) : null}

        {isError ? (
          <Card>
            <p className="py-8 text-center text-sm text-red-600">
              Failed to load cases: {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </Card>
        ) : null}

        {data && data.items.length === 0 ? (
          <Card>
            <p className="py-12 text-center text-sm text-gray-500">
              No cases are linked to your portal account yet.
            </p>
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
                      {item.case_number ? `Case ${item.case_number}` : 'Case in progress'}
                    </p>
                    <p className="mt-2 text-sm text-gray-600">
                      Status:{' '}
                      <span className="font-medium capitalize">
                        {item.status.replace('_', ' ')}
                      </span>
                      {' · '}
                      Stage:{' '}
                      <span className="font-medium capitalize">{item.stage.replace('_', ' ')}</span>
                    </p>
                    <p className="mt-1 text-xs text-gray-400">
                      Opened {formatDate(item.opened_at)}
                    </p>
                  </div>
                  <Link to={`/portal/cases/${item.id}`}>
                    <Button>View progress</Button>
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
