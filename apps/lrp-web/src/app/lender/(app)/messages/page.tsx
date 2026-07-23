'use client';

import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { useLenderAuth } from '@/lib/lender/auth';
import { threads as seedThreads } from '@/lib/lender/data';
import type { LenderThread } from '@/lib/lender/types';
import { cn, formatDate } from '@/lib/utils';

export default function MessagesPage() {
  const { user, can } = useLenderAuth();
  const [threads, setThreads] = useState<LenderThread[]>(seedThreads);
  const [activeId, setActiveId] = useState(seedThreads[0]?.id ?? '');
  const [draft, setDraft] = useState('');

  const active = useMemo(
    () => threads.find((t) => t.id === activeId) ?? threads[0],
    [threads, activeId],
  );

  function sendMessage(event: React.FormEvent) {
    event.preventDefault();
    if (!can('messages.send') || !draft.trim() || !active) return;

    const message = {
      id: `tm-local-${Date.now()}`,
      from: user?.displayName ?? 'You',
      body: draft.trim(),
      at: new Date().toISOString(),
      mine: true,
    };

    setThreads((prev) =>
      prev.map((thread) =>
        thread.id === active.id
          ? {
              ...thread,
              messages: [...thread.messages, message],
              preview: message.body,
              updatedAt: message.at,
              unread: 0,
            }
          : thread,
      ),
    );
    setDraft('');
  }

  return (
    <RoleGate permission="messages.view">
      <div>
        <PageHeader
          eyebrow="Messages"
          title="Partner messaging"
          description="Coordinate with CRO advisors on borrower remediation. Messages are demo-local until platform messaging APIs connect."
        />

        <div className="grid gap-4 lg:grid-cols-[18rem_1fr]">
          <PortalCard title="Threads" className="p-0">
            <ul className="divide-y divide-navy-900/8 dark:divide-white/10">
              {threads.map((thread) => (
                <li key={thread.id}>
                  <button
                    type="button"
                    onClick={() => setActiveId(thread.id)}
                    className={cn(
                      'w-full px-4 py-3 text-left transition hover:bg-navy-900/[0.03] dark:hover:bg-white/[0.03]',
                      active?.id === thread.id && 'bg-gold-500/10',
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-navy-900 dark:text-white">
                        {thread.borrowerName}
                      </p>
                      {thread.unread > 0 ? (
                        <StatusPill tone="warn">{thread.unread}</StatusPill>
                      ) : null}
                    </div>
                    <p className="mt-0.5 text-xs font-medium text-slate-600 dark:text-white/70">
                      {thread.subject}
                    </p>
                    <p className="mt-1 line-clamp-2 text-xs text-slate-500">{thread.preview}</p>
                    <p className="mt-2 text-[0.65rem] text-slate-400">
                      {formatDate(thread.updatedAt, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          </PortalCard>

          <PortalCard
            title={active?.subject ?? 'Select a thread'}
            description={
              active ? `${active.borrowerName} · ${active.messages.length} messages` : undefined
            }
          >
            {active ? (
              <>
                <ul className="max-h-[24rem] space-y-3 overflow-y-auto pr-1">
                  {active.messages.map((message) => (
                    <li
                      key={message.id}
                      className={cn(
                        'rounded-md px-3 py-2 text-sm',
                        message.mine
                          ? 'ml-8 bg-navy-900 text-white dark:bg-gold-500/20 dark:text-white'
                          : 'mr-8 border border-navy-900/10 bg-[#F8FAFC] dark:border-white/10 dark:bg-navy-900/40',
                      )}
                    >
                      <p className="text-xs font-semibold opacity-80">{message.from}</p>
                      <p className="mt-1">{message.body}</p>
                      <p className="mt-2 text-[0.65rem] opacity-60">
                        {formatDate(message.at, {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </p>
                    </li>
                  ))}
                </ul>

                {can('messages.send') ? (
                  <form onSubmit={sendMessage} className="mt-4 flex gap-2">
                    <input
                      type="text"
                      value={draft}
                      onChange={(e) => setDraft(e.target.value)}
                      placeholder="Reply to thread…"
                      className="min-w-0 flex-1 rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                    />
                    <button
                      type="submit"
                      disabled={!draft.trim()}
                      className="rounded-md bg-navy-900 px-3 py-2 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-50 dark:bg-gold-500 dark:text-navy-900"
                    >
                      Send
                    </button>
                  </form>
                ) : (
                  <p className="mt-4 text-xs text-slate-500">
                    You have read-only access to messaging.
                  </p>
                )}
              </>
            ) : (
              <p className="text-sm text-slate-500">Select a thread to view messages.</p>
            )}
          </PortalCard>
        </div>
      </div>
    </RoleGate>
  );
}
