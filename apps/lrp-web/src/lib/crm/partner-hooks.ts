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
import { useCrmAuth } from '@/lib/crm/auth';

export function useCrmMortgagePartnerStatus() {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'mortgage-partner', 'status'],
    enabled: isAuthenticated && authMode === 'platform',
    queryFn: getMortgagePartnerStatus,
  });
}

export function useCrmPartnerships() {
  const { isAuthenticated, authMode } = useCrmAuth();
  const status = useCrmMortgagePartnerStatus();
  return useQuery({
    queryKey: ['crm', 'mortgage-partner', 'partnerships'],
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

export function useCrmReferrals(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'mortgage-partner', 'referrals', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => listPartnerReferrals(partnershipId!),
  });
}

export function useUpdateCrmReferral(partnershipId: string | undefined) {
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
        queryKey: ['crm', 'mortgage-partner', 'referrals', partnershipId],
      });
    },
  });
}

export type { PartnerReferral, PartnerReferralStatus, Partnership };
