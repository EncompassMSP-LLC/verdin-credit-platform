import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createOrganizationApiKey,
  getOrgAdminStatus,
  getOrganizationAdminSummary,
  listOrganizationApiKeys,
  revokeOrganizationApiKey,
  type ApiKey,
  type ApiKeyScope,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { DashboardMetricCard } from '../../components/dashboard/DashboardMetricCard';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : '—';
}

function formatLabel(value: string) {
  return value.replaceAll('_', ' ');
}

export function OrgAdminPage() {
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  if (!featureFlags.enableEnterprise) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">
            Org admin requires <code className="text-xs">VITE_ENABLE_ENTERPRISE=true</code>.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Organization admin</h1>
        <p className="mt-1 text-gray-500">
          Review organization summary and manage API keys for integrations.
        </p>
      </div>

      <OrgAdminStatusCard />
      <OrganizationSummaryCard />
      <ApiKeysPanel onKeyCreated={setCreatedKey} />

      {createdKey ? (
        <Card className="mt-6 border-amber-200 bg-amber-50" title="API key created">
          <p className="text-sm text-amber-900">Copy this key now. It will not be shown again.</p>
          <pre className="mt-3 overflow-x-auto rounded-md bg-white p-3 text-sm text-gray-900">
            {createdKey}
          </pre>
          <Button className="mt-4" variant="secondary" onClick={() => setCreatedKey(null)}>
            Dismiss
          </Button>
        </Card>
      ) : null}
    </div>
  );
}

function OrgAdminStatusCard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['org-admin-status'],
    queryFn: getOrgAdminStatus,
  });

  if (isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading org admin status…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-red-600">Failed to load org admin status.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-6" title="Capabilities">
      <div className="flex flex-wrap gap-2">
        {data.capabilities.map((capability) => (
          <Badge key={capability} variant="success">
            {formatLabel(capability)}
          </Badge>
        ))}
        {data.deferred_capabilities.map((capability) => (
          <Badge key={capability} variant="default">
            {formatLabel(capability)} (deferred)
          </Badge>
        ))}
      </div>
    </Card>
  );
}

function OrganizationSummaryCard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['org-admin-summary'],
    queryFn: getOrganizationAdminSummary,
  });

  if (isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading organization summary…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-red-600">Failed to load organization summary.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-6" title={data.name}>
      <p className="text-sm text-gray-500">Slug: {data.slug}</p>
      <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3">
        <DashboardMetricCard label="Active users" value={data.active_user_count} />
        <DashboardMetricCard
          label="Active API keys"
          value={data.active_api_key_count}
          tone="info"
        />
        <DashboardMetricCard
          label="Organization status"
          value={data.is_active ? 'Active' : 'Inactive'}
          tone={data.is_active ? 'success' : 'warning'}
        />
      </div>
    </Card>
  );
}

function ApiKeysPanel({ onKeyCreated }: { onKeyCreated: (key: string) => void }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [scopes, setScopes] = useState<ApiKeyScope[]>(['read']);
  const [error, setError] = useState<string | null>(null);

  const keysQuery = useQuery({
    queryKey: ['org-admin-api-keys'],
    queryFn: listOrganizationApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: () => {
      if (!name.trim()) throw new Error('Key name is required');
      if (scopes.length === 0) throw new Error('Select at least one scope');
      return createOrganizationApiKey({ name: name.trim(), scopes });
    },
    onSuccess: (result) => {
      void queryClient.invalidateQueries({ queryKey: ['org-admin-api-keys'] });
      void queryClient.invalidateQueries({ queryKey: ['org-admin-summary'] });
      onKeyCreated(result.api_key);
      setName('');
      setScopes(['read']);
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  const revokeMutation = useMutation({
    mutationFn: (apiKeyId: string) => revokeOrganizationApiKey(apiKeyId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['org-admin-api-keys'] });
      void queryClient.invalidateQueries({ queryKey: ['org-admin-summary'] });
    },
  });

  const toggleScope = (scope: ApiKeyScope) => {
    setScopes((current) =>
      current.includes(scope) ? current.filter((value) => value !== scope) : [...current, scope],
    );
  };

  return (
    <div className="space-y-6">
      <Card title="Create API key">
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setError(null);
            createMutation.mutate();
          }}
        >
          <div>
            <label htmlFor="api-key-name" className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              id="api-key-name"
              className={inputClass}
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Integration name"
              required
            />
          </div>

          <fieldset>
            <legend className="text-sm font-medium text-gray-700">Scopes</legend>
            <div className="mt-2 flex gap-4">
              {(['read', 'write'] as ApiKeyScope[]).map((scope) => (
                <label key={scope} className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={scopes.includes(scope)}
                    onChange={() => toggleScope(scope)}
                  />
                  {scope}
                </label>
              ))}
            </div>
          </fieldset>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <Button type="submit" loading={createMutation.isPending}>
            Create API key
          </Button>
        </form>
      </Card>

      <Card title="API keys">
        {keysQuery.isLoading ? <p className="text-sm text-gray-500">Loading API keys…</p> : null}
        {keysQuery.isError ? (
          <p className="text-sm text-red-600">Failed to load API keys.</p>
        ) : null}
        {keysQuery.data && keysQuery.data.length === 0 ? (
          <p className="text-sm text-gray-500">No API keys yet.</p>
        ) : null}
        {keysQuery.data && keysQuery.data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Name</th>
                  <th className="px-3 py-2 font-medium">Prefix</th>
                  <th className="px-3 py-2 font-medium">Scopes</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Last used</th>
                  <th className="px-3 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {keysQuery.data.map((key) => (
                  <ApiKeyRow
                    key={key.id}
                    apiKey={key}
                    onRevoke={() => revokeMutation.mutate(key.id)}
                    revoking={revokeMutation.isPending}
                  />
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </Card>
    </div>
  );
}

function ApiKeyRow({
  apiKey,
  onRevoke,
  revoking,
}: {
  apiKey: ApiKey;
  onRevoke: () => void;
  revoking: boolean;
}) {
  const isActive = apiKey.is_active && !apiKey.revoked_at;

  return (
    <tr className="border-b border-gray-100">
      <td className="px-3 py-3 font-medium text-gray-900">{apiKey.name}</td>
      <td className="px-3 py-3 font-mono text-xs text-gray-600">{apiKey.key_prefix}…</td>
      <td className="px-3 py-3">{apiKey.scopes.join(', ')}</td>
      <td className="px-3 py-3">
        <Badge variant={isActive ? 'success' : 'default'}>{isActive ? 'Active' : 'Revoked'}</Badge>
      </td>
      <td className="px-3 py-3">{formatDate(apiKey.last_used_at)}</td>
      <td className="px-3 py-3">
        {isActive ? (
          <Button type="button" size="sm" variant="secondary" loading={revoking} onClick={onRevoke}>
            Revoke
          </Button>
        ) : (
          '—'
        )}
      </td>
    </tr>
  );
}
