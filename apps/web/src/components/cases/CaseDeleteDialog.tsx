import { Button, Card } from '@verdin/ui';

interface CaseDeleteDialogProps {
  open: boolean;
  caseTitle: string;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function CaseDeleteDialog({
  open,
  caseTitle,
  loading,
  onConfirm,
  onCancel,
}: CaseDeleteDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gray-900/50" aria-hidden="true" onClick={onCancel} />
      <Card className="relative z-10 w-full max-w-md" title="Delete case">
        <p className="text-sm text-gray-600">
          Are you sure you want to delete <strong>{caseTitle}</strong>? This action cannot be
          undone.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>
            Delete
          </Button>
        </div>
      </Card>
    </div>
  );
}
