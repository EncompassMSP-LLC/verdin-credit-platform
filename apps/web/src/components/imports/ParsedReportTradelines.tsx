import type { DocumentParsedCreditReport } from '@verdin/api-client';

interface ParsedTradeline {
  creditor_name: string | null;
  account_number_masked: string | null;
  balance: number | null;
  payment_status: string | null;
  open_date: string | null;
  date_reported: string | null;
}

function formatCurrency(value: number | null): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function parseTradelines(parsedReport: DocumentParsedCreditReport): ParsedTradeline[] {
  const accounts = parsedReport.parsed_report.accounts;
  if (!Array.isArray(accounts)) {
    return [];
  }

  return accounts.map((item) => {
    const row = item as Record<string, unknown>;
    return {
      creditor_name: typeof row.creditor_name === 'string' ? row.creditor_name : null,
      account_number_masked:
        typeof row.account_number_masked === 'string' ? row.account_number_masked : null,
      balance: typeof row.balance === 'number' ? row.balance : null,
      payment_status: typeof row.payment_status === 'string' ? row.payment_status : null,
      open_date: typeof row.open_date === 'string' ? row.open_date : null,
      date_reported: typeof row.date_reported === 'string' ? row.date_reported : null,
    };
  });
}

interface ParsedReportTradelinesProps {
  parsedReport: DocumentParsedCreditReport;
}

export function ParsedReportTradelines({ parsedReport }: ParsedReportTradelinesProps) {
  const tradelines = parseTradelines(parsedReport);

  if (tradelines.length === 0) {
    return <p className="text-sm text-gray-500">No tradelines were extracted from this report.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead>
          <tr className="text-left text-gray-500">
            <th className="px-3 py-2 font-medium">Creditor</th>
            <th className="px-3 py-2 font-medium">Account</th>
            <th className="px-3 py-2 font-medium">Balance</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium">Opened</th>
            <th className="px-3 py-2 font-medium">Reported</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {tradelines.map((tradeline, index) => (
            <tr key={`${tradeline.creditor_name ?? 'tradeline'}-${index}`}>
              <td className="px-3 py-2 font-medium text-gray-900">
                {tradeline.creditor_name ?? '—'}
              </td>
              <td className="px-3 py-2 text-gray-700">{tradeline.account_number_masked ?? '—'}</td>
              <td className="px-3 py-2 text-gray-700">{formatCurrency(tradeline.balance)}</td>
              <td className="px-3 py-2 text-gray-700">{tradeline.payment_status ?? '—'}</td>
              <td className="px-3 py-2 text-gray-700">{tradeline.open_date ?? '—'}</td>
              <td className="px-3 py-2 text-gray-700">{tradeline.date_reported ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
