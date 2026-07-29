import { redirect } from 'next/navigation';

/** Alias route — financial planners land on /advisors (LRP-305). */
export default function FinancialPlannersAliasPage() {
  redirect('/advisors');
}
