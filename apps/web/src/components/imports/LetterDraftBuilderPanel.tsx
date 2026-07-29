import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  advanceCaseLetterDraft,
  createCaseLetterDraft,
  getCaseLetterDraft,
  listCaseLetterDrafts,
  type LetterDraft,
  type LetterTemplateKind,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';

const DEFAULT_TEMPLATE: LetterTemplateKind = 'bureau_dispute';

export function CaseLetterDraftBuilderPanel({
  caseId,
  className,
  id,
  initialIssueSourceId,
}: {
  caseId: string;
  className?: string;
  id?: string;
  initialIssueSourceId?: string | null;
}) {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [templateKind, setTemplateKind] = useState<LetterTemplateKind>(DEFAULT_TEMPLATE);
  const [issueSourceId, setIssueSourceId] = useState(initialIssueSourceId ?? '');
  const [error, setError] = useState<string | null>(null);

  const listQuery = useQuery({
    queryKey: ['case-letter-drafts', caseId],
    queryFn: () => listCaseLetterDrafts(caseId),
    retry: false,
  });

  const detailQuery = useQuery({
    queryKey: ['case-letter-draft', caseId, selectedId],
    queryFn: () => getCaseLetterDraft(caseId, selectedId!),
    enabled: Boolean(selectedId),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createCaseLetterDraft(caseId, {
        template_kind: templateKind,
        issue_source_id: issueSourceId.trim() || null,
      }),
    onSuccess: (draft) => {
      setSelectedId(draft.id);
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ['case-letter-drafts', caseId] });
    },
    onError: (err: Error) => setError(err.message),
  });

  const advanceMutation = useMutation({
    mutationFn: (draft: LetterDraft) => advanceCaseLetterDraft(caseId, draft.id, 'staff_review'),
    onSuccess: (draft) => {
      setSelectedId(draft.id);
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ['case-letter-drafts', caseId] });
      void queryClient.invalidateQueries({ queryKey: ['case-letter-draft', caseId, draft.id] });
    },
    onError: (err: Error) => setError(err.message),
  });

  const draft = detailQuery.data;
  const templates = listQuery.data?.templates ?? [];

  return (
    <div id={id} className={className}>
      <Card title="Intelligent letter drafts">
        <p className="text-sm text-gray-500">
          Staff-gated letter drafts with section editing and validation. Never auto-mailed or
          bureau-submitted. No score-increase promises.
        </p>

        <div className="mt-4 flex flex-wrap items-end gap-3">
          <label className="text-sm text-gray-700">
            Template
            <select
              className="mt-1 block rounded-md border border-gray-300 px-2 py-1.5 text-sm"
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
                <option value={DEFAULT_TEMPLATE}>Credit bureau dispute</option>
              )}
            </select>
          </label>
          <label className="text-sm text-gray-700">
            Issue source (optional)
            <input
              className="mt-1 block w-56 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              value={issueSourceId}
              onChange={(e) => setIssueSourceId(e.target.value)}
              placeholder="From issue card"
            />
          </label>
          <Button
            type="button"
            onClick={() => createMutation.mutate()}
            loading={createMutation.isPending}
            disabled={createMutation.isPending}
          >
            Generate draft
          </Button>
        </div>

        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}

        {listQuery.isLoading ? <p className="mt-3 text-sm text-gray-500">Loading drafts…</p> : null}

        {listQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {listQuery.error instanceof ApiClientError
              ? listQuery.error.message
              : 'Failed to load letter drafts'}
          </p>
        ) : null}

        {listQuery.data && listQuery.data.items.length > 0 ? (
          <ul className="mt-4 space-y-2">
            {listQuery.data.items.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className="flex w-full flex-wrap items-center justify-between gap-2 rounded-md border border-gray-200 px-3 py-2 text-left text-sm hover:bg-gray-50"
                  onClick={() => setSelectedId(item.id)}
                >
                  <span>
                    {item.template_kind.replace(/_/g, ' ')} · v{item.version}
                    {item.issue_source_id ? ` · issue ${item.issue_source_id}` : ''}
                  </span>
                  <span className="flex gap-1">
                    <Badge variant={item.validation_ok ? 'info' : 'warning'}>
                      {item.validation_ok ? 'validation ok' : 'needs review'}
                    </Badge>
                    <Badge variant="default">{item.workflow_status.replace(/_/g, ' ')}</Badge>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        ) : null}

        {draft ? (
          <div className="mt-4 space-y-3 rounded-md border border-gray-200 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {draft.template_title ?? draft.template_kind}
                </p>
                <p className="text-xs text-gray-500">
                  {draft.workflow_status.replace(/_/g, ' ')} · version {draft.version}
                </p>
              </div>
              {draft.workflow_status === 'ai_draft_created' ? (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => advanceMutation.mutate(draft)}
                  loading={advanceMutation.isPending}
                >
                  Send to staff review
                </Button>
              ) : null}
            </div>

            {draft.claim_warnings.length > 0 ? (
              <ul className="list-disc pl-5 text-xs text-amber-800">
                {draft.claim_warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            ) : null}

            {draft.validation.checklist ? (
              <ul className="space-y-1 text-xs text-gray-600">
                {draft.validation.checklist.map((item) => (
                  <li key={item.id}>
                    {item.passed ? '✓' : '✗'} {item.label}
                  </li>
                ))}
              </ul>
            ) : null}

            <div className="space-y-2">
              {draft.sections.map((section) => (
                <div key={section.key} className="rounded bg-gray-50 px-3 py-2">
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                    {section.heading} · {section.fact_classification.replace(/_/g, ' ')}
                  </p>
                  <p className="mt-1 whitespace-pre-wrap text-sm text-gray-800">{section.body}</p>
                </div>
              ))}
            </div>

            <p className="text-xs text-gray-500">{draft.disclaimer}</p>
            <p className="text-xs text-gray-500">
              Auto-transmit: {String(draft.send_guardrails.auto_transmit ?? false)} · Transmission
              blocked: {String(draft.send_guardrails.transmission_blocked ?? true)}
            </p>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
