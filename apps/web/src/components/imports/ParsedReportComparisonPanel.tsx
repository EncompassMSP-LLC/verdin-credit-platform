import type {
  DocumentParsedCreditReportComparison,
  ParsedReportAccountChange,
} from '@verdin/api-client';
import { Badge } from '@verdin/ui';
import { Link } from 'react-router-dom';

export interface ParsedReportTradelineHighlight {
  creditorName?: string | null;
  accountNumberMasked?: string | null;
}

function formatCurrency(value: number | null): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function changeVariant(
  changeType: ParsedReportAccountChange['change_type'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (changeType === 'added') return 'success';
  if (changeType === 'removed') return 'danger';
  if (changeType === 'changed') return 'warning';
  return 'default';
}

function matchesTradeline(
  change: ParsedReportAccountChange,
  highlight: ParsedReportTradelineHighlight,
): boolean {
  const creditorMatch =
    Boolean(highlight.creditorName) &&
    Boolean(change.creditor_name) &&
    change.creditor_name!.toLowerCase() === highlight.creditorName!.toLowerCase();

  const highlightDigits = highlight.accountNumberMasked?.replace(/\D/g, '') ?? '';
  const changeDigits = change.account_number_masked?.replace(/\D/g, '') ?? '';
  const accountMatch =
    highlightDigits.length >= 4 &&
    changeDigits.length >= 4 &&
    changeDigits.endsWith(highlightDigits.slice(-4));

  return creditorMatch || accountMatch;
}

export function ParsedReportComparisonPanel({
  comparison,
  highlightTradeline,
  documentLink,
  previousDocumentLink,
}: {
  comparison?: DocumentParsedCreditReportComparison;
  highlightTradeline?: ParsedReportTradelineHighlight;
  documentLink?: string;
  previousDocumentLink?: string | null;
}) {
  if (!comparison) {
    return null;
  }

  const notableChanges = comparison.account_changes.filter((change) => {
    if (change.change_type === 'unchanged') {
      return false;
    }
    if (!highlightTradeline) {
      return true;
    }
    return matchesTradeline(change, highlightTradeline);
  });

  return (
    <div className="rounded-md border border-gray-200 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Historical comparison</h4>
          <p className="mt-1 text-sm text-gray-500">
            {comparison.previous_document_id
              ? `Compared with the previous ${comparison.bureau} report for this case.`
              : `No previous ${comparison.bureau} report was found for this case.`}
          </p>
          <div className="mt-2 flex flex-wrap gap-3 text-xs">
            {documentLink ? (
              <Link to={documentLink} className="text-brand-600 hover:underline">
                View current report
              </Link>
            ) : null}
            {previousDocumentLink ? (
              <Link to={previousDocumentLink} className="text-brand-600 hover:underline">
                View previous report
              </Link>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge variant="success">{comparison.summary.added} added</Badge>
          <Badge variant="danger">{comparison.summary.removed} removed</Badge>
          <Badge variant="warning">{comparison.summary.changed} changed</Badge>
          <Badge variant="default">{comparison.summary.unchanged} unchanged</Badge>
        </div>
      </div>

      {highlightTradeline ? (
        <p className="mt-3 text-sm text-gray-600">
          Showing tradeline changes for{' '}
          <span className="font-medium">{highlightTradeline.creditorName ?? 'this account'}</span>
          {highlightTradeline.accountNumberMasked
            ? ` (${highlightTradeline.accountNumberMasked})`
            : null}
          .
        </p>
      ) : null}

      {notableChanges.length > 0 ? (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Change</th>
                <th className="px-3 py-2 font-medium">Creditor</th>
                <th className="px-3 py-2 font-medium">Account</th>
                <th className="px-3 py-2 font-medium">Previous</th>
                <th className="px-3 py-2 font-medium">Current</th>
                <th className="px-3 py-2 font-medium">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {notableChanges.map((change) => (
                <tr key={change.match_key}>
                  <td className="px-3 py-2">
                    <Badge variant={changeVariant(change.change_type)}>{change.change_type}</Badge>
                  </td>
                  <td className="px-3 py-2 font-medium text-gray-900">
                    {change.creditor_name ?? '—'}
                  </td>
                  <td className="px-3 py-2 text-gray-700">{change.account_number_masked ?? '—'}</td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.previous_balance)}
                  </td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.current_balance)}
                  </td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.balance_delta)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-3 text-sm text-gray-500">
          {highlightTradeline
            ? 'No balance or payment status changes were detected for this tradeline.'
            : 'No balance or payment status changes were detected.'}
        </p>
      )}
    </div>
  );
}
