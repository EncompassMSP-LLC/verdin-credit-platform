'use client';

import {
  ApiClientError,
  advanceCaseLetterDraft,
  createCaseLetterDraft,
  getCaseLetterDraft,
  listCaseLetterDrafts,
  type LetterDraft,
  type LetterTemplateKind,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { useCrmAuth } from '@/lib/crm/auth';

type Props = {
  caseId: string | undefined;
};

export function CrmLetterDraftBuilderPanel({ caseId }: Props) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [templateKind, setTemplateKind] = useState<LetterTemplateKind>('bureau_dispute');
  const [error, setError] = useState<string | null>(null);

  const listQuery = useQuery({
    queryKey: ['crm', 'case-letter-drafts', caseId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(caseId),
    queryFn: () => listCaseLetterDrafts(caseId!),
    retry: false,
  });

  const detailQuery = useQuery({
    queryKey: ['crm', 'case-letter-draft', caseId, selectedId],
    enabled: Boolean(caseId && selectedId),
    queryFn: () => getCaseLetterDraft(caseId!, selectedId!),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createCaseLetterDraft(caseId!, {
        template_kind: templateKind,
      }),
    onSuccess: (draft) => {
      setSelectedId(draft.id);
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ['crm', 'case-letter-drafts', caseId] });
    },
    onError: (err: Error) => setError(err.message),
  });

  const advanceMutation = useMutation({
    mutationFn: (draft: LetterDraft) => advanceCaseLetterDraft(caseId!, draft.id, 'staff_review'),
    onSuccess: (draft) => {
      setSelectedId(draft.id);
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ['crm', 'case-letter-drafts', caseId] });
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'case-letter-draft', caseId, draft.id],
      });
    },
    onError: (err: Error) => setError(err.message),
  });

  if (!caseId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Letter drafts</h2>
        <p className="mt-2 text-sm text-slate-500">
          Link a case to generate staff-gated letter drafts.
        </p>
      </div>
    );
  }

  if (authMode !== 'platform') {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Letter drafts</h2>
        <p className="mt-2 text-sm text-slate-500">
          Letter drafts require platform authentication (demo mode unavailable).
        </p>
      </div>
    );
  }

  const draft = detailQuery.data;
  const templates = listQuery.data?.templates ?? [];

  return (
    <div id="letter-draft-builder" className="rounded-md border border-navy-900/10 bg-white p-4">
      <h2 className="text-sm font-semibold">Intelligent letter drafts</h2>
      <p className="mt-2 text-sm text-slate-500">
        Staff-gated drafts with validation. Never auto-mailed or bureau-submitted.
      </p>

      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="text-xs text-slate-600">
          Template
          <select
            className="mt-1 block rounded border border-navy-900/15 px-2 py-1.5 text-sm"
            value={templateKind}
            onChange={(e) => setTemplateKind(e.target.value as LetterTemplateKind)}
          >
            {templates.length > 0 ? (
              templates.map((t) => (
                <option key={t.kind} value={t.kind}>
                  {t.title}
                </option>
              ))
            ) : (
              <option value="bureau_dispute">Credit bureau dispute</option>
            )}
          </select>
        </label>
        <button
          type="button"
          className="rounded bg-navy-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          disabled={createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          {createMutation.isPending ? 'Generating…' : 'Generate draft'}
        </button>
      </div>

      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

      {listQuery.isError ? (
        <p className="mt-2 text-sm text-red-700">
          {listQuery.error instanceof ApiClientError
            ? listQuery.error.message
            : 'Failed to load drafts'}
        </p>
      ) : null}

      {listQuery.data && listQuery.data.items.length > 0 ? (
        <ul className="mt-3 space-y-1">
          {listQuery.data.items.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className="w-full rounded border border-navy-900/10 px-2 py-1.5 text-left text-sm hover:bg-slate-50"
                onClick={() => setSelectedId(item.id)}
              >
                {item.template_kind.replace(/_/g, ' ')} · {item.workflow_status.replace(/_/g, ' ')}
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {draft ? (
        <div className="mt-3 space-y-2 rounded border border-navy-900/10 bg-slate-50 p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-medium text-navy-900">
              {draft.template_title ?? draft.template_kind} · v{draft.version}
            </p>
            {draft.workflow_status === 'ai_draft_created' ? (
              <button
                type="button"
                className="rounded border border-navy-900/20 px-2 py-1 text-xs"
                disabled={advanceMutation.isPending}
                onClick={() => advanceMutation.mutate(draft)}
              >
                Send to staff review
              </button>
            ) : null}
          </div>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap text-xs text-slate-700">
            {draft.full_text}
          </pre>
          <p className="text-xs text-slate-500">{draft.disclaimer}</p>
        </div>
      ) : null}
    </div>
  );
}
