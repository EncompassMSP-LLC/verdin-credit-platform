'use client';

import {
  ApiClientError,
  askFaqKb,
  listFaqKbConversations,
  submitFaqKbFeedback,
  type FaqKbAskResponse,
  type FaqKbAudience,
  type FaqKbConversationTurn,
  type FaqKbFeedbackRating,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';

export default function CrmFaqAssistantPage() {
  const { authMode, can } = useCrmAuth();
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState('');
  const [audience, setAudience] = useState<FaqKbAudience>('staff');
  const [latest, setLatest] = useState<FaqKbAskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const historyQuery = useQuery({
    queryKey: ['crm', 'faq-kb-conversations'],
    enabled: authMode === 'platform',
    queryFn: () => listFaqKbConversations(20),
    retry: false,
  });

  const askMutation = useMutation({
    mutationFn: () => askFaqKb({ question, audience }),
    onSuccess: async (data) => {
      setLatest(data);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['crm', 'faq-kb-conversations'] });
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : 'Ask failed');
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: (input: { turnId: string; rating: FaqKbFeedbackRating }) =>
      submitFaqKbFeedback(input.turnId, { rating: input.rating }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['crm', 'faq-kb-conversations'] });
    },
  });

  if (authMode !== 'platform') {
    return (
      <RoleGate
        permission="dashboard.view"
        fallback={<p className="text-sm text-slate-500">No access.</p>}
      >
        <PageHeader
          eyebrow="Assistant"
          title="FAQ knowledge-base assistant"
          description="Platform authentication required for org-isolated retrieval and audit."
        />
        <p className="text-sm text-slate-500">
          Demo mode cannot call the approved KB retrieval API.
        </p>
      </RoleGate>
    );
  }

  return (
    <RoleGate
      permission="dashboard.view"
      fallback={<p className="text-sm text-slate-500">No access.</p>}
    >
      <PageHeader
        eyebrow="Assistant"
        title="FAQ knowledge-base assistant"
        description="Retrieval only from approved LRP articles. Citations required. No legal advice, score promises, or auto-filing."
      />

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-md border border-navy-900/10 bg-white p-4">
          <label className="block text-sm font-medium text-navy-900">
            Audience
            <select
              className="mt-1 w-full max-w-xs rounded-md border border-navy-900/20 px-2 py-1.5 text-sm"
              value={audience}
              onChange={(e) => setAudience(e.target.value as FaqKbAudience)}
            >
              <option value="staff">Staff</option>
              <option value="borrower">Borrower</option>
              <option value="lender">Lender</option>
              <option value="realtor">Realtor</option>
            </select>
          </label>
          <label className="mt-4 block text-sm font-medium text-navy-900">
            Question
            <textarea
              className="mt-1 min-h-28 w-full rounded-md border border-navy-900/20 px-3 py-2 text-sm"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about readiness, disputes, partners, privacy, or pricing…"
            />
          </label>
          <button
            type="button"
            className="mt-3 inline-flex items-center justify-center rounded-md bg-navy-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
            disabled={!question.trim() || askMutation.isPending}
            onClick={() => askMutation.mutate()}
          >
            {askMutation.isPending ? 'Retrieving…' : 'Ask approved KB'}
          </button>
          {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

          {latest ? (
            <AnswerCard
              answer={latest}
              canFeedback={can('borrowers.manage')}
              onFeedback={(rating) => feedbackMutation.mutate({ turnId: latest.turn_id, rating })}
            />
          ) : null}
        </section>

        <section className="rounded-md border border-navy-900/10 bg-white p-4">
          <h2 className="text-sm font-semibold text-navy-900">Recent org turns</h2>
          {historyQuery.isLoading ? <p className="mt-2 text-sm text-slate-500">Loading…</p> : null}
          {historyQuery.isError ? (
            <p className="mt-2 text-sm text-red-700">
              {historyQuery.error instanceof ApiClientError
                ? historyQuery.error.message
                : 'Failed to load history'}
            </p>
          ) : null}
          <ul className="mt-3 space-y-3">
            {(historyQuery.data ?? []).map((turn) => (
              <HistoryItem key={turn.id} turn={turn} />
            ))}
          </ul>
        </section>
      </div>
    </RoleGate>
  );
}

function AnswerCard({
  answer,
  canFeedback,
  onFeedback,
}: {
  answer: FaqKbAskResponse;
  canFeedback: boolean;
  onFeedback: (rating: FaqKbFeedbackRating) => void;
}) {
  return (
    <article className="mt-4 rounded-md border border-navy-900/10 bg-slate-50 p-3">
      <p className="text-xs text-slate-500">
        {answer.grounded ? 'Grounded' : 'Not grounded'}
        {answer.refused ? ` · refused (${answer.refusal_reason})` : ''}
      </p>
      <p className="mt-2 text-sm text-slate-800 whitespace-pre-wrap">{answer.answer}</p>
      <p className="mt-2 text-xs text-amber-900">{answer.disclaimer}</p>
      {answer.citations.length > 0 ? (
        <div className="mt-3 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Citations</p>
          {answer.citations.map((cite) => (
            <div
              key={cite.article_id}
              className="rounded border border-navy-900/10 bg-white px-2 py-1.5 text-xs text-slate-600"
            >
              <p className="font-medium text-navy-900">{cite.title}</p>
              <p className="mt-0.5">{cite.source_path}</p>
              <p className="mt-1">{cite.excerpt}</p>
            </div>
          ))}
        </div>
      ) : null}
      {canFeedback ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {(['accurate', 'inaccurate', 'incomplete'] as const).map((rating) => (
            <button
              key={rating}
              type="button"
              className="rounded-md border border-navy-900/20 px-2 py-1 text-xs text-navy-900"
              onClick={() => onFeedback(rating)}
            >
              Mark {rating}
            </button>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function HistoryItem({ turn }: { turn: FaqKbConversationTurn }) {
  return (
    <li className="rounded-md border border-navy-900/10 px-3 py-2">
      <p className="text-xs text-slate-500">
        {turn.audience} · {new Date(turn.created_at).toLocaleString()}
        {turn.feedback_rating ? ` · feedback ${turn.feedback_rating}` : ''}
      </p>
      <p className="mt-1 text-sm font-medium text-navy-900">{turn.question}</p>
      <p className="mt-1 line-clamp-3 text-xs text-slate-600">{turn.answer}</p>
    </li>
  );
}
