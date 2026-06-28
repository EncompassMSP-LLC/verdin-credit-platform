import { Card, EmptyState, PageHeader, ShellContent } from '@verdin/ui';

export function TasksPage() {
  return (
    <ShellContent>
      <PageHeader title="Tasks" description="Track and assign case tasks." />
      <Card className="mt-8">
        <EmptyState title="No tasks yet" description="Task management UI coming in Sprint 2." />
      </Card>
    </ShellContent>
  );
}
