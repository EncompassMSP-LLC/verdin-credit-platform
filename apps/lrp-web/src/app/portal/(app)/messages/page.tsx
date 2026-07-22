'use client';

import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { sendPortalCaseMessage } from '@verdin/api-client';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { usePrimaryCase, usePortalMessages } from '@/lib/platform/hooks';
import { cn, formatDate } from '@/lib/utils';

export default function MessagesPage() {
  const queryClient = useQueryClient();
  const { primary } = usePrimaryCase();
  const messagesQuery = usePortalMessages(primary?.id);
  const [draft, setDraft] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  async function send() {
    if (!draft.trim() || !primary) return;
    setSending(true);
    setError(null);
    try {
      await sendPortalCaseMessage(primary.id, { body: draft.trim() });
      setDraft('');
      await queryClient.invalidateQueries({ queryKey: ['portal', 'messages', primary.id] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message.');
    } finally {
      setSending(false);
    }
  }

  const messages = messagesQuery.data?.messages ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Messages"
        title="Case messaging"
        description="Secure thread on your primary case—same messaging store as the staff client portal."
      />

      {!primary ? (
        <p className="rounded-brand border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
          No case available for messaging yet.
        </p>
      ) : (
        <PortalCard
          title={primary.title}
          description={`Source: /portal/cases/${primary.id}/messages`}
        >
          {error ? <p className="mb-3 text-sm text-critical">{error}</p> : null}
          <div className="flex max-h-[28rem] flex-col gap-3 overflow-y-auto">
            {messagesQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading messages…</p>
            ) : !messages.length ? (
              <p className="text-sm text-slate-500">No messages yet. Start the conversation.</p>
            ) : (
              messages.map((message) => {
                const mine = message.sender_role === 'portal_client';
                return (
                  <div
                    key={message.id}
                    className={cn(
                      'max-w-[90%] rounded-brand px-3 py-2 text-sm',
                      mine
                        ? 'ml-auto bg-navy-900 text-white dark:bg-gold-500 dark:text-navy-900'
                        : 'bg-sand-100 text-navy-900 dark:bg-navy-900/60 dark:text-white',
                    )}
                  >
                    <p className="text-[0.65rem] font-medium uppercase opacity-70">
                      {mine ? 'You' : 'Staff'}
                    </p>
                    <p className="mt-1">{message.body}</p>
                    <p className="mt-1 text-[0.65rem] opacity-70">
                      {formatDate(message.created_at, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                );
              })
            )}
          </div>
          <div className="mt-4 flex gap-2 border-t border-navy-900/8 pt-4 dark:border-white/10">
            <label htmlFor="draft" className="sr-only">
              Message
            </label>
            <input
              id="draft"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Write a message…"
              className="flex-1 rounded-brand border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  void send();
                }
              }}
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={sending || !draft.trim()}
              className="rounded-brand bg-gold-500 px-4 py-2 text-sm font-semibold text-navy-900 hover:bg-gold-400 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </PortalCard>
      )}
    </div>
  );
}
