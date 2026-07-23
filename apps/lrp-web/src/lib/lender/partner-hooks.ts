'use client';

import {
  getMortgagePartnerStatus,
  listPartnerReferrals,
  listPartnerships,
  updatePartnerReferral,
  type PartnerReferral,
  type PartnerReferralStatus,
  type Partnership,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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

export function useUpdateLenderReferral(partnershipId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ referralId, status }: { referralId: string; status: PartnerReferralStatus }) => {
      if (!partnershipId) {
        throw new Error('Partnership is required to update a referral');
      }
      return updatePartnerReferral(partnershipId, referralId, { status });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'referrals', partnershipId],
      });
    },
  });
}

export type { PartnerReferral, PartnerReferralStatus, Partnership };
