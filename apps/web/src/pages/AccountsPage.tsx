import { Card, EmptyState, PageHeader, ShellContent } from '@verdin/ui';

export function AccountsPage() {
  return (
    <ShellContent>
      <PageHeader title="Accounts" description="Manage client accounts." />
      <Card className="mt-8">
        <EmptyState
          title="No accounts yet"
          description="Account management UI coming in Sprint 2."
        />
      </Card>
    </ShellContent>
  );
}
