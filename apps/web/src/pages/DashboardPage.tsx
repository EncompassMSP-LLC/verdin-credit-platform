import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  PageHeader,
  ShellContent,
  StatCard,
} from '@verdin/ui';
import { useAuth } from '../lib/auth';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <ShellContent>
      <PageHeader
        title="Dashboard"
        description={`Welcome back, ${user?.first_name}. Here is your credit operations overview.`}
      />

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Open Cases" value="—" valueClassName="text-blue-600" />
        <StatCard label="Active Accounts" value="—" valueClassName="text-green-600" />
        <StatCard label="Pending Tasks" value="—" valueClassName="text-yellow-600" />
        <StatCard label="Documents" value="—" valueClassName="text-purple-600" />
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">Activity feed will be populated in Sprint 2.</p>
        </CardContent>
      </Card>
    </ShellContent>
  );
}
