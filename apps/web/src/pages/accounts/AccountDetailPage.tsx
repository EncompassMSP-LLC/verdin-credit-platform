import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { deleteAccount, getAccount } from '@verdin/api-client';
import { ACCOUNT_TYPE_LABELS, DISPUTE_STATUS_LABELS, PAYMENT_STATUS_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { AccountDeleteDialog } from '../../components/accounts/AccountDeleteDialog';
import {
  AccountStatusChip,
  BureauBadge,
  DisputeStatusChip,
  ScoreDisplay,
} from '../../components/accounts/AccountBadges';

function formatCurrency(value: string | null) {
  if (!value) return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

function formatDate(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

export function AccountDetailPage() {
  const { accountId } = useParams<{ accountId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['account', accountId],
    queryFn: () => getAccount(accountId!),
    enabled: Boolean(accountId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteAccount(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
      navigate('/accounts');
    },
  });

  if (!accountId) return null;

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading account...</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Account not found'}
            </p>
            <Link
              to="/accounts"
              className="mt-4 inline-block text-sm text-brand-600 hover:underline"
            >
              Back to accounts
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/accounts" className="text-sm text-brand-600 hover:underline">
            ← Back to accounts
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.creditor_name}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <BureauBadge bureau={data.bureau} />
            <AccountStatusChip status={data.account_status} />
            <DisputeStatusChip status={data.dispute_status} />
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/accounts/${accountId}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card title="Intelligence scores" className="lg:col-span-1">
          <div className="flex gap-8">
            <ScoreDisplay label="Risk score" score={data.risk_score} variant="risk" />
            <ScoreDisplay
              label="Readiness score"
              score={data.readiness_score}
              variant="readiness"
            />
          </div>
          {data.ai_recommended_next_action ? (
            <p className="mt-4 text-sm text-gray-600">
              <span className="font-medium text-gray-900">Next action:</span>{' '}
              {data.ai_recommended_next_action}
            </p>
          ) : null}
        </Card>

        <Card title="Financial details" className="lg:col-span-2">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-xs text-gray-500">Balance</dt>
              <dd className="text-sm font-medium text-gray-900">{formatCurrency(data.balance)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Past due</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatCurrency(data.past_due_amount)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Account type</dt>
              <dd className="text-sm text-gray-900">{ACCOUNT_TYPE_LABELS[data.account_type]}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Payment status</dt>
              <dd className="text-sm text-gray-900">
                {PAYMENT_STATUS_LABELS[data.payment_status]}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Date reported</dt>
              <dd className="text-sm text-gray-900">{formatDate(data.date_reported)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Next eligible dispute</dt>
              <dd className="text-sm text-gray-900">
                {formatDate(data.next_eligible_dispute_date)}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Dispute workflow" className="lg:col-span-3">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs text-gray-500">Dispute status</dt>
              <dd className="mt-1">
                <DisputeStatusChip status={data.dispute_status} />
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Dispute round</dt>
              <dd className="text-sm text-gray-900">{data.dispute_round}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Status label</dt>
              <dd className="text-sm text-gray-900">
                {DISPUTE_STATUS_LABELS[data.dispute_status]}
              </dd>
            </div>
          </dl>
          <div className="mt-4">
            <Link to={`/cases/${data.case_id}`} className="text-sm text-brand-600 hover:underline">
              View linked case →
            </Link>
          </div>
        </Card>
      </div>

      <AccountDeleteDialog
        creditorName={data.creditor_name}
        open={deleteOpen}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteOpen(false)}
      />
    </div>
  );
}
