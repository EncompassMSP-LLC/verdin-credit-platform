'use client';

import {
  ApiClientError,
  createUnwantedCallIncident,
  listUnwantedCallIncidents,
  updateUnwantedCallIncident,
  type CreateUnwantedCallIncidentInput,
  type UnwantedCallIncident,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { useCrmAuth } from '@/lib/crm/auth';

type Props = {
  clientId: string | undefined;
  caseId?: string | undefined;
  canManage: boolean;
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function IncidentCard({
  clientId,
  incident,
  canManage,
}: {
  clientId: string;
  incident: UnwantedCallIncident;
  canManage: boolean;
}) {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const updateMutation = useMutation({
    mutationFn: (status: UnwantedCallIncident['status']) =>
      updateUnwantedCallIncident(clientId, incident.id, { status }),
    onSuccess: async () => {
      setMessage('Status updated.');
      await queryClient.invalidateQueries({
        queryKey: ['crm', 'unwanted-call-incidents', clientId],
      });
      if (incident.case_id) {
        await queryClient.invalidateQueries({
          queryKey: ['crm', 'case-action-timeline'],
        });
      }
    },
    onError: (error) => {
      setMessage(error instanceof Error ? error.message : 'Update failed');
    },
  });

  const guidanceNotes = incident.eligibility_guidance.notes ?? [];

  return (
    <article className="rounded-md border border-navy-900/10 bg-slate-50 p-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-navy-900">
            {incident.creditor_or_collector_name || incident.party_type} · {incident.channel}
          </p>
          <p className="text-xs text-slate-500">{formatDateTime(incident.called_at)}</p>
        </div>
        <p className="text-xs text-slate-600">{incident.status.replace(/_/g, ' ')}</p>
      </div>
      {incident.caller_number || incident.called_number ? (
        <p className="mt-1 text-xs text-slate-600">
          {incident.caller_number ? `From ${incident.caller_number}` : null}
          {incident.caller_number && incident.called_number ? ' → ' : null}
          {incident.called_number ? `to ${incident.called_number}` : null}
        </p>
      ) : null}
      {guidanceNotes.length > 0 ? (
        <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-slate-700">
          {guidanceNotes.slice(0, 4).map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      ) : null}
      {incident.draft_text ? (
        <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded bg-white p-2 text-xs text-slate-700">
          {incident.draft_text}
        </pre>
      ) : null}
      {canManage ? (
        <div className="mt-2 flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded border border-navy-900/20 bg-white px-2 py-1 text-xs disabled:opacity-50"
            disabled={updateMutation.isPending}
            onClick={() => updateMutation.mutate('follow_up_due')}
          >
            Mark follow-up due
          </button>
          <button
            type="button"
            className="rounded border border-navy-900/20 bg-white px-2 py-1 text-xs disabled:opacity-50"
            disabled={updateMutation.isPending}
            onClick={() => updateMutation.mutate('closed')}
          >
            Close
          </button>
        </div>
      ) : null}
      {message ? <p className="mt-2 text-xs text-slate-600">{message}</p> : null}
    </article>
  );
}

export function CrmUnwantedCallIncidentsPanel({ clientId, caseId, canManage }: Props) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const queryClient = useQueryClient();
  const [formError, setFormError] = useState<string | null>(null);
  const [callerNumber, setCallerNumber] = useState('');
  const [partyName, setPartyName] = useState('');
  const [notes, setNotes] = useState('');
  const [partyType, setPartyType] =
    useState<CreateUnwantedCallIncidentInput['party_type']>('unknown');
  const [complaintTarget, setComplaintTarget] =
    useState<CreateUnwantedCallIncidentInput['complaint_target']>('none');

  const query = useQuery({
    queryKey: ['crm', 'unwanted-call-incidents', clientId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(clientId),
    queryFn: () => listUnwantedCallIncidents(clientId!),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createUnwantedCallIncident(clientId!, {
        called_at: new Date().toISOString(),
        case_id: caseId ?? null,
        caller_number: callerNumber || null,
        creditor_or_collector_name: partyName || null,
        party_type: partyType,
        channel: 'phone',
        notes: notes || null,
        complaint_target: complaintTarget,
      }),
    onSuccess: async () => {
      setFormError(null);
      setCallerNumber('');
      setPartyName('');
      setNotes('');
      await queryClient.invalidateQueries({
        queryKey: ['crm', 'unwanted-call-incidents', clientId],
      });
      if (caseId) {
        await queryClient.invalidateQueries({ queryKey: ['crm', 'case-action-timeline'] });
      }
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : 'Could not log incident');
    },
  });

  if (!clientId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Unwanted-call complaints</h2>
        <p className="mt-2 text-sm text-slate-500">Link a borrower to log unwanted calls.</p>
      </div>
    );
  }

  if (authMode !== 'platform') {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Unwanted-call complaints</h2>
        <p className="mt-2 text-sm text-slate-500">
          Requires platform authentication (demo mode unavailable).
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-navy-900/10 bg-white p-4">
      <h2 className="text-sm font-semibold">Unwanted-call complaints</h2>
      <p className="mt-2 text-sm text-slate-500">
        Staff-mediated incident log with advisory eligibility notes and complaint drafts. Never
        auto-submitted to FTC/CFPB/DNC.
      </p>

      {query.data?.disclaimer ? (
        <p className="mt-2 rounded bg-amber-50 px-3 py-2 text-xs text-amber-950">
          {query.data.disclaimer}
        </p>
      ) : null}

      {canManage ? (
        <div className="mt-3 space-y-2 rounded border border-navy-900/10 bg-slate-50 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Log unwanted call
          </p>
          <input
            className="w-full rounded border border-navy-900/20 px-2 py-1 text-xs"
            placeholder="Caller number"
            value={callerNumber}
            onChange={(event) => setCallerNumber(event.target.value)}
          />
          <input
            className="w-full rounded border border-navy-900/20 px-2 py-1 text-xs"
            placeholder="Creditor / collector / telemarketer name"
            value={partyName}
            onChange={(event) => setPartyName(event.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <select
              className="rounded border border-navy-900/20 px-2 py-1 text-xs"
              value={partyType}
              onChange={(event) =>
                setPartyType(event.target.value as CreateUnwantedCallIncidentInput['party_type'])
              }
            >
              <option value="unknown">Party: unknown</option>
              <option value="creditor">Creditor</option>
              <option value="collector">Collector</option>
              <option value="telemarketer">Telemarketer</option>
            </select>
            <select
              className="rounded border border-navy-900/20 px-2 py-1 text-xs"
              value={complaintTarget}
              onChange={(event) =>
                setComplaintTarget(
                  event.target.value as CreateUnwantedCallIncidentInput['complaint_target'],
                )
              }
            >
              <option value="none">Draft target: none</option>
              <option value="ftc">FTC</option>
              <option value="cfpb">CFPB</option>
              <option value="state_ag">State AG</option>
              <option value="carrier">Carrier</option>
              <option value="other">Other</option>
            </select>
          </div>
          <textarea
            className="w-full rounded border border-navy-900/20 px-2 py-1 text-xs"
            rows={2}
            placeholder="Notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
          />
          <button
            type="button"
            className="rounded border border-navy-900/20 bg-white px-2 py-1 text-xs font-medium text-navy-900 disabled:opacity-50"
            disabled={createMutation.isPending}
            onClick={() => createMutation.mutate()}
          >
            {createMutation.isPending ? 'Saving…' : 'Save incident'}
          </button>
          {formError ? <p className="text-xs text-red-700">{formError}</p> : null}
        </div>
      ) : null}

      {query.isLoading ? <p className="mt-3 text-sm text-slate-500">Loading incidents…</p> : null}
      {query.isError ? (
        <p className="mt-3 text-sm text-red-700">
          {query.error instanceof ApiClientError
            ? query.error.message
            : query.error instanceof Error
              ? query.error.message
              : 'Failed to load incidents'}
        </p>
      ) : null}

      {query.data && query.data.items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No unwanted-call incidents logged yet.</p>
      ) : null}

      {query.data && query.data.items.length > 0 ? (
        <div className="mt-3 space-y-2">
          {query.data.items.map((incident) => (
            <IncidentCard
              key={incident.id}
              clientId={clientId}
              incident={incident}
              canManage={canManage}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
