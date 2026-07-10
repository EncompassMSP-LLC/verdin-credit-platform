import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  disconnectPilotBilling,
  getBillingStatus,
  getOrganizationAdminSummary,
  setupOrganizationBilling,
  subscribeOrganizationBilling,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useState } from 'react';

function formatDate(value: string | null | undefined) {
  return value ? new Date(value).toLocaleString() : '—';
}

function formatLabel(value: string) {
  return value.replaceAll('_', ' ');
}

function formatError(error: unknown) {
  if (error instanceof ApiClientError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Billing request failed';
}

function isPilotCustomer(customerId: string | null | undefined) {
  return Boolean(customerId?.startsWith('cus_pilot_'));
}

export function BillingSettingsCard() {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['billing-status'],
    queryFn: getBillingStatus,
    retry: false,
  });

  const summaryQuery = useQuery({
    queryKey: ['org-admin-summary'],
    queryFn: getOrganizationAdminSummary,
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ['billing-status'] });
    void queryClient.invalidateQueries({ queryKey: ['org-admin-summary'] });
    void queryClient.invalidateQueries({ queryKey: ['reporting-revenue'] });
  };

  const setupMutation = useMutation({
    mutationFn: setupOrganizationBilling,
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (error) => setActionError(formatError(error)),
  });

  const subscribeMutation = useMutation({
    mutationFn: () => subscribeOrganizationBilling({}),
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (error) => setActionError(formatError(error)),
  });

  const disconnectMutation = useMutation({
    mutationFn: disconnectPilotBilling,
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (error) => setActionError(formatError(error)),
  });

  if (statusQuery.isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading billing settings…</p>
      </Card>
    );
  }

  if (statusQuery.isError) {
    return (
      <Card className="mb-6" title="Stripe billing">
        <p className="text-sm text-gray-600">
          Billing is disabled. Set <code className="text-xs">ENABLE_BILLING=true</code> and Stripe
          keys in the API environment, then rebuild the pilot.
        </p>
      </Card>
    );
  }

  const status = statusQuery.data!;
  const billing = summaryQuery.data?.billing;
  const hasCustomer = Boolean(billing?.stripe_customer_id);
  const hasSubscription = Boolean(billing?.stripe_subscription_id);
  const pilotRecord = isPilotCustomer(billing?.stripe_customer_id);

  return (
    <Card className="mb-6" title="Stripe billing">
      <p className="text-sm text-gray-600">
        Connect your organization to Stripe for subscriptions and revenue reporting. Use{' '}
        <strong>test mode</strong> keys while developing locally.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Badge variant={status.ready ? 'success' : 'warning'}>
          {status.ready ? 'Stripe configured' : 'Stripe setup incomplete'}
        </Badge>
        {billing?.subscription_status ? (
          <Badge variant={billing.subscription_status === 'active' ? 'success' : 'default'}>
            {formatLabel(billing.subscription_status)}
          </Badge>
        ) : null}
        {pilotRecord ? <Badge variant="warning">Pilot placeholder data</Badge> : null}
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
            Add keys to <code>.env.production</code>, then rebuild:{' '}
            <code>
              docker compose -f docker-compose.local-pilot.yml --env-file .env.production up -d
              --build api
            </code>
          </p>
        </div>
      ) : null}

      {billing ? (
        <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-gray-500">Stripe customer</dt>
            <dd className="break-all font-mono text-xs">{billing.stripe_customer_id ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Subscription</dt>
            <dd className="break-all font-mono text-xs">{billing.stripe_subscription_id ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Price ID</dt>
            <dd className="break-all font-mono text-xs">
              {billing.price_id ?? status.default_price_id ?? '—'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Current period ends</dt>
            <dd>{formatDate(billing.current_period_end ?? null)}</dd>
          </div>
        </dl>
      ) : null}

      {actionError ? (
        <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{actionError}</p>
      ) : null}

      <div className="mt-6 flex flex-wrap gap-3">
        {pilotRecord ? (
          <Button
            variant="secondary"
            loading={disconnectMutation.isPending}
            onClick={() => disconnectMutation.mutate()}
          >
            Remove pilot billing record
          </Button>
        ) : null}
        {!hasCustomer && status.ready ? (
          <Button loading={setupMutation.isPending} onClick={() => setupMutation.mutate()}>
            Create Stripe customer
          </Button>
        ) : null}
        {hasCustomer && !hasSubscription && status.ready && !pilotRecord ? (
          <Button loading={subscribeMutation.isPending} onClick={() => subscribeMutation.mutate()}>
            Start subscription
          </Button>
        ) : null}
      </div>

      <div className="mt-6 border-t border-gray-200 pt-4 text-xs text-gray-500">
        <p className="font-medium text-gray-700">Stripe Dashboard checklist</p>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          <li>Create a recurring Price (Products → Add product) and copy the Price ID.</li>
          <li>
            Set <code>STRIPE_SECRET_KEY</code> (test), <code>STRIPE_DEFAULT_PRICE_ID</code>, and{' '}
            <code>STRIPE_WEBHOOK_SECRET</code> in <code>.env.production</code>.
          </li>
          <li>
            Forward webhooks locally:{' '}
            <code>stripe listen --forward-to localhost:8080/api/v1/billing/webhooks/stripe</code>
          </li>
          <li>Remove any pilot placeholder record, then create customer and subscription above.</li>
        </ol>
      </div>
    </Card>
  );
}
