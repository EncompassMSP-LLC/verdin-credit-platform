import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listPortalCaseMessages,
  sendPortalCaseMessage,
  type PortalThreadMessage,
} from '@verdin/api-client';
import { Button } from '@verdin/ui';
import { useTranslation } from 'react-i18next';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatTimestamp(value: string, locale: string) {
  return new Date(value).toLocaleString(locale);
}

interface PortalCaseMessagesProps {
  caseId: string;
}

export function PortalCaseMessages({ caseId }: PortalCaseMessagesProps) {
  const { t, i18n } = useTranslation('portal');
  const { t: tCommon } = useTranslation('common');
  const queryClient = useQueryClient();
  const [body, setBody] = useState('');
  const [error, setError] = useState<string | null>(null);

  const threadQuery = useQuery({
    queryKey: ['portal-case-messages', caseId],
    queryFn: () => listPortalCaseMessages(caseId),
  });

  const sendMutation = useMutation({
    mutationFn: () => {
      const trimmed = body.trim();
      if (!trimmed) {
        throw new Error(t('messages.errors.empty'));
      }
      return sendPortalCaseMessage(caseId, { body: trimmed });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-case-messages', caseId] });
      setBody('');
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  const messages = threadQuery.data?.messages ?? [];
  const threadClosed = threadQuery.data?.status === 'closed';

  return (
    <div className="mt-8 border-t border-gray-200 pt-8">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
          {t('messages.title')}
        </h2>
        <p className="mt-1 text-sm text-gray-600">{t('messages.subtitle')}</p>
      </div>

      {threadQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">{t('messages.loading')}</p>
      ) : null}

      {threadQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">
          {t('messages.loadError')}:{' '}
          {threadQuery.error instanceof Error ? threadQuery.error.message : tCommon('unknownError')}
        </p>
      ) : null}

      {!threadQuery.isLoading && !threadQuery.isError ? (
        <div className="mt-4 space-y-3">
          {messages.length === 0 ? (
            <p className="text-sm text-gray-500">{t('messages.empty')}</p>
          ) : (
            messages.map((message) => (
              <PortalMessageBubble
                key={message.id}
                message={message}
                locale={i18n.language}
                youLabel={t('messages.you')}
                caseTeamLabel={t('messages.caseTeam')}
              />
            ))
          )}
        </div>
      ) : null}

      {threadClosed ? (
        <p className="mt-4 rounded-md bg-gray-100 px-4 py-3 text-sm text-gray-600">
          {t('messages.threadClosed')}
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
            <label
              htmlFor="portal-message-body"
              className="block text-sm font-medium text-gray-700"
            >
              {t('messages.yourMessage')}
            </label>
            <textarea
              id="portal-message-body"
              rows={4}
              className={inputClass}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder={t('messages.placeholder')}
              disabled={sendMutation.isPending}
            />
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <Button type="submit" loading={sendMutation.isPending} disabled={!body.trim()}>
            {t('messages.send')}
          </Button>
        </form>
      )}
    </div>
  );
}

function PortalMessageBubble({
  message,
  locale,
  youLabel,
  caseTeamLabel,
}: {
  message: PortalThreadMessage;
  locale: string;
  youLabel: string;
  caseTeamLabel: string;
}) {
  const isClient = message.sender_role === 'portal_client';

  return (
    <div className={`flex ${isClient ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
          isClient ? 'bg-brand-600 text-white' : 'border border-gray-200 bg-white text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.body}</p>
        <p className={`mt-2 text-xs ${isClient ? 'text-brand-100' : 'text-gray-400'}`}>
          {isClient ? youLabel : caseTeamLabel} · {formatTimestamp(message.created_at, locale)}
        </p>
      </div>
    </div>
  );
}
