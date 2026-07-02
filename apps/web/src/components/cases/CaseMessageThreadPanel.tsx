import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getCaseMessageThread,
  postCaseMessageThreadReply,
  type ThreadMessage,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString();
}

interface CaseMessageThreadPanelProps {
  caseId: string;
}

export function CaseMessageThreadPanel({ caseId }: CaseMessageThreadPanelProps) {
  const queryClient = useQueryClient();
  const [body, setBody] = useState('');
  const [error, setError] = useState<string | null>(null);

  const threadQuery = useQuery({
    queryKey: ['case-message-thread', caseId],
    queryFn: () => getCaseMessageThread(caseId),
  });

  const sendMutation = useMutation({
    mutationFn: () => {
      const trimmed = body.trim();
      if (!trimmed) {
        throw new Error('Message cannot be empty');
      }
      return postCaseMessageThreadReply(caseId, { body: trimmed });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['case-message-thread', caseId] });
      setBody('');
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  const messages = threadQuery.data?.messages ?? [];
  const threadClosed = threadQuery.data?.status === 'closed';

  return (
    <Card title="Client messages" className="lg:col-span-3">
      <p className="text-sm text-gray-600">
        Secure thread with the linked portal client for this case.
      </p>

      {threadQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">Loading messages…</p>
      ) : null}

      {threadQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">
          Failed to load messages:{' '}
          {threadQuery.error instanceof Error ? threadQuery.error.message : 'Unknown error'}
        </p>
      ) : null}

      {!threadQuery.isLoading && !threadQuery.isError ? (
        <div className="mt-4 space-y-3">
          {messages.length === 0 ? (
            <p className="text-sm text-gray-500">
              No messages yet. Send the first message to the portal client below.
            </p>
          ) : (
            messages.map((message) => <StaffMessageBubble key={message.id} message={message} />)
          )}
        </div>
      ) : null}

      {threadClosed ? (
        <p className="mt-4 rounded-md bg-gray-100 px-4 py-3 text-sm text-gray-600">
          This message thread is closed.
        </p>
      ) : (
        <form
          className="mt-4 space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            setError(null);
            sendMutation.mutate();
          }}
        >
          <div>
            <label htmlFor="staff-message-body" className="block text-sm font-medium text-gray-700">
              Reply to client
            </label>
            <textarea
              id="staff-message-body"
              rows={4}
              className={inputClass}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Write your message…"
              disabled={sendMutation.isPending}
            />
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <Button type="submit" loading={sendMutation.isPending} disabled={!body.trim()}>
            Send message
          </Button>
        </form>
      )}
    </Card>
  );
}

function StaffMessageBubble({ message }: { message: ThreadMessage }) {
  const isStaff = message.sender_role === 'staff';

  return (
    <div className={`flex ${isStaff ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
          isStaff ? 'bg-brand-600 text-white' : 'border border-gray-200 bg-white text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.body}</p>
        <p className={`mt-2 text-xs ${isStaff ? 'text-brand-100' : 'text-gray-400'}`}>
          {isStaff ? 'You' : 'Client'} · {formatTimestamp(message.created_at)}
        </p>
      </div>
    </div>
  );
}
