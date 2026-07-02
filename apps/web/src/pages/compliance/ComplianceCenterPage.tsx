import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createConsentRecord,
  createRetentionPolicy,
  getComplianceCenterStatus,
  listClients,
  listConsentRecords,
  listRetentionPolicies,
  withdrawConsentRecord,
  type ConsentType,
  type RetentionScope,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const CONSENT_TYPE_LABELS: Record<ConsentType, string> = {
  croa_services: 'CROA services',
  fcra_dispute: 'FCRA dispute',
  fdcpa_contact: 'FDCPA contact',
  marketing: 'Marketing',
  data_processing: 'Data processing',
};

const RETENTION_SCOPE_LABELS: Record<RetentionScope, string> = {
  documents: 'Documents',
  communications: 'Communications',
  audit_logs: 'Audit logs',
  client_profiles: 'Client profiles',
};

type ComplianceTab = 'consents' | 'retention';

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : '—';
}

export function ComplianceCenterPage() {
  const [tab, setTab] = useState<ComplianceTab>('consents');

  if (!featureFlags.enableEnterprise) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">
            Compliance center requires <code className="text-xs">VITE_ENABLE_ENTERPRISE=true</code>.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Compliance center</h1>
        <p className="mt-1 text-gray-500">
          Track client consent records and configure retention policy placeholders.
        </p>
      </div>

      <ComplianceStatusCard />

      <div className="mb-6 flex gap-2">
        <Button
          type="button"
          variant={tab === 'consents' ? 'primary' : 'secondary'}
          onClick={() => setTab('consents')}
        >
          Consent records
        </Button>
        <Button
          type="button"
          variant={tab === 'retention' ? 'primary' : 'secondary'}
          onClick={() => setTab('retention')}
        >
          Retention policies
        </Button>
      </div>

      {tab === 'consents' ? <ConsentRecordsPanel /> : <RetentionPoliciesPanel />}
    </div>
  );
}

function ComplianceStatusCard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['compliance-status'],
    queryFn: getComplianceCenterStatus,
  });

  if (isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading compliance status…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-red-600">Failed to load compliance center status.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-6" title="Capabilities">
      <div className="flex flex-wrap gap-2">
        {data.capabilities.map((capability) => (
          <Badge key={capability} variant="success">
            {capability.replaceAll('_', ' ')}
          </Badge>
        ))}
        {data.deferred_capabilities.map((capability) => (
          <Badge key={capability} variant="default">
            {capability.replaceAll('_', ' ')} (deferred)
          </Badge>
        ))}
      </div>
    </Card>
  );
}

function ConsentRecordsPanel() {
  const queryClient = useQueryClient();
  const [clientId, setClientId] = useState('');
  const [consentType, setConsentType] = useState<ConsentType>('croa_services');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  const clientsQuery = useQuery({
    queryKey: ['clients-for-compliance'],
    queryFn: () => listClients({ page_size: 100, status: 'active' }),
  });

  const consentsQuery = useQuery({
    queryKey: ['compliance-consents'],
    queryFn: () => listConsentRecords({ page_size: 50, sort_by: 'granted_at', sort_order: 'desc' }),
  });

  const createMutation = useMutation({
    mutationFn: () => {
      if (!clientId) throw new Error('Client is required');
      return createConsentRecord({
        client_id: clientId,
        consent_type: consentType,
        notes: notes.trim() || null,
        source: 'staff_ui',
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['compliance-consents'] });
      setNotes('');
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  const withdrawMutation = useMutation({
    mutationFn: (consentId: string) => withdrawConsentRecord(consentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['compliance-consents'] });
    },
  });

  const clientNameById = useMemo(() => {
    const map = new Map<string, string>();
    for (const client of clientsQuery.data?.items ?? []) {
      map.set(client.id, client.display_name);
    }
    return map;
  }, [clientsQuery.data?.items]);

  return (
    <div className="space-y-6">
      <Card title="Record consent">
        <form
          className="grid grid-cols-1 gap-4 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            setError(null);
            createMutation.mutate();
          }}
        >
          <div>
            <label htmlFor="consent-client" className="block text-sm font-medium text-gray-700">
              Client
            </label>
            <select
              id="consent-client"
              className={inputClass}
              value={clientId}
              onChange={(event) => setClientId(event.target.value)}
              required
            >
              <option value="">Select client</option>
              {clientsQuery.data?.items.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.display_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="consent-type" className="block text-sm font-medium text-gray-700">
              Consent type
            </label>
            <select
              id="consent-type"
              className={inputClass}
              value={consentType}
              onChange={(event) => setConsentType(event.target.value as ConsentType)}
            >
              {(Object.keys(CONSENT_TYPE_LABELS) as ConsentType[]).map((type) => (
                <option key={type} value={type}>
                  {CONSENT_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2">
            <label htmlFor="consent-notes" className="block text-sm font-medium text-gray-700">
              Notes
            </label>
            <textarea
              id="consent-notes"
              rows={2}
              className={inputClass}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </div>
          {error ? (
            <div className="md:col-span-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}
          <div className="md:col-span-2">
            <Button type="submit" loading={createMutation.isPending}>
              Record consent
            </Button>
          </div>
        </form>
      </Card>

      <Card title="Consent records">
        {consentsQuery.isLoading ? (
          <p className="text-sm text-gray-500">Loading consent records…</p>
        ) : null}
        {consentsQuery.isError ? (
          <p className="text-sm text-red-600">Failed to load consent records.</p>
        ) : null}
        {consentsQuery.data && consentsQuery.data.items.length === 0 ? (
          <p className="text-sm text-gray-500">No consent records yet.</p>
        ) : null}
        {consentsQuery.data && consentsQuery.data.items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Client</th>
                  <th className="px-3 py-2 font-medium">Type</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Granted</th>
                  <th className="px-3 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {consentsQuery.data.items.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100">
                    <td className="px-3 py-3">
                      {clientNameById.get(record.client_id) ?? record.client_id}
                    </td>
                    <td className="px-3 py-3">{CONSENT_TYPE_LABELS[record.consent_type]}</td>
                    <td className="px-3 py-3">
                      <Badge variant={record.status === 'granted' ? 'success' : 'warning'}>
                        {record.status}
                      </Badge>
                    </td>
                    <td className="px-3 py-3">{formatDate(record.granted_at)}</td>
                    <td className="px-3 py-3">
                      {record.status === 'granted' ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          loading={withdrawMutation.isPending}
                          onClick={() => withdrawMutation.mutate(record.id)}
                        >
                          Withdraw
                        </Button>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </Card>
    </div>
  );
}

function RetentionPoliciesPanel() {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [scope, setScope] = useState<RetentionScope>('documents');
  const [retentionDays, setRetentionDays] = useState('365');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  const policiesQuery = useQuery({
    queryKey: ['compliance-retention-policies'],
    queryFn: () =>
      listRetentionPolicies({ page_size: 50, sort_by: 'created_at', sort_order: 'desc' }),
  });

  const createMutation = useMutation({
    mutationFn: () => {
      const days = Number(retentionDays);
      if (!name.trim()) throw new Error('Policy name is required');
      if (!Number.isFinite(days) || days < 1) throw new Error('Retention days must be at least 1');
      return createRetentionPolicy({
        name: name.trim(),
        scope,
        retention_days: days,
        description: description.trim() || null,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['compliance-retention-policies'] });
      setName('');
      setDescription('');
      setRetentionDays('365');
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  return (
    <div className="space-y-6">
      <Card title="Create retention policy">
        <form
          className="grid grid-cols-1 gap-4 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            setError(null);
            createMutation.mutate();
          }}
        >
          <div>
            <label htmlFor="policy-name" className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              id="policy-name"
              className={inputClass}
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="policy-scope" className="block text-sm font-medium text-gray-700">
              Scope
            </label>
            <select
              id="policy-scope"
              className={inputClass}
              value={scope}
              onChange={(event) => setScope(event.target.value as RetentionScope)}
            >
              {(Object.keys(RETENTION_SCOPE_LABELS) as RetentionScope[]).map((value) => (
                <option key={value} value={value}>
                  {RETENTION_SCOPE_LABELS[value]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="policy-days" className="block text-sm font-medium text-gray-700">
              Retention days
            </label>
            <input
              id="policy-days"
              type="number"
              min={1}
              className={inputClass}
              value={retentionDays}
              onChange={(event) => setRetentionDays(event.target.value)}
              required
            />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="policy-description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="policy-description"
              rows={2}
              className={inputClass}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          {error ? (
            <div className="md:col-span-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}
          <div className="md:col-span-2">
            <Button type="submit" loading={createMutation.isPending}>
              Create policy
            </Button>
          </div>
        </form>
      </Card>

      <Card title="Retention policies">
        {policiesQuery.isLoading ? (
          <p className="text-sm text-gray-500">Loading retention policies…</p>
        ) : null}
        {policiesQuery.isError ? (
          <p className="text-sm text-red-600">Failed to load retention policies.</p>
        ) : null}
        {policiesQuery.data && policiesQuery.data.items.length === 0 ? (
          <p className="text-sm text-gray-500">No retention policies yet.</p>
        ) : null}
        {policiesQuery.data && policiesQuery.data.items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Name</th>
                  <th className="px-3 py-2 font-medium">Scope</th>
                  <th className="px-3 py-2 font-medium">Days</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {policiesQuery.data.items.map((policy) => (
                  <tr key={policy.id} className="border-b border-gray-100">
                    <td className="px-3 py-3 font-medium text-gray-900">{policy.name}</td>
                    <td className="px-3 py-3">{RETENTION_SCOPE_LABELS[policy.scope]}</td>
                    <td className="px-3 py-3">{policy.retention_days}</td>
                    <td className="px-3 py-3">
                      <Badge variant={policy.is_active ? 'success' : 'default'}>
                        {policy.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-3 py-3">{formatDate(policy.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
