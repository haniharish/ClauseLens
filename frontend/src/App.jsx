import { Navigate, Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useApp } from './context/AppContext';
import DashboardLayout from './components/layout/DashboardLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AnalyzeDocument from './pages/AnalyzeDocument';
import AnalysisResults from './pages/AnalysisResults';
import MyDocuments from './pages/MyDocuments';
import RiskAnalysis from './pages/RiskAnalysis';
import PolicyMonitoring from './pages/PolicyMonitoring';
import VersionHistory from './pages/VersionHistory';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useApp();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#141725',
            color: '#F1F5F9',
            border: '1px solid rgba(155, 122, 255, 0.3)',
            fontSize: '13px',
          },
        }}
      />

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="analyze" element={<AnalyzeDocument />} />
          <Route path="analysis/:id" element={<AnalysisResults />} />
          <Route path="documents" element={<MyDocuments />} />
          <Route path="risk-analysis" element={<RiskAnalysis />} />
          <Route path="monitoring" element={<PolicyMonitoring />} />
          <Route path="version-history" element={<VersionHistory />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </>
  );
}
