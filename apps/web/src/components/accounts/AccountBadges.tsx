import type { AccountBureau, AccountStatus, DisputeStatus } from '@verdin/shared';
import { ACCOUNT_STATUS_LABELS, BUREAU_LABELS, DISPUTE_STATUS_LABELS } from '@verdin/shared';
import { Badge } from '@verdin/ui';

const bureauVariants: Record<AccountBureau, 'default' | 'success' | 'warning' | 'danger' | 'info'> =
  {
    equifax: 'danger',
    experian: 'info',
    transunion: 'success',
    innovis: 'warning',
    unknown: 'default',
  };

const statusVariants: Record<AccountStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> =
  {
    open: 'info',
    closed: 'default',
    collection: 'danger',
    charge_off: 'danger',
    repossession: 'danger',
    foreclosure: 'danger',
    transferred: 'warning',
    paid: 'success',
    settled: 'success',
    deleted: 'default',
    unknown: 'default',
  };

const disputeVariants: Record<
  DisputeStatus,
  'default' | 'success' | 'warning' | 'danger' | 'info'
> = {
  not_started: 'default',
  evidence_needed: 'warning',
  ready_for_dispute: 'success',
  dispute_sent: 'info',
  awaiting_response: 'info',
  verified: 'default',
  corrected: 'success',
  deleted: 'success',
  escalated: 'danger',
  monitoring: 'warning',
};

export function BureauBadge({ bureau }: { bureau: AccountBureau }) {
  return <Badge variant={bureauVariants[bureau]}>{BUREAU_LABELS[bureau]}</Badge>;
}

export function AccountStatusChip({ status }: { status: AccountStatus }) {
  return <Badge variant={statusVariants[status]}>{ACCOUNT_STATUS_LABELS[status]}</Badge>;
}

export function DisputeStatusChip({ status }: { status: DisputeStatus }) {
  return <Badge variant={disputeVariants[status]}>{DISPUTE_STATUS_LABELS[status]}</Badge>;
}

export function ScoreDisplay({
  label,
  score,
  variant = 'default',
}: {
  label: string;
  score: number | null;
  variant?: 'risk' | 'readiness' | 'default';
}) {
  if (score === null) {
    return (
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm text-gray-400">—</p>
      </div>
    );
  }

  let badgeVariant: 'default' | 'success' | 'warning' | 'danger' | 'info' = 'default';
  if (variant === 'risk') {
    badgeVariant = score >= 75 ? 'danger' : score >= 50 ? 'warning' : 'success';
  } else if (variant === 'readiness') {
    badgeVariant = score >= 80 ? 'success' : score >= 50 ? 'info' : 'warning';
  }

  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <Badge variant={badgeVariant}>{score}</Badge>
    </div>
  );
}
