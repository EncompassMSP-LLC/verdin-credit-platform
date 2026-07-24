'use client';

import {
  getMortgagePartnerStatus,
  getPartnerDashboardSummary,
  getPartnershipPipeline,
  listPartnerReferrals,
  listPartnerships,
  listReferralMilestones,
  replaceReferralMilestones,
  updatePartnerReferral,
  type MilestoneReplacePayload,
  type PartnerDashboardSummary,
  type PartnerLoanMilestone,
  type PartnerReferral,
  type PartnerReferralStatus,
  type Partnership,
  type PipelineCard,
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

export function useLenderPipeline(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'pipeline', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => getPartnershipPipeline(partnershipId!),
  });
}

export function useLenderDashboardSummary(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'dashboard-summary', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => getPartnerDashboardSummary(partnershipId!),
  });
}

export function useReferralMilestones(
  partnershipId: string | undefined,
  referralId: string | undefined,
) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'mortgage-partner', 'milestones', partnershipId, referralId],
    enabled:
      isAuthenticated && authMode === 'platform' && Boolean(partnershipId) && Boolean(referralId),
    queryFn: () => listReferralMilestones(partnershipId!, referralId!),
  });
}

export function useReplaceReferralMilestones(
  partnershipId: string | undefined,
  referralId: string | undefined,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: MilestoneReplacePayload) => {
      if (!partnershipId || !referralId) {
        throw new Error('Partnership and referral IDs are required to update milestones');
      }
      return replaceReferralMilestones(partnershipId, referralId, payload);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'milestones', partnershipId, referralId],
      });
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'referrals', partnershipId],
      });
    },
  });
}

export function useUpdateLenderReferral(partnershipId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      referralId,
      status,
      pipeline_stage,
    }: {
      referralId: string;
      status?: PartnerReferralStatus;
      pipeline_stage?: string;
    }) => {
      if (!partnershipId) {
        throw new Error('Partnership is required to update a referral');
      }
      return updatePartnerReferral(partnershipId, referralId, {
        status,
        pipeline_stage,
      } as Parameters<typeof updatePartnerReferral>[2]);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'referrals', partnershipId],
      });
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'pipeline', partnershipId],
      });
      void queryClient.invalidateQueries({
        queryKey: ['lender', 'mortgage-partner', 'dashboard-summary', partnershipId],
      });
    },
  });
}

export type {
  PartnerDashboardSummary,
  PartnerLoanMilestone,
  PartnerReferral,
  PartnerReferralStatus,
  Partnership,
  PipelineCard,
};
