import type {
  AccountBureau,
  AccountStatus,
  AccountType,
  DisputeStatus,
  PaymentStatus,
} from '@verdin/shared';
import {
  ACCOUNT_BUREAUS,
  ACCOUNT_STATUSES,
  ACCOUNT_STATUS_LABELS,
  ACCOUNT_TYPES,
  ACCOUNT_TYPE_LABELS,
  BUREAU_LABELS,
  DISPUTE_STATUSES,
  DISPUTE_STATUS_LABELS,
  PAYMENT_STATUSES,
  PAYMENT_STATUS_LABELS,
} from '@verdin/shared';

export interface AccountFiltersValue {
  search: string;
  bureau: AccountBureau | '';
  account_type: AccountType | '';
  account_status: AccountStatus | '';
  payment_status: PaymentStatus | '';
  dispute_status: DisputeStatus | '';
  dispute_ready: boolean;
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

interface AccountFiltersProps {
  value: AccountFiltersValue;
  onChange: (value: AccountFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function AccountFilters({ value, onChange }: AccountFiltersProps) {
  const update = (patch: Partial<AccountFiltersValue>) => onChange({ ...value, ...patch });

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8">
      <div className="xl:col-span-2">
        <label htmlFor="account-search" className="mb-1 block text-sm font-medium text-gray-700">
          Search
        </label>
        <input
          id="account-search"
          type="search"
          placeholder="Creditor, account number..."
          className={inputClass}
          value={value.search}
          onChange={(e) => update({ search: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="account-bureau" className="mb-1 block text-sm font-medium text-gray-700">
          Bureau
        </label>
        <select
          id="account-bureau"
          className={inputClass}
          value={value.bureau}
          onChange={(e) => update({ bureau: e.target.value as AccountBureau | '' })}
        >
          <option value="">All bureaus</option>
          {ACCOUNT_BUREAUS.map((bureau) => (
            <option key={bureau} value={bureau}>
              {BUREAU_LABELS[bureau]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="account-type" className="mb-1 block text-sm font-medium text-gray-700">
          Type
        </label>
        <select
          id="account-type"
          className={inputClass}
          value={value.account_type}
          onChange={(e) => update({ account_type: e.target.value as AccountType | '' })}
        >
          <option value="">All types</option>
          {ACCOUNT_TYPES.map((type) => (
            <option key={type} value={type}>
              {ACCOUNT_TYPE_LABELS[type]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="account-status" className="mb-1 block text-sm font-medium text-gray-700">
          Status
        </label>
        <select
          id="account-status"
          className={inputClass}
          value={value.account_status}
          onChange={(e) => update({ account_status: e.target.value as AccountStatus | '' })}
        >
          <option value="">All statuses</option>
          {ACCOUNT_STATUSES.map((status) => (
            <option key={status} value={status}>
              {ACCOUNT_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="payment-status" className="mb-1 block text-sm font-medium text-gray-700">
          Payment
        </label>
        <select
          id="payment-status"
          className={inputClass}
          value={value.payment_status}
          onChange={(e) => update({ payment_status: e.target.value as PaymentStatus | '' })}
        >
          <option value="">All payment</option>
          {PAYMENT_STATUSES.map((status) => (
            <option key={status} value={status}>
              {PAYMENT_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="dispute-status" className="mb-1 block text-sm font-medium text-gray-700">
          Dispute
        </label>
        <select
          id="dispute-status"
          className={inputClass}
          value={value.dispute_status}
          onChange={(e) => update({ dispute_status: e.target.value as DisputeStatus | '' })}
        >
          <option value="">All dispute</option>
          {DISPUTE_STATUSES.map((status) => (
            <option key={status} value={status}>
              {DISPUTE_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="account-sort" className="mb-1 block text-sm font-medium text-gray-700">
          Sort
        </label>
        <select
          id="account-sort"
          className={inputClass}
          value={`${value.sort_by}:${value.sort_order}`}
          onChange={(e) => {
            const [sort_by, sort_order] = e.target.value.split(':');
            update({ sort_by, sort_order: sort_order as 'asc' | 'desc' });
          }}
        >
          <option value="created_at:desc">Newest first</option>
          <option value="creditor_name:asc">Creditor A–Z</option>
          <option value="bureau:asc">Bureau</option>
          <option value="account_type:asc">Type</option>
          <option value="account_status:asc">Status</option>
          <option value="dispute_status:asc">Dispute status</option>
          <option value="balance:desc">Highest balance</option>
          <option value="risk_score:desc">Highest risk</option>
          <option value="readiness_score:desc">Highest readiness</option>
          <option value="date_reported:desc">Recently reported</option>
        </select>
      </div>
      <div className="flex items-end">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={value.dispute_ready}
            onChange={(e) => update({ dispute_ready: e.target.checked })}
          />
          Dispute ready only
        </label>
      </div>
    </div>
  );
}
