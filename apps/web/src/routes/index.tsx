import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { AppLayout } from '../components/AppLayout';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { CasesListPage } from '../pages/cases/CasesListPage';
import { CaseCreatePage } from '../pages/cases/CaseCreatePage';
import { CaseDetailPage } from '../pages/cases/CaseDetailPage';
import { CaseDisputePlaybookPage } from '../pages/cases/CaseDisputePlaybookPage';
import { CaseEditPage } from '../pages/cases/CaseEditPage';
import { AccountsListPage } from '../pages/accounts/AccountsListPage';
import { AccountCreatePage } from '../pages/accounts/AccountCreatePage';
import { AccountDetailPage } from '../pages/accounts/AccountDetailPage';
import { AccountEditPage } from '../pages/accounts/AccountEditPage';
import { CaseAccountsPage } from '../pages/accounts/CaseAccountsPage';
import { DocumentsListPage } from '../pages/documents/DocumentsListPage';
import { DocumentUploadPage } from '../pages/documents/DocumentUploadPage';
import { DocumentDetailPage } from '../pages/documents/DocumentDetailPage';
import { CreditReportImportWizard } from '../pages/imports/CreditReportImportWizard';
import { TimelinePage } from '../pages/timeline/TimelinePage';
import { TasksListPage } from '../pages/tasks/TasksListPage';
import { TaskCreatePage } from '../pages/tasks/TaskCreatePage';
import { TaskDetailPage } from '../pages/tasks/TaskDetailPage';
import { TaskEditPage } from '../pages/tasks/TaskEditPage';
import { SettingsPage } from '../pages/SettingsPage';
import { ClientsListPage } from '../pages/clients/ClientsListPage';
import { ClientCreatePage } from '../pages/clients/ClientCreatePage';
import { ClientDetailPage } from '../pages/clients/ClientDetailPage';
import { ClientEditPage } from '../pages/clients/ClientEditPage';
import { ComplianceCenterPage } from '../pages/compliance/ComplianceCenterPage';
import { ReportingCenterPage } from '../pages/reporting/ReportingCenterPage';
import { OrgAdminPage } from '../pages/org-admin/OrgAdminPage';
import { DisputeWorkflowGuidePage } from '../pages/guides/DisputeWorkflowGuidePage';
import { EnrollPage } from '../pages/enrollment/EnrollPage';
import { EnrollSuccessPage } from '../pages/enrollment/EnrollSuccessPage';
import { PortalRoutes } from './portal';
import { featureFlags } from '../lib/feature-flags';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
      />
      {featureFlags.enableClientEnrollment ? (
        <>
          <Route path="/enroll" element={<EnrollPage />} />
          <Route path="/enroll/success" element={<EnrollSuccessPage />} />
        </>
      ) : null}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="cases" element={<CasesListPage />} />
        <Route path="cases/new" element={<CaseCreatePage />} />
        <Route path="cases/:caseId" element={<CaseDetailPage />} />
        <Route path="cases/:caseId/dispute-playbook" element={<CaseDisputePlaybookPage />} />
        <Route path="cases/:caseId/edit" element={<CaseEditPage />} />
        <Route path="cases/:caseId/accounts" element={<CaseAccountsPage />} />
        <Route path="clients" element={<ClientsListPage />} />
        <Route path="clients/new" element={<ClientCreatePage />} />
        <Route path="clients/:clientId" element={<ClientDetailPage />} />
        <Route path="clients/:clientId/edit" element={<ClientEditPage />} />
        <Route path="accounts" element={<AccountsListPage />} />
        <Route path="accounts/new" element={<AccountCreatePage />} />
        <Route path="accounts/:accountId" element={<AccountDetailPage />} />
        <Route path="accounts/:accountId/edit" element={<AccountEditPage />} />
        <Route path="documents" element={<DocumentsListPage />} />
        <Route path="documents/upload" element={<DocumentUploadPage />} />
        <Route path="documents/:documentId" element={<DocumentDetailPage />} />
        <Route path="imports/credit-report" element={<CreditReportImportWizard />} />
        <Route path="timeline" element={<TimelinePage />} />
        <Route path="tasks" element={<TasksListPage />} />
        <Route path="tasks/new" element={<TaskCreatePage />} />
        <Route path="tasks/:taskId" element={<TaskDetailPage />} />
        <Route path="tasks/:taskId/edit" element={<TaskEditPage />} />
        {featureFlags.enableEnterprise ? (
          <>
            <Route path="compliance" element={<ComplianceCenterPage />} />
            <Route path="reporting" element={<ReportingCenterPage />} />
            <Route path="org-admin" element={<OrgAdminPage />} />
          </>
        ) : null}
        <Route path="guides/dispute-workflow" element={<DisputeWorkflowGuidePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      {featureFlags.enableClientPortal ? (
        <Route path="portal/*" element={<PortalRoutes />} />
      ) : null}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
