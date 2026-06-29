import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { createAccount, listCases, updateAccount } from '@verdin/api-client';
import { createAccountSchema, type CreateAccountInput } from '@verdin/validation';
import {
  ACCOUNT_BUREAUS,
  ACCOUNT_STATUSES,
  ACCOUNT_STATUS_LABELS,
  ACCOUNT_TYPES,
  ACCOUNT_TYPE_LABELS,
  BUREAU_LABELS,
  PAYMENT_STATUSES,
  PAYMENT_STATUS_LABELS,
} from '@verdin/shared';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface AccountFormPageProps {
  mode: 'create' | 'edit';
  accountId?: string;
  defaultValues?: CreateAccountInput;
}

export function AccountFormPage({ mode, accountId, defaultValues }: AccountFormPageProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  const casesQuery = useQuery({
    queryKey: ['cases-for-account-form'],
    queryFn: () => listCases({ page_size: 100 }),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateAccountInput>({
    resolver: zodResolver(createAccountSchema),
    defaultValues: defaultValues ?? {
      case_id: searchParams.get('case_id') ?? '',
      bureau: 'unknown',
      creditor_name: '',
      account_type: 'other',
      account_status: 'unknown',
      payment_status: 'unknown',
      account_number_masked: '',
      balance: '',
      past_due_amount: '',
      remarks: '',
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: CreateAccountInput) => {
      const payload = {
        ...values,
        original_creditor: values.original_creditor || null,
        account_number_masked: values.account_number_masked || null,
        balance: values.balance || null,
        past_due_amount: values.past_due_amount || null,
        remarks: values.remarks || null,
      };
      if (mode === 'create') {
        return createAccount(payload);
      }
      if (!accountId) throw new Error('Account ID is required');
      return updateAccount(accountId, {
        bureau: payload.bureau,
        creditor_name: payload.creditor_name,
        original_creditor: payload.original_creditor,
        account_number_masked: payload.account_number_masked,
        account_type: payload.account_type,
        account_status: payload.account_status,
        payment_status: payload.payment_status,
        balance: payload.balance,
        past_due_amount: payload.past_due_amount,
        remarks: payload.remarks,
      });
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
      queryClient.invalidateQueries({ queryKey: ['account', result.id] });
      navigate(`/accounts/${result.id}`);
    },
    onError: (err: Error) => setError(err.message),
  });

  const onSubmit = handleSubmit((values) => {
    setError(null);
    mutation.mutate(values);
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          to={accountId ? `/accounts/${accountId}` : '/accounts'}
          className="text-sm text-brand-600 hover:underline"
        >
          ← Back
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">
          {mode === 'create' ? 'Create account' : 'Edit account'}
        </h1>
      </div>

      <Card className="max-w-3xl">
        <form onSubmit={onSubmit} className="space-y-4">
          {mode === 'create' ? (
            <div>
              <label htmlFor="case_id" className="block text-sm font-medium text-gray-700">
                Case
              </label>
              <select id="case_id" className={inputClass} {...register('case_id')}>
                <option value="">Select a case</option>
                {casesQuery.data?.items.map((caseItem) => (
                  <option key={caseItem.id} value={caseItem.id}>
                    {caseItem.title} ({caseItem.client_name})
                  </option>
                ))}
              </select>
              {errors.case_id ? (
                <p className="mt-1 text-sm text-red-600">{errors.case_id.message}</p>
              ) : null}
            </div>
          ) : null}

          <div>
            <label htmlFor="creditor_name" className="block text-sm font-medium text-gray-700">
              Creditor name
            </label>
            <input id="creditor_name" className={inputClass} {...register('creditor_name')} />
            {errors.creditor_name ? (
              <p className="mt-1 text-sm text-red-600">{errors.creditor_name.message}</p>
            ) : null}
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label htmlFor="bureau" className="block text-sm font-medium text-gray-700">
                Bureau
              </label>
              <select id="bureau" className={inputClass} {...register('bureau')}>
                {ACCOUNT_BUREAUS.map((bureau) => (
                  <option key={bureau} value={bureau}>
                    {BUREAU_LABELS[bureau]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                htmlFor="account_number_masked"
                className="block text-sm font-medium text-gray-700"
              >
                Account number (masked)
              </label>
              <input
                id="account_number_masked"
                className={inputClass}
                placeholder="****1234"
                {...register('account_number_masked')}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label htmlFor="account_type" className="block text-sm font-medium text-gray-700">
                Account type
              </label>
              <select id="account_type" className={inputClass} {...register('account_type')}>
                {ACCOUNT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {ACCOUNT_TYPE_LABELS[type]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="account_status" className="block text-sm font-medium text-gray-700">
                Account status
              </label>
              <select id="account_status" className={inputClass} {...register('account_status')}>
                {ACCOUNT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {ACCOUNT_STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="payment_status" className="block text-sm font-medium text-gray-700">
                Payment status
              </label>
              <select id="payment_status" className={inputClass} {...register('payment_status')}>
                {PAYMENT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {PAYMENT_STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label htmlFor="balance" className="block text-sm font-medium text-gray-700">
                Balance
              </label>
              <input id="balance" className={inputClass} {...register('balance')} />
            </div>
            <div>
              <label htmlFor="past_due_amount" className="block text-sm font-medium text-gray-700">
                Past due amount
              </label>
              <input id="past_due_amount" className={inputClass} {...register('past_due_amount')} />
            </div>
          </div>

          <div>
            <label htmlFor="remarks" className="block text-sm font-medium text-gray-700">
              Remarks
            </label>
            <textarea id="remarks" rows={3} className={inputClass} {...register('remarks')} />
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <div className="flex gap-2 pt-2">
            <Button type="submit" loading={isSubmitting || mutation.isPending}>
              {mode === 'create' ? 'Create account' : 'Save changes'}
            </Button>
            <Link to={accountId ? `/accounts/${accountId}` : '/accounts'}>
              <Button type="button" variant="secondary">
                Cancel
              </Button>
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}
