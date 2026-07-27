'use client';

import {
  createPartnerContact,
  getMortgagePartnerStatus,
  listCrmAutomationRules,
  listPartnerContacts,
  listPartnerReferrals,
  listPartnerships,
  updateCrmAutomationRule,
  updatePartnerContact,
  updatePartnerReferral,
  type CrmAutomationRuleUpdateInput,
  type PartnerContact,
  type PartnerContactCreateInput,
  type PartnerContactUpdateInput,
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

export function useCrmPartnerContacts(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'mortgage-partner', 'contacts', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => listPartnerContacts(partnershipId!),
  });
}

export function useCreateCrmPartnerContact(partnershipId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: PartnerContactCreateInput) => {
      if (!partnershipId) {
        throw new Error('Partnership is required to create a contact');
      }
      return createPartnerContact(partnershipId, body);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'mortgage-partner', 'contacts', partnershipId],
      });
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'mortgage-partner', 'partnerships'],
      });
    },
  });
}

export function useUpdateCrmPartnerContact(partnershipId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ contactId, body }: { contactId: string; body: PartnerContactUpdateInput }) => {
      if (!partnershipId) {
        throw new Error('Partnership is required to update a contact');
      }
      return updatePartnerContact(partnershipId, contactId, body);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'mortgage-partner', 'contacts', partnershipId],
      });
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'mortgage-partner', 'partnerships'],
      });
    },
  });
}

export function useCrmAutomationRules() {
  const { isAuthenticated, authMode } = useCrmAuth();
  const status = useCrmMortgagePartnerStatus();
  return useQuery({
    queryKey: ['crm', 'mortgage-partner', 'automation-rules'],
    enabled:
      isAuthenticated && authMode === 'platform' && status.data?.mortgage_partner_enabled === true,
    queryFn: listCrmAutomationRules,
  });
}

export function useUpdateCrmAutomationRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ruleId, body }: { ruleId: string; body: CrmAutomationRuleUpdateInput }) =>
      updateCrmAutomationRule(ruleId, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ['crm', 'mortgage-partner', 'automation-rules'],
      });
    },
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

export type {
  PartnerContact,
  PartnerContactCreateInput,
  PartnerReferral,
  PartnerReferralStatus,
  Partnership,
};
