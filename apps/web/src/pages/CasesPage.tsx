import { Card, EmptyState, PageHeader, ShellContent } from '@verdin/ui';

export function CasesPage() {
  return (
    <ShellContent>
      <PageHeader title="Cases" description="Manage credit review cases." />
      <Card className="mt-8">
        <EmptyState title="No cases yet" description="Case management UI coming in Sprint 2." />
      </Card>
    </ShellContent>
  );
}
