'use client';

import {
  getRealtorPipeline,
  getRealtorPortalDashboard,
  listRealtorReferrals,
  type RealtorPipelineBoard,
  type RealtorPortalDashboard,
  type RealtorReferralCard,
} from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { useRealtorAuth } from '@/lib/realtor/auth';

export function useRealtorPortalDashboard() {
  const { authMode, isAuthenticated } = useRealtorAuth();
  return useQuery<RealtorPortalDashboard>({
    queryKey: ['realtor', 'dashboard'],
    queryFn: getRealtorPortalDashboard,
    enabled: isAuthenticated && authMode === 'platform',
  });
}

export function useRealtorReferrals() {
  const { authMode, isAuthenticated } = useRealtorAuth();
  return useQuery<RealtorReferralCard[]>({
    queryKey: ['realtor', 'referrals'],
    queryFn: listRealtorReferrals,
    enabled: isAuthenticated && authMode === 'platform',
  });
}

export function useRealtorPipeline() {
  const { authMode, isAuthenticated } = useRealtorAuth();
  return useQuery<RealtorPipelineBoard>({
    queryKey: ['realtor', 'pipeline'],
    queryFn: getRealtorPipeline,
    enabled: isAuthenticated && authMode === 'platform',
  });
}

export const STAGE_LABELS: Record<string, string> = {
  referred: 'Referred',
  intake: 'Intake',
  in_repair: 'In repair',
  near_ready: 'Near ready',
  mortgage_ready: 'Mortgage ready',
  in_underwriting: 'In underwriting',
  funded: 'Funded',
  declined: 'Declined',
  withdrawn: 'Withdrawn',
};
