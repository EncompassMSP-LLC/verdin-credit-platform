'use client';

import {
  ApiClientError,
  getClientCommunicationPreferences,
  markClientDncCompleted,
  openClientDncRegistry,
  updateClientCommunicationPreferences,
  type ClientCommunicationPreferences,
  type UpdateClientCommunicationPreferencesInput,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { useCrmAuth } from '@/lib/crm/auth';

type Props = {
  clientId: string | undefined;
  canManage: boolean;
};

export function CrmCommunicationPreferencesPanel({ clientId, canManage }: Props) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const queryClient = useQueryClient();
  const [formError, setFormError] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['crm', 'communication-preferences', clientId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(clientId),
    queryFn: () => getClientCommunicationPreferences(clientId!),
    retry: false,
  });

  const saveMutation = useMutation({
    mutationFn: (input: UpdateClientCommunicationPreferencesInput) =>
      updateClientCommunicationPreferences(clientId!, input),
    onSuccess: async (data) => {
      setFormError(null);
      queryClient.setQueryData(['crm', 'communication-preferences', clientId], data);
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : 'Save failed');
    },
  });

  const openRegistryMutation = useMutation({
    mutationFn: () => openClientDncRegistry(clientId!),
    onSuccess: async (data) => {
      setFormError(null);
      queryClient.setQueryData(['crm', 'communication-preferences', clientId], data);
      if (typeof window !== 'undefined') {
        window.open(data.official_dnc_registry_url, '_blank', 'noopener,noreferrer');
      }
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : 'Could not open registry workflow');
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => markClientDncCompleted(clientId!),
    onSuccess: async (data) => {
      setFormError(null);
      queryClient.setQueryData(['crm', 'communication-preferences', clientId], data);
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : 'Could not mark complete');
    },
  });

  if (!clientId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Communication preferences</h2>
        <p className="mt-2 text-sm text-slate-500">Link a borrower record to manage preferences.</p>
      </div>
    );
  }

  if (authMode !== 'platform') {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Communication preferences</h2>
        <p className="mt-2 text-sm text-slate-500">Requires platform authentication.</p>
      </div>
    );
  }

  const prefs = query.data;

  return (
    <div className="rounded-md border border-navy-900/10 bg-white p-4">
      <h2 className="text-sm font-semibold">Communication preferences</h2>
      <p className="mt-2 text-sm text-slate-500">
        Track creditor/collector contact preferences and guided National Do Not Call assistance.
        Never silently registers a phone number and never auto-sends letters.
      </p>

      {query.isLoading ? <p className="mt-3 text-sm text-slate-500">Loading preferences…</p> : null}

      {query.isError ? (
        <p className="mt-3 text-sm text-red-700">
          {query.error instanceof ApiClientError
            ? query.error.message
            : query.error instanceof Error
              ? query.error.message
              : 'Failed to load preferences'}
        </p>
      ) : null}

      {prefs ? (
        <PreferencesForm
          key={prefs.updated_at}
          prefs={prefs}
          canManage={canManage}
          saving={saveMutation.isPending}
          opening={openRegistryMutation.isPending}
          completing={completeMutation.isPending}
          formError={formError}
          onSave={(input) => saveMutation.mutate(input)}
          onOpenRegistry={() => openRegistryMutation.mutate()}
          onMarkCompleted={() => completeMutation.mutate()}
        />
      ) : null}
    </div>
  );
}

function PreferencesForm({
  prefs,
  canManage,
  saving,
  opening,
  completing,
  formError,
  onSave,
  onOpenRegistry,
  onMarkCompleted,
}: {
  prefs: ClientCommunicationPreferences;
  canManage: boolean;
  saving: boolean;
  opening: boolean;
  completing: boolean;
  formError: string | null;
  onSave: (input: UpdateClientCommunicationPreferencesInput) => void;
  onOpenRegistry: () => void;
  onMarkCompleted: () => void;
}) {
  const [preferredChannel, setPreferredChannel] = useState(prefs.preferred_channel);
  const [doNotText, setDoNotText] = useState(prefs.do_not_text);
  const [doNotEmail, setDoNotEmail] = useState(prefs.do_not_email);
  const [bestHours, setBestHours] = useState(prefs.best_calling_hours ?? '');
  const [workplaceProhibited, setWorkplaceProhibited] = useState(prefs.workplace_calls_prohibited);
  const [attorneyStatus, setAttorneyStatus] = useState(prefs.attorney_representation_status);
  const [collectorOptOut, setCollectorOptOut] = useState(prefs.collector_opt_out_recorded);
  const [dncRequested, setDncRequested] = useState(prefs.dnc_assistance_requested);
  const [dncConsent, setDncConsent] = useState(prefs.dnc_consent_attested);
  const [dncOwnership, setDncOwnership] = useState(prefs.dnc_phone_ownership_confirmed);
  const [dncDisclosure, setDncDisclosure] = useState(prefs.dnc_disclosure_acknowledged);
  const [dncPhone, setDncPhone] = useState(prefs.dnc_phone_number ?? '');

  return (
    <div className="mt-3 space-y-4">
      <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-950">{prefs.disclaimer}</p>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="text-sm text-slate-700">
          Preferred channel
          <select
            className="mt-1 w-full rounded-md border border-navy-900/20 px-2 py-1.5 text-sm"
            value={preferredChannel}
            disabled={!canManage}
            onChange={(e) =>
              setPreferredChannel(
                e.target.value as ClientCommunicationPreferences['preferred_channel'],
              )
            }
          >
            <option value="mail">Mail</option>
            <option value="phone">Phone</option>
            <option value="email">Email</option>
            <option value="text">Text</option>
          </select>
        </label>
        <label className="text-sm text-slate-700">
          Best calling hours
          <input
            className="mt-1 w-full rounded-md border border-navy-900/20 px-2 py-1.5 text-sm"
            value={bestHours}
            disabled={!canManage}
            onChange={(e) => setBestHours(e.target.value)}
            placeholder="e.g. Weekdays 10am–2pm ET"
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-4 text-sm text-slate-700">
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={doNotText}
            disabled={!canManage}
            onChange={(e) => setDoNotText(e.target.checked)}
          />
          Do not text
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={doNotEmail}
            disabled={!canManage}
            onChange={(e) => setDoNotEmail(e.target.checked)}
          />
          Do not email
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={workplaceProhibited}
            disabled={!canManage}
            onChange={(e) => setWorkplaceProhibited(e.target.checked)}
          />
          Workplace calls prohibited
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={collectorOptOut}
            disabled={!canManage}
            onChange={(e) => setCollectorOptOut(e.target.checked)}
          />
          Collector opt-out recorded
        </label>
      </div>

      <label className="block text-sm text-slate-700">
        Attorney representation
        <select
          className="mt-1 w-full max-w-xs rounded-md border border-navy-900/20 px-2 py-1.5 text-sm"
          value={attorneyStatus}
          disabled={!canManage}
          onChange={(e) =>
            setAttorneyStatus(
              e.target.value as ClientCommunicationPreferences['attorney_representation_status'],
            )
          }
        >
          <option value="unknown">Unknown</option>
          <option value="none">None</option>
          <option value="represented">Represented</option>
        </select>
      </label>

      <div className="rounded-md border border-navy-900/10 bg-slate-50 p-3">
        <h3 className="text-sm font-semibold text-navy-900">Do Not Call assistance</h3>
        <p className="mt-1 text-xs text-slate-600">{prefs.dnc_disclosure}</p>
        <p className="mt-2 text-xs text-slate-500">
          Status: {prefs.dnc_status.replace(/_/g, ' ')}
          {prefs.dnc_followup_due_at
            ? ` · 31-day follow-up due ${new Date(prefs.dnc_followup_due_at).toLocaleDateString()}`
            : ''}
        </p>
        <div className="mt-3 space-y-2 text-sm text-slate-700">
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={dncRequested}
              disabled={!canManage}
              onChange={(e) => setDncRequested(e.target.checked)}
            />
            Help me register this personal phone number on the National Do Not Call Registry
          </label>
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={dncConsent}
              disabled={!canManage}
              onChange={(e) => setDncConsent(e.target.checked)}
            />
            Explicit consent to assist with registration
          </label>
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={dncOwnership}
              disabled={!canManage}
              onChange={(e) => setDncOwnership(e.target.checked)}
            />
            I confirm I own or control this phone number
          </label>
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={dncDisclosure}
              disabled={!canManage}
              onChange={(e) => setDncDisclosure(e.target.checked)}
            />
            I understand the telemarketing limitation disclosure above
          </label>
          <label className="block text-sm">
            Phone number for registry
            <input
              className="mt-1 w-full max-w-xs rounded-md border border-navy-900/20 px-2 py-1.5 text-sm"
              value={dncPhone}
              disabled={!canManage}
              onChange={(e) => setDncPhone(e.target.value)}
            />
          </label>
        </div>
      </div>

      {canManage ? (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md bg-navy-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
            disabled={saving}
            onClick={() =>
              onSave({
                preferred_channel: preferredChannel,
                do_not_text: doNotText,
                do_not_email: doNotEmail,
                best_calling_hours: bestHours.trim() || null,
                workplace_calls_prohibited: workplaceProhibited,
                attorney_representation_status: attorneyStatus,
                collector_opt_out_recorded: collectorOptOut,
                dnc_assistance_requested: dncRequested,
                dnc_consent_attested: dncConsent,
                dnc_phone_ownership_confirmed: dncOwnership,
                dnc_disclosure_acknowledged: dncDisclosure,
                dnc_phone_number: dncPhone.trim() || null,
              })
            }
          >
            {saving ? 'Saving…' : 'Save preferences'}
          </button>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border border-navy-900/20 px-3 py-2 text-sm font-medium text-navy-900 disabled:opacity-60"
            disabled={opening || prefs.dnc_status === 'completed'}
            onClick={onOpenRegistry}
          >
            {opening ? 'Opening…' : 'Open official registry'}
          </button>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border border-navy-900/20 px-3 py-2 text-sm font-medium text-navy-900 disabled:opacity-60"
            disabled={completing || prefs.dnc_status === 'completed'}
            onClick={onMarkCompleted}
          >
            {completing ? 'Saving…' : 'Mark registration complete'}
          </button>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Requires borrowers.manage to edit.</p>
      )}

      {formError ? <p className="text-sm text-red-700">{formError}</p> : null}

      <details className="text-sm text-slate-600">
        <summary className="cursor-pointer font-medium text-navy-900">
          Communication-request letter draft
        </summary>
        <pre className="mt-2 whitespace-pre-wrap rounded-md bg-slate-50 p-3 text-xs">
          {prefs.communication_request_draft}
        </pre>
      </details>
    </div>
  );
}
