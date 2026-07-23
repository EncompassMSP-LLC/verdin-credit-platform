'use client';

import {
  getMortgagePartnerStatus,
  listPartnerReferrals,
  listPartnerships,
  type PartnerReferral,
  type Partnership,
} from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { useLenderAuth } from '@/lib/lender/auth';

export function useMortgagePartnerStatus() {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'status'],
    enabled: isAuthenticated && authMode === 'platform',
    queryFn: getMortgagePartnerStatus,
  });
}

export function useLenderPartnerships() {
  const { isAuthenticated, authMode } = useLenderAuth();
  const status = useMortgagePartnerStatus();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'partnerships'],
    enabled:
      isAuthenticated && authMode === 'platform' && status.data?.mortgage_partner_enabled === true,
    queryFn: listPartnerships,
  });
}

/** Prefer first active partnership; fall back to first listed. */
export function pickPrimaryPartnership(items: Partnership[] | undefined): Partnership | null {
  if (!items?.length) return null;
  return items.find((p) => p.status === 'active') ?? items[0] ?? null;
}

export function useLenderReferrals(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'referrals', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => listPartnerReferrals(partnershipId!),
  });
}

export type { PartnerReferral, Partnership };
