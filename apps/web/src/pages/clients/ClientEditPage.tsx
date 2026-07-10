import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { getClient } from '@verdin/api-client';
import { Card } from '@verdin/ui';
import { ClientFormPage } from './ClientFormPage';

export function ClientEditPage() {
  const { clientId } = useParams<{ clientId: string }>();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['client', clientId],
    queryFn: () => getClient(clientId!),
    enabled: Boolean(clientId),
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading client…</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-8 text-center text-sm text-red-600">
            {error instanceof Error ? error.message : 'Client not found'}
          </p>
          <div className="pb-6 text-center">
            <Link to="/clients" className="text-sm text-brand-600 hover:underline">
              Back to clients
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <ClientFormPage
      mode="edit"
      clientId={data.id}
      defaultValues={{
        display_name: data.display_name,
        email: data.email ?? '',
        phone: data.phone ?? '',
        mailing_address_line1: data.mailing_address_line1 ?? '',
        mailing_address_line2: data.mailing_address_line2 ?? '',
        mailing_city: data.mailing_city ?? '',
        mailing_state: data.mailing_state ?? '',
        mailing_postal_code: data.mailing_postal_code ?? '',
        status: data.status,
        notes: data.notes ?? '',
      }}
    />
  );
}
