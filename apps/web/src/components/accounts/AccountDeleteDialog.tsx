import { Button } from '@verdin/ui';

interface AccountDeleteDialogProps {
  creditorName: string;
  open: boolean;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function AccountDeleteDialog({
  creditorName,
  open,
  loading,
  onConfirm,
  onCancel,
}: AccountDeleteDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <h2 className="text-lg font-semibold text-gray-900">Delete account</h2>
        <p className="mt-2 text-sm text-gray-600">
          Are you sure you want to delete <strong>{creditorName}</strong>? This action cannot be
          undone.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" loading={loading} onClick={onConfirm}>
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
