import { Link, useSearchParams } from 'react-router-dom';
import { Button, Card } from '@verdin/ui';
import { featureFlags } from '../../lib/feature-flags';

interface GuideStep {
  title: string;
  summary: string;
  actions: Array<{ label: string; to: string }>;
}

function GuideStepCard({ step, number }: { step: GuideStep; number: number }) {
  return (
    <Card>
      <div className="flex gap-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-800">
          {number}
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-semibold text-gray-900">{step.title}</h2>
          <p className="mt-2 text-sm text-gray-600">{step.summary}</p>
          {step.actions.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {step.actions.map((action) => (
                <Link key={action.to} to={action.to}>
                  <Button size="sm" variant="secondary">
                    {action.label}
                  </Button>
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </Card>
  );
}

export function DisputeWorkflowGuidePage() {
  const [searchParams] = useSearchParams();
  const caseId = searchParams.get('case_id');
  const casePath = caseId ? `/cases/${caseId}` : '/cases';
  const importPath = caseId ? `/imports/credit-report?case_id=${caseId}` : '/imports/credit-report';
  const accountsPath = caseId ? `/cases/${caseId}/accounts` : '/accounts';

  const steps: GuideStep[] = [
    {
      title: 'Open or create a case',
      summary:
        'Confirm the client name and email on the case. Every dispute letter uses the client name from the case record.',
      actions: caseId
        ? [{ label: 'Back to this case', to: casePath }]
        : [{ label: 'Go to cases', to: '/cases' }],
    },
    {
      title: 'Import bureau credit reports',
      summary:
        'Upload Experian, Equifax, and TransUnion PDFs on the same case. Wait for parsing to finish — each document should show tradelines under Parsed credit report. You need at least two bureaus for cross-bureau comparison.',
      actions: featureFlags.enableImports
        ? [{ label: 'Import credit report', to: importPath }]
        : [],
    },
    {
      title: 'Review cross-bureau discrepancies',
      summary:
        'On the case page, compare tradelines across bureaus. Review actionable rows (missing bureau, balance mismatch, status mismatch) before preparing disputes. Creditor name differences can create false “missing” flags — always review manually.',
      actions: caseId
        ? [{ label: 'Open case discrepancies', to: `${casePath}#cross-bureau-discrepancies` }]
        : [],
    },
    {
      title: 'Prepare accounts and letter drafts',
      summary:
        'Click Prepare all disputes for bulk setup, or Create account & letter per row. This creates one credit account and one dispute letter draft per tradeline.',
      actions: caseId
        ? [
            { label: 'View case accounts', to: accountsPath },
            { label: 'Case discrepancies', to: `${casePath}#cross-bureau-discrepancies` },
          ]
        : [{ label: 'View accounts', to: '/accounts' }],
    },
    {
      title: 'Review evidence and download mail packets',
      summary:
        'Each prepared account has a complete mail packet: page 1 mailing labels (MAIL TO bureau, RETURN, CONSUMER), page 2 FCRA dispute letter with consumer and return addresses, page 3 mailing checklist. Use Download mail packet on an account, or Download all mail packets on the case for a ZIP of every creditor.',
      actions: [
        { label: 'Open accounts', to: accountsPath },
        { label: 'Case discrepancies', to: `${casePath}#cross-bureau-discrepancies` },
      ],
    },
    {
      title: 'Assemble and mail the packet',
      summary:
        'Print the mail-ready letter and have the consumer sign. Attach a copy of government ID, proof of address, and the credit report page for that tradeline. Mail via certified mail with return receipt (tracked outside the app). Set DISPUTE_RETURN_ADDRESS_* in deployment settings for your return address on labels.',
      actions: [],
    },
    {
      title: 'Approve, mark sent, and track the response',
      summary:
        'After review: Create review task → Approve letter → Mark as sent → Mark awaiting response when the bureau should reply. Record Verified, Corrected, or Deleted when the CRA responds. Check Tasks and Dashboard for overdue investigations.',
      actions: [
        { label: 'Open tasks', to: '/tasks' },
        { label: 'Dashboard', to: '/' },
      ],
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        {caseId ? (
          <Link to={casePath} className="text-sm text-brand-600 hover:underline">
            ← Back to case
          </Link>
        ) : (
          <Link to="/cases" className="text-sm text-brand-600 hover:underline">
            ← Back to cases
          </Link>
        )}
        <h1 className="mt-2 text-2xl font-bold text-gray-900">Dispute workflow guide</h1>
        <p className="mt-1 max-w-3xl text-gray-600">
          Step-by-step instructions for importing credit reports, finding cross-bureau problems,
          preparing dispute letters, and mailing them.
        </p>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Import', detail: '2+ bureau PDFs' },
          { label: 'Compare', detail: 'Cross-bureau panel' },
          { label: 'Prepare', detail: 'Accounts + drafts' },
          { label: 'Mail', detail: 'Mail-ready PDF + labels' },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              {item.label}
            </p>
            <p className="mt-1 text-sm font-medium text-gray-900">{item.detail}</p>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <GuideStepCard key={step.title} step={step} number={index + 1} />
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Letter lifecycle">
          <p className="font-mono text-sm text-gray-700">draft → review → approved → sent</p>
          <p className="mt-3 text-sm text-gray-600">
            Void cancels an in-flight letter. Mark as sent only after the packet is actually mailed.
          </p>
        </Card>

        <Card title="CRA mailing addresses">
          <ul className="space-y-2 text-sm text-gray-700">
            <li>
              <span className="font-medium">Experian:</span> P.O. Box 4500, Allen, TX 75013
            </li>
            <li>
              <span className="font-medium">Equifax:</span> P.O. Box 740256, Atlanta, GA 30374-0256
            </li>
            <li>
              <span className="font-medium">TransUnion:</span> P.O. Box 2000, Chester, PA 19016
            </li>
          </ul>
          <p className="mt-3 text-xs text-gray-500">
            Included automatically on mail-ready letter and label exports.
          </p>
        </Card>

        <Card title="Troubleshooting" className="lg:col-span-2">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="font-medium text-gray-900">No cross-bureau panel</dt>
              <dd className="text-gray-600">
                Upload at least two bureau reports on the same case.
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900">Prepare all disputes failed</dt>
              <dd className="text-gray-600">
                Hard-refresh the page and check for a red error message on the panel.
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900">Return address placeholder on labels</dt>
              <dd className="text-gray-600">
                Set DISPUTE_RETURN_ADDRESS_LINE1 (and LINE2/LINE3) in .env.production, then rebuild
                the API.
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900">Furnisher address not filled in</dt>
              <dd className="text-gray-600">
                Look up the creditor dispute address — the system cannot guess furnisher addresses.
              </dd>
            </div>
          </dl>
        </Card>
      </div>
    </div>
  );
}
