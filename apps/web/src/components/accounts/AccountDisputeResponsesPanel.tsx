import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listAccountDisputeResponses,
  recordAccountDisputeResponse,
  type DisputeResponseMethod,
  type DisputeResponseRecordOutcome,
} from '@verdin/api-client';

const OUTCOME_OPTIONS: { value: DisputeResponseRecordOutcome; label: string }[] = [
  { value: 'deleted', label: 'Deleted' },
  { value: 'corrected', label: 'Corrected' },
  { value: 'updated', label: 'Updated' },
  { value: 'verified', label: 'Verified (unchanged)' },
  { value: 'rejected', label: 'Rejected / frivolous' },
  { value: 'no_response', label: 'No response' },
];

const METHOD_OPTIONS: { value: DisputeResponseMethod; label: string }[] = [
  { value: 'mail', label: 'Mail' },
  { value: 'portal', label: 'Portal' },
  { value: 'phone', label: 'Phone' },
  { value: 'email', label: 'Email' },
  { value: 'other', label: 'Other' },
];

const OUTCOME_LABELS: Record<DisputeResponseRecordOutcome, string> = Object.fromEntries(
  OUTCOME_OPTIONS.map((o) => [o.value, o.label]),
) as Record<DisputeResponseRecordOutcome, string>;

function formatDate(value: string | null): string {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

interface AccountDisputeResponsesPanelProps {
  accountId: string;
}

export function AccountDisputeResponsesPanel({ accountId }: AccountDisputeResponsesPanelProps) {
  const queryClient = useQueryClient();
  const [outcome, setOutcome] = useState<DisputeResponseRecordOutcome>('deleted');
  const [method, setMethod] = useState<DisputeResponseMethod>('mail');
  const [responseDate, setResponseDate] = useState('');
  const [notes, setNotes] = useState('');

  const responsesQuery = useQuery({
    queryKey: ['account-dispute-responses', accountId],
    queryFn: () => listAccountDisputeResponses(accountId),
  });

  const recordMutation = useMutation({
    mutationFn: () =>
      recordAccountDisputeResponse(accountId, {
        outcome,
        response_method: method,
        response_date: responseDate || null,
        notes: notes.trim() ? notes.trim() : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account-dispute-responses', accountId] });
      queryClient.invalidateQueries({ queryKey: ['account', accountId] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
      setNotes('');
      setResponseDate('');
    },
  });

  const responses = responsesQuery.data ?? [];

  return (
    <div className="mt-6 border-t border-gray-100 pt-4">
      <h3 className="text-sm font-semibold text-gray-900">Dispute response history</h3>
      <p className="mt-1 text-xs text-gray-500">
        Record bureau/furnisher responses as they arrive by mail or portal. Staff-entered only — the
        platform never contacts a bureau automatically.
      </p>

      <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="text-xs font-medium text-gray-700">
          Outcome
          <select
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={outcome}
            onChange={(event) => setOutcome(event.target.value as DisputeResponseRecordOutcome)}
          >
            {OUTCOME_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-medium text-gray-700">
          Received via
          <select
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={method}
            onChange={(event) => setMethod(event.target.value as DisputeResponseMethod)}
          >
            {METHOD_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-medium text-gray-700">
          Response date
          <input
            type="date"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={responseDate}
            onChange={(event) => setResponseDate(event.target.value)}
          />
        </label>
        <label className="text-xs font-medium text-gray-700 sm:col-span-2">
          Notes
          <textarea
            rows={2}
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            placeholder="Optional context for the reinvestigation record"
          />
        </label>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <button
          type="button"
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          onClick={() => recordMutation.mutate()}
          disabled={recordMutation.isPending}
        >
          {recordMutation.isPending ? 'Recording…' : 'Record response'}
        </button>
        {recordMutation.isError ? (
          <span className="text-xs text-red-600">Failed to record response.</span>
        ) : null}
      </div>

      <div className="mt-4">
        {responsesQuery.isLoading ? (
          <p className="text-xs text-gray-500">Loading response history…</p>
        ) : responses.length === 0 ? (
          <p className="text-xs text-gray-500">No dispute responses recorded yet.</p>
        ) : (
          <ul className="divide-y divide-gray-100 rounded-md border border-gray-100">
            {responses.map((response) => (
              <li key={response.id} className="px-3 py-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    {OUTCOME_LABELS[response.outcome] ?? response.outcome}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(response.response_date)} · {response.response_method}
                  </span>
                </div>
                {response.notes ? (
                  <p className="mt-1 text-xs text-gray-600">{response.notes}</p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
