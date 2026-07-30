import { createMetadata } from '@/lib/seo';
import ForgotPasswordPageClient from '@/components/portal/ForgotPasswordForm';

export const metadata = createMetadata({
  title: 'Reset Portal Password',
  description: 'Request a self-serve password reset for your borrower portal account.',
  path: '/portal/forgot-password',
  noIndex: true,
});

export default function ForgotPasswordPage() {
  return <ForgotPasswordPageClient />;
}
