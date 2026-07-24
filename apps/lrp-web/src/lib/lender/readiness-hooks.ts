'use client';

/**
 * Lender readiness hooks — wire the Mortgage Partner Readiness Report API.
 *
 * Disclaimer: Lending Readiness Score™ is an advisory tool for organizing
 * credit and documentation work toward a mortgage conversation. It is not a
 * credit score from a consumer reporting agency, not an underwriting decision,
 * and not a guarantee of loan approval or terms.
 */

import {
  getReferralReadinessReport,
  getReferralReadinessReportExportUrl,
  listPartnershipReadinessReports,
  type MortgageReadinessReport,
  type ReadinessReportSummary,
} from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { useLenderAuth } from '@/lib/lender/auth';

/** List advisory readiness summaries for all referrals with published runs. */
export function usePartnershipReadinessReports(partnershipId: string | undefined) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'readiness-reports', partnershipId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(partnershipId),
    queryFn: () => listPartnershipReadinessReports(partnershipId!),
    retry: false,
  });
}

/** Get full advisory readiness report for a single referral. */
export function useReferralReadinessReport(
  partnershipId: string | undefined,
  referralId: string | undefined,
) {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'readiness-report', partnershipId, referralId],
    enabled:
      isAuthenticated && authMode === 'platform' && Boolean(partnershipId) && Boolean(referralId),
    queryFn: () => getReferralReadinessReport(partnershipId!, referralId!),
    retry: false,
  });
}

/** Return the PDF export URL for a referral's readiness report (operator-gated). */
export function readinessExportUrl(
  partnershipId: string,
  referralId: string,
  format: 'text' | 'pdf' = 'pdf',
): string {
  return getReferralReadinessReportExportUrl(partnershipId, referralId, format);
}

export type { MortgageReadinessReport, ReadinessReportSummary };
