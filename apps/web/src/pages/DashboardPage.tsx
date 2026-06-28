import { Card } from '@verdin/ui';
import { useAuth } from '../lib/auth';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p className="mt-1 text-gray-500">
        Welcome back, {user?.first_name}. Here is your credit operations overview.
      </p>

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Open Cases', value: '—', color: 'text-blue-600' },
          { label: 'Active Accounts', value: '—', color: 'text-green-600' },
          { label: 'Pending Tasks', value: '—', color: 'text-yellow-600' },
          { label: 'Documents', value: '—', color: 'text-purple-600' },
        ].map((stat) => (
          <Card key={stat.label}>
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className={`mt-1 text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </Card>
        ))}
      </div>

      <div className="mt-8">
        <Card title="Recent Activity">
          <p className="text-sm text-gray-500">
            Activity feed will be populated in Sprint 2.
          </p>
        </Card>
      </div>
    </div>
  );
}
