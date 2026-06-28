import { Card, CardContent, CardHeader, CardTitle, PageHeader, ShellContent } from '@verdin/ui';
import { ROLE_LABELS, type UserRole } from '@verdin/shared';
import { useAuth } from '../lib/auth';

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <ShellContent>
      <PageHeader title="Settings" description="Manage your account and preferences." />

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>
    </ShellContent>
  );
}
