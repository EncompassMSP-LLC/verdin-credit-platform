import { Card, EmptyState, PageHeader, ShellContent } from '@verdin/ui';

export function DocumentsPage() {
  return (
    <ShellContent>
      <PageHeader title="Documents" description="Upload and manage case documents." />
      <Card className="mt-8">
        <EmptyState
          title="No documents yet"
          description="Document management UI coming in Sprint 3."
        />
      </Card>
    </ShellContent>
  );
}
