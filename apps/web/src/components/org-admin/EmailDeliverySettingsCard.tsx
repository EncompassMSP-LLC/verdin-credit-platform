import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  getNotificationEmailDeliveryStatus,
  listNotificationEmailDeliveries,
  sendNotificationEmail,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useState } from 'react';

import { useAuth } from '../../lib/auth';

function formatDate(value: string | null | undefined) {
  return value ? new Date(value).toLocaleString() : '—';
}

function formatError(error: unknown) {
  if (error instanceof ApiClientError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Email request failed';
}

function canSendTestEmail(role: string | undefined) {
  return role === 'admin' || role === 'owner';
}

export function EmailDeliverySettingsCard() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [actionError, setActionError] = useState<string | null>(null);
  const [lastTestResult, setLastTestResult] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['email-delivery-status'],
    queryFn: getNotificationEmailDeliveryStatus,
    retry: false,
  });

  const deliveriesQuery = useQuery({
    queryKey: ['email-delivery-logs'],
    queryFn: () => listNotificationEmailDeliveries({ page: 1, page_size: 10 }),
    enabled: statusQuery.data?.ready === true && canSendTestEmail(user?.role),
    retry: false,
  });

  const testSendMutation = useMutation({
    mutationFn: () => {
      if (!user?.id) throw new Error('Sign in to send a test email');
      return sendNotificationEmail({
        recipient_user_id: user.id,
        subject: 'Verdin email delivery test',
        body: 'This is a test message from Organization admin. If you received this in Mailpit or your inbox, email delivery is working.',
      });
    },
    onSuccess: (result) => {
      setActionError(null);
      setLastTestResult(
        result.status === 'sent'
          ? `Test email sent to ${result.recipient_email}.`
          : `Send failed: ${result.error_message ?? 'unknown error'}`,
      );
      void queryClient.invalidateQueries({ queryKey: ['email-delivery-logs'] });
    },
    onError: (error) => {
      setLastTestResult(null);
      setActionError(formatError(error));
    },
  });

  if (statusQuery.isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading email delivery settings…</p>
      </Card>
    );
  }

  if (statusQuery.isError) {
    return (
      <Card className="mb-6" title="Email delivery">
        <p className="text-sm text-gray-600">
          Could not load email delivery status. Ensure the API is running and you are signed in.
        </p>
      </Card>
    );
  }

  const status = statusQuery.data!;
  const deliveries = deliveriesQuery.data?.items ?? [];
  const showMailpitHint = status.provider === 'smtp' && status.ready;

  return (
    <Card className="mb-6" title="Email delivery">
      <p className="text-sm text-gray-600">
        Send transactional email for notifications and staff workflows. Local pilot uses Mailpit;
        production can use SMTP or SendGrid.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Badge variant={status.enabled ? 'success' : 'default'}>
          {status.enabled ? 'Feature enabled' : 'Feature disabled'}
        </Badge>
        <Badge variant={status.ready ? 'success' : 'warning'}>
          {status.ready ? 'Provider ready' : 'Setup incomplete'}
        </Badge>
        {status.provider !== 'none' ? (
          <Badge variant="default">{status.provider.toUpperCase()}</Badge>
        ) : null}
      </div>

      {status.blockers.length > 0 ? (
        <div className="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-900">
          <p className="font-medium">Configuration needed</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {status.blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
          <p className="mt-3 text-xs">
            Set variables in <code>.env.production</code>, then rebuild:{' '}
            <code>
              docker compose -f docker-compose.local-pilot.yml --env-file .env.production up -d
              --build api
            </code>
          </p>
        </div>
      ) : null}

      {status.ready ? (
        <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-gray-500">From address</dt>
            <dd className="break-all font-mono text-xs">{status.from_address ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Provider</dt>
            <dd>{status.provider}</dd>
          </div>
        </dl>
      ) : null}

      {showMailpitHint ? (
        <p className="mt-4 text-sm text-gray-600">
          Local pilot inbox:{' '}
          <a
            className="font-medium text-brand-600 hover:text-brand-700"
            href="http://localhost:8025"
            rel="noreferrer"
            target="_blank"
          >
            http://localhost:8025
          </a>{' '}
          (Mailpit)
        </p>
      ) : null}

      {actionError ? (
        <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{actionError}</p>
      ) : null}

      {lastTestResult ? (
        <p className="mt-4 rounded-md bg-green-50 p-3 text-sm text-green-800">{lastTestResult}</p>
      ) : null}

      {status.ready && canSendTestEmail(user?.role) ? (
        <div className="mt-6 flex flex-wrap gap-3">
          <Button
            loading={testSendMutation.isPending}
            onClick={() => testSendMutation.mutate()}
            variant="secondary"
          >
            Send test email to me
          </Button>
        </div>
      ) : null}

      {status.ready && !canSendTestEmail(user?.role) ? (
        <p className="mt-4 text-xs text-gray-500">
          Admin or owner role required to send test email and view delivery logs.
        </p>
      ) : null}

      {deliveriesQuery.isSuccess && deliveries.length > 0 ? (
        <div className="mt-6 border-t border-gray-200 pt-4">
          <p className="text-sm font-medium text-gray-700">Recent deliveries</p>
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-2 py-2 font-medium">When</th>
                  <th className="px-2 py-2 font-medium">To</th>
                  <th className="px-2 py-2 font-medium">Subject</th>
                  <th className="px-2 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {deliveries.map((entry) => (
                  <tr key={entry.id} className="border-b border-gray-100">
                    <td className="px-2 py-2 whitespace-nowrap">{formatDate(entry.created_at)}</td>
                    <td className="px-2 py-2 font-mono text-xs">{entry.recipient_email}</td>
                    <td className="px-2 py-2">{entry.subject}</td>
                    <td className="px-2 py-2">
                      <Badge variant={entry.status === 'sent' ? 'success' : 'warning'}>
                        {entry.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      <div className="mt-6 border-t border-gray-200 pt-4 text-xs text-gray-500">
        <p className="font-medium text-gray-700">Production checklist</p>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          <li>
            Set <code>ENABLE_EMAIL_DELIVERY=true</code> and <code>EMAIL_PROVIDER</code> (
            <code>smtp</code> or <code>sendgrid</code>).
          </li>
          <li>
            Configure <code>EMAIL_FROM_ADDRESS</code> and provider credentials (SMTP host/port or{' '}
            <code>EMAIL_SENDGRID_API_KEY</code>).
          </li>
          <li>
            Use <code>deliver_email: true</code> on notification create, or send via this panel.
          </li>
        </ol>
      </div>
    </Card>
  );
}
