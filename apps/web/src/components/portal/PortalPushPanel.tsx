import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getPortalPushStatus, subscribePortalPush } from '@verdin/api-client';
import { Button } from '@verdin/ui';
import { featureFlags } from '../../lib/feature-flags';

export function PortalPushPanel() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['portal-push-status'],
    queryFn: getPortalPushStatus,
    enabled: featureFlags.enableClientPortal && featureFlags.enablePortalPush,
  });

  const subscribeMutation = useMutation({
    mutationFn: () =>
      subscribePortalPush({
        endpoint: `https://push.verdin.demo/scaffold/${crypto.randomUUID()}`,
        p256dh_key: 'scaffold-p256dh',
        auth_key: 'scaffold-auth',
        user_agent: navigator.userAgent,
      }),
    onSuccess: () => {
      setError(null);
      setSuccess('Push subscription registered for this device.');
      void queryClient.invalidateQueries({ queryKey: ['portal-push-status'] });
    },
    onError: (err: Error) => {
      setSuccess(null);
      setError(err.message);
    },
  });

  if (!featureFlags.enableClientPortal || !featureFlags.enablePortalPush) {
    return null;
  }

  if (statusQuery.isLoading) {
    return <p className="mt-6 text-sm text-gray-500">Checking push notification status…</p>;
  }

  if (statusQuery.isError || !statusQuery.data) {
    return <p className="mt-6 text-sm text-red-600">Unable to load push notification settings.</p>;
  }

  const status = statusQuery.data;

  return (
    <div className="mt-8 rounded-md border border-gray-200 bg-gray-50 p-4">
      <h2 className="text-sm font-semibold text-gray-900">Message notifications</h2>
      <p className="mt-1 text-sm text-gray-600">
        Register this browser for push alerts when your case team sends a secure message.
      </p>

      {!status.ready ? (
        <div className="mt-3 rounded-md bg-amber-50 p-3 text-sm text-amber-900">
          <p className="font-medium">Push delivery is not fully configured.</p>
          {status.blockers.length > 0 ? (
            <ul className="mt-2 list-disc pl-5">
              {status.blockers.map((blocker) => (
                <li key={blocker}>{blocker.replaceAll('_', ' ')}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      <div className="mt-3 text-sm text-gray-600">
        Active subscriptions: {status.active_subscription_count}
      </div>

      <div className="mt-4">
        <Button
          type="button"
          variant="secondary"
          loading={subscribeMutation.isPending}
          onClick={() => subscribeMutation.mutate()}
        >
          Register for notifications
        </Button>
      </div>

      {success ? <p className="mt-3 text-sm text-green-700">{success}</p> : null}
      {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}
