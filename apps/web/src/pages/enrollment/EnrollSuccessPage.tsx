import { useMutation } from '@tanstack/react-query';
import { completeClientEnrollment } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { establishPortalSession } from '../../lib/portal-auth';

export function EnrollSuccessPage() {
  const { t } = useTranslation('enrollment');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [mutationError, setMutationError] = useState<string | null>(null);
  const startedRef = useRef(false);

  const validationError = (() => {
    if (!sessionId) {
      return t('successMissingSession');
    }
    if (!sessionId.startsWith('cs_')) {
      return t('successInvalidSession');
    }
    return null;
  })();

  const completeMutation = useMutation({
    mutationFn: () => {
      if (!sessionId) throw new Error(t('successMissingSession'));
      return completeClientEnrollment(sessionId);
    },
    onSuccess: async (result) => {
      await establishPortalSession(result.portal);
      if (result.enrollment.case_id) {
        navigate(`/portal/cases/${result.enrollment.case_id}`, { replace: true });
        return;
      }
      navigate('/portal', { replace: true });
    },
    onError: (err: Error) => setMutationError(err.message),
  });

  useEffect(() => {
    if (validationError || startedRef.current) return;
    startedRef.current = true;
    completeMutation.mutate();
  }, [validationError, completeMutation]);

  const error = validationError ?? mutationError;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-lg p-8 text-center">
        <div className="mb-4 flex justify-end">
          <LanguageSwitcher compact />
        </div>
        {completeMutation.isPending ? (
          <>
            <h1 className="text-2xl font-bold text-gray-900">{t('successFinalizingTitle')}</h1>
            <p className="mt-2 text-sm text-gray-600">{t('successFinalizingBody')}</p>
          </>
        ) : null}

        {error ? (
          <>
            <h1 className="text-2xl font-bold text-gray-900">{t('successErrorTitle')}</h1>
            <p className="mt-2 text-sm text-red-600">{error}</p>
            <Link to="/enroll" className="mt-6 inline-block">
              <Button variant="secondary">{t('successBack')}</Button>
            </Link>
          </>
        ) : null}
      </Card>
    </div>
  );
}
