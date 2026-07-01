import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { deleteCase, getCase } from '@verdin/api-client';
import { CASE_STAGE_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { CaseDeleteDialog } from '../../components/cases/CaseDeleteDialog';
import { CasePriorityBadge, CaseStatusChip } from '../../components/cases/CaseBadges';
import { CreditReportHistoryPanel } from '../../components/imports/CreditReportHistoryPanel';
import { featureFlags } from '../../lib/feature-flags';

function formatDateTime(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleString();
}

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: Boolean(caseId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteCase(caseId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      navigate('/cases');
    },
  });

  if (!caseId) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading case...</p>
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
              {error instanceof Error ? error.message : 'Case not found'}
            </p>
            <Link to="/cases" className="mt-4 inline-block text-sm text-brand-600 hover:underline">
              Back to cases
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
          <Link to="/cases" className="text-sm text-brand-600 hover:underline">
            ← Back to cases
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.title}</h1>
          {data.case_number ? <p className="text-sm text-gray-500">{data.case_number}</p> : null}
        </div>
        <div className="flex gap-2">
          <Link to={`/cases/${caseId}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2" title="Overview">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-gray-500">Client</dt>
              <dd className="font-medium">{data.client_name}</dd>
              {data.client_email ? (
                <dd className="text-sm text-gray-500">{data.client_email}</dd>
              ) : null}
            </div>
            <div>
              <dt className="text-sm text-gray-500">Stage</dt>
              <dd className="font-medium">{CASE_STAGE_LABELS[data.stage]}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Status</dt>
              <dd className="mt-1">
                <CaseStatusChip status={data.status} />
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Priority</dt>
              <dd className="mt-1">
                <CasePriorityBadge priority={data.priority} />
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Opened</dt>
              <dd className="font-medium">{formatDateTime(data.opened_at)}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Closed</dt>
              <dd className="font-medium">{formatDateTime(data.closed_at)}</dd>
            </div>
          </dl>
          {data.summary ? (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-700">Summary</h3>
              <p className="mt-1 whitespace-pre-wrap text-sm text-gray-600">{data.summary}</p>
            </div>
          ) : null}
          {data.notes ? (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-700">Notes</h3>
              <p className="mt-1 whitespace-pre-wrap text-sm text-gray-600">{data.notes}</p>
            </div>
          ) : null}
        </Card>

        <Card title="Credit accounts">
          <p className="text-sm text-gray-600">View tradelines linked to this case.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Link to={`/cases/${caseId}/accounts`}>
              <Button variant="secondary" size="sm">
                View accounts
              </Button>
            </Link>
            {featureFlags.enableImports ? (
              <Link to={`/imports/credit-report?case_id=${caseId}`}>
                <Button size="sm">Import credit report</Button>
              </Link>
            ) : null}
          </div>
        </Card>

        <Card title="Metadata">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-gray-500">Created</dt>
              <dd>{formatDateTime(data.created_at)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Updated</dt>
              <dd>{formatDateTime(data.updated_at)}</dd>
            </div>
          </dl>
        </Card>

        <CreditReportHistoryPanel caseId={caseId} className="lg:col-span-3" />
      </div>

      <CaseDeleteDialog
        open={deleteOpen}
        caseTitle={data.title}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteOpen(false)}
      />
    </div>
  );
}
