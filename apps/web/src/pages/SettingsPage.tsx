import { Card } from '@verdin/ui';
import { ROLE_LABELS, type UserRole } from '@verdin/shared';
import { useAuth } from '../lib/auth';

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      <p className="mt-1 text-gray-500">Manage your account and preferences.</p>

      <Card title="Profile" className="mt-8">
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500">Name</dt>
            <dd className="font-medium">
              {user?.first_name} {user?.last_name}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Email</dt>
            <dd className="font-medium">{user?.email}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Role</dt>
            <dd className="font-medium">
              {user?.role ? ROLE_LABELS[user.role as UserRole] : '—'}
            </dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
