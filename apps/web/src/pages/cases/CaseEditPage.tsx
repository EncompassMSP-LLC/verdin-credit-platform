import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { getCase } from '@verdin/api-client';
import { Card } from '@verdin/ui';
import { CaseFormPage } from './CaseFormPage';

export function CaseEditPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: Boolean(caseId),
  });

  if (!caseId) return null;

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
    <CaseFormPage
      mode="edit"
      caseId={caseId}
      defaultValues={{
        title: data.title,
        client_id: data.client_id ?? '',
        client_name: data.client_name,
        client_email: data.client_email ?? '',
        case_number: data.case_number ?? '',
        status: data.status,
        stage: data.stage,
        priority: data.priority,
        summary: data.summary ?? '',
        notes: data.notes ?? '',
      }}
    />
  );
}
