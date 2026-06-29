import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  confirmDocumentResolution,
  getDocumentResolutions,
  rejectDocumentResolution,
  resolveDocumentEntities,
  type DocumentEntityResolution,
} from '@verdin/api-client';
import {
  MATCHED_ENTITY_TYPE_LABELS,
  RESOLUTION_STATUS_LABELS,
  type ResolutionStatus,
} from '@verdin/shared';
import { Badge, Button, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

interface DocumentEntityResolutionPanelProps {
  documentId: string;
  hasMetadata: boolean;
}

const STATUS_VARIANT: Record<
  ResolutionStatus,
  'default' | 'success' | 'warning' | 'danger' | 'info'
> = {
  matched: 'success',
  ambiguous: 'warning',
  unmatched: 'default',
  confirmed: 'success',
  rejected: 'danger',
};

function ResolutionRow({
  documentId,
  resolution,
}: {
  documentId: string;
  resolution: DocumentEntityResolution;
}) {
  const queryClient = useQueryClient();
  const [selectedCandidate, setSelectedCandidate] = useState(
    resolution.matched_entity_id ?? resolution.candidate_entity_ids[0] ?? '',
  );

  const confirmMutation = useMutation({
    mutationFn: (matchedEntityId?: string) =>
      confirmDocumentResolution(documentId, resolution.id, matchedEntityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-resolutions', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectDocumentResolution(documentId, resolution.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-resolutions', documentId] });
    },
  });

  const entityLink =
    resolution.matched_entity_id && resolution.entity_type === 'case'
      ? `/cases/${resolution.matched_entity_id}`
      : resolution.matched_entity_id && resolution.entity_type === 'account'
        ? `/accounts/${resolution.matched_entity_id}`
        : null;

  return (
    <li className="rounded-md border border-gray-100 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-gray-900">
            {MATCHED_ENTITY_TYPE_LABELS[resolution.entity_type]}
          </span>
          <Badge variant={STATUS_VARIANT[resolution.resolution_status]}>
            {RESOLUTION_STATUS_LABELS[resolution.resolution_status]}
          </Badge>
          <span className="text-xs text-gray-500">
            {Math.round(resolution.confidence_score * 100)}% confidence
          </span>
        </div>
        {entityLink ? (
          <Link to={entityLink} className="text-sm text-brand-600 hover:underline">
            View match
          </Link>
        ) : null}
      </div>
      {resolution.reasoning ? (
        <p className="mt-2 text-sm text-gray-600">{resolution.reasoning}</p>
      ) : null}
      {resolution.resolution_status === 'ambiguous' ? (
        <div className="mt-3 space-y-2">
          <label
            className="block text-sm font-medium text-gray-700"
            htmlFor={`candidate-${resolution.id}`}
          >
            Select candidate
          </label>
          <select
            id={`candidate-${resolution.id}`}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            value={selectedCandidate}
            onChange={(e) => setSelectedCandidate(e.target.value)}
          >
            {resolution.candidate_entity_ids.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => confirmMutation.mutate(selectedCandidate || undefined)}
              disabled={confirmMutation.isPending || !selectedCandidate}
            >
              Confirm match
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => rejectMutation.mutate()}
              disabled={rejectMutation.isPending}
            >
              Reject
            </Button>
          </div>
        </div>
      ) : null}
      {resolution.resolution_status === 'matched' && !resolution.reviewed_at ? (
        <div className="mt-3 flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() => confirmMutation.mutate()}
            disabled={confirmMutation.isPending}
          >
            Confirm
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => rejectMutation.mutate()}
            disabled={rejectMutation.isPending}
          >
            Reject
          </Button>
        </div>
      ) : null}
    </li>
  );
}

export function DocumentEntityResolutionPanel({
  documentId,
  hasMetadata,
}: DocumentEntityResolutionPanelProps) {
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['document-resolutions', documentId],
    queryFn: () => getDocumentResolutions(documentId),
    enabled: hasMetadata,
    retry: false,
  });

  const resolveMutation = useMutation({
    mutationFn: () => resolveDocumentEntities(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-resolutions', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
    },
  });

  if (!hasMetadata) {
    return (
      <Card title="Entity matches">
        <p className="text-sm text-gray-500">Extract metadata before resolving entities.</p>
      </Card>
    );
  }

  return (
    <Card title="Entity matches">
      <div className="mb-4 flex justify-end">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => resolveMutation.mutate()}
          disabled={resolveMutation.isPending}
        >
          Resolve
        </Button>
      </div>
      {isLoading ? <p className="text-sm text-gray-500">Loading resolutions...</p> : null}
      {isError ? (
        <p className="text-sm text-gray-500">
          {error instanceof Error && error.message.includes('404')
            ? 'No entity resolutions yet. Run resolve to link cases and accounts.'
            : error instanceof Error
              ? error.message
              : 'Failed to load resolutions'}
        </p>
      ) : null}
      {data && data.resolutions.length > 0 ? (
        <ul className="space-y-3">
          {data.resolutions.map((resolution) => (
            <ResolutionRow key={resolution.id} documentId={documentId} resolution={resolution} />
          ))}
        </ul>
      ) : (
        !isLoading &&
        !isError && (
          <p className="text-sm text-gray-500">
            No entity matches yet. Click Resolve to run deterministic matching.
          </p>
        )
      )}
      {resolveMutation.isError ? (
        <p className="mt-3 text-sm text-red-600">
          {resolveMutation.error instanceof Error
            ? resolveMutation.error.message
            : 'Resolution failed'}
        </p>
      ) : null}
    </Card>
  );
}
