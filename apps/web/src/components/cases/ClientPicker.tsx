import { useQuery } from '@tanstack/react-query';
import { listClients, type Client } from '@verdin/api-client';
import { Link } from 'react-router-dom';

const selectClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface ClientPickerProps {
  value: string;
  onChange: (clientId: string, client: Client | null) => void;
  error?: string;
}

export function ClientPicker({ value, onChange, error }: ClientPickerProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['clients', 'picker'],
    queryFn: () =>
      listClients({ page_size: 100, status: 'active', sort_by: 'display_name', sort_order: 'asc' }),
  });

  const selectedClient = data?.items.find((client) => client.id === value) ?? null;

  return (
    <div className="space-y-2">
      <div>
        <label htmlFor="client_id" className="block text-sm font-medium text-gray-700">
          Linked client
        </label>
        <select
          id="client_id"
          className={selectClass}
          value={value}
          onChange={(event) => {
            const clientId = event.target.value;
            const client = data?.items.find((item) => item.id === clientId) ?? null;
            onChange(clientId, client);
          }}
          disabled={isLoading}
        >
          <option value="">{isLoading ? 'Loading clients…' : 'Manual client entry'}</option>
          {data?.items.map((client) => (
            <option key={client.id} value={client.id}>
              {client.display_name}
              {client.email ? ` (${client.email})` : ''}
            </option>
          ))}
        </select>
        {error ? <p className="mt-1 text-sm text-red-600">{error}</p> : null}
        <p className="mt-1 text-xs text-gray-500">
          Link to a client record for portal access and durable case matching, or enter details
          manually below.
        </p>
      </div>
      {selectedClient ? (
        <p className="text-sm text-gray-600">
          Profile:{' '}
          <Link to={`/clients/${selectedClient.id}`} className="text-brand-600 hover:underline">
            {selectedClient.display_name}
          </Link>
        </p>
      ) : null}
    </div>
  );
}
