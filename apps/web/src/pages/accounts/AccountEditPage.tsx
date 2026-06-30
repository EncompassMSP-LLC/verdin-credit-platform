import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { getAccount } from '@verdin/api-client';
import { Card } from '@verdin/ui';
import { AccountFormPage } from './AccountFormPage';

export function AccountEditPage() {
  const { accountId } = useParams<{ accountId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['account', accountId],
    queryFn: () => getAccount(accountId!),
    enabled: Boolean(accountId),
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
          <p className="py-8 text-center text-sm text-red-600">Account not found</p>
        </Card>
      </div>
    );
  }

  return (
    <AccountFormPage
      mode="edit"
      accountId={accountId}
      defaultValues={{
        case_id: data.case_id,
        bureau: data.bureau,
        creditor_name: data.creditor_name,
        original_creditor: data.original_creditor ?? '',
        account_number_masked: data.account_number_masked ?? '',
        account_type: data.account_type,
        account_status: data.account_status,
        payment_status: data.payment_status,
        balance: data.balance ?? '',
        past_due_amount: data.past_due_amount ?? '',
        remarks: data.remarks ?? '',
      }}
    />
  );
}
