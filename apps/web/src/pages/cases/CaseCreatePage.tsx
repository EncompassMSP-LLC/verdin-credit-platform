import { useSearchParams } from 'react-router-dom';
import { CaseFormPage } from './CaseFormPage';

export function CaseCreatePage() {
  const [searchParams] = useSearchParams();
  const clientId = searchParams.get('client_id') ?? '';

  return (
    <CaseFormPage
      mode="create"
      defaultValues={{
        title: '',
        client_id: clientId,
        client_name: '',
        client_email: '',
        status: 'open',
        stage: 'intake',
        priority: 'medium',
        summary: '',
        notes: '',
      }}
    />
  );
}
