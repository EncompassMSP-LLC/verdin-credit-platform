import { useMutation } from '@tanstack/react-query';
import { completeClientEnrollment } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';

import { establishPortalSession } from '../../lib/portal-auth';

export function EnrollSuccessPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [mutationError, setMutationError] = useState<string | null>(null);
  const startedRef = useRef(false);

  const validationError = (() => {
    if (!sessionId) {
      return 'Missing payment session. Return to enrollment and try again.';
    }
    if (!sessionId.startsWith('cs_')) {
      return 'Invalid checkout session id.';
    }
    return null;
  })();

  const completeMutation = useMutation({
    mutationFn: () => {
      if (!sessionId) throw new Error('Missing checkout session');
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
        {completeMutation.isPending ? (
          <>
            <h1 className="text-2xl font-bold text-gray-900">Finalizing your enrollment</h1>
            <p className="mt-2 text-sm text-gray-600">
              Confirming payment and creating your client portal account…
            </p>
          </>
        ) : null}

        {error ? (
          <>
            <h1 className="text-2xl font-bold text-gray-900">Enrollment could not be completed</h1>
            <p className="mt-2 text-sm text-red-600">{error}</p>
            <Link to="/enroll" className="mt-6 inline-block">
              <Button variant="secondary">Back to enrollment</Button>
            </Link>
          </>
        ) : null}
      </Card>
    </div>
  );
}
