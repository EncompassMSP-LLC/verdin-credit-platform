import { Navigate, Route, Routes } from 'react-router-dom';
import { PortalAuthProvider, usePortalAuth } from '../lib/portal-auth';
import { PortalLoginPage } from '../pages/portal/PortalLoginPage';
import { PortalAcceptInvitePage } from '../pages/portal/PortalAcceptInvitePage';
import { PortalResetPasswordPage } from '../pages/portal/PortalResetPasswordPage';
import { PortalCasesPage } from '../pages/portal/PortalCasesPage';
import { PortalCaseDetailPage } from '../pages/portal/PortalCaseDetailPage';
import { featureFlags } from '../lib/feature-flags';

function ProtectedPortalRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = usePortalAuth();

  if (!featureFlags.enableClientPortal) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/portal/login" replace />;
  }

  return <>{children}</>;
}

export function PortalRoutes() {
  return (
    <PortalAuthProvider>
      <Routes>
        <Route path="login" element={<PortalLoginPage />} />
        <Route path="accept-invite" element={<PortalAcceptInvitePage />} />
        <Route path="reset-password" element={<PortalResetPasswordPage />} />
        <Route
          index
          element={
            <ProtectedPortalRoute>
              <PortalCasesPage />
            </ProtectedPortalRoute>
          }
        />
        <Route
          path="cases/:caseId"
          element={
            <ProtectedPortalRoute>
              <PortalCaseDetailPage />
            </ProtectedPortalRoute>
          }
        />
      </Routes>
    </PortalAuthProvider>
  );
}
