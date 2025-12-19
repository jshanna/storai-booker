/**
 * Main App component with routing and providers.
 */

import { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { ErrorBoundary, FullPageSpinner } from '@/components/shared';
import { ProtectedRoute } from '@/components/auth';
import { Toaster } from '@/components/ui/toaster';
import { useAuthInit } from '@/lib/hooks/useAuth';
import { useRouteAnnouncer } from '@/lib/hooks/useRouteAnnouncer';
import { AnnouncerProvider } from '@/lib/contexts/AnnouncerContext';
import { HomePage } from '@/pages';

// Lazy load pages for code splitting
const GeneratePage = lazy(() => import('@/pages/GeneratePage').then(m => ({ default: m.GeneratePage })));
const LibraryPage = lazy(() => import('@/pages/LibraryPage').then(m => ({ default: m.LibraryPage })));
const ReaderPage = lazy(() => import('@/pages/ReaderPage').then(m => ({ default: m.ReaderPage })));
const SettingsPage = lazy(() => import('@/pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));
const LoginPage = lazy(() => import('@/pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then(m => ({ default: m.ProfilePage })));
const OAuthCallbackPage = lazy(() => import('@/pages/OAuthCallbackPage').then(m => ({ default: m.OAuthCallbackPage })));
const SharedReaderPage = lazy(() => import('@/pages/SharedReaderPage').then(m => ({ default: m.SharedReaderPage })));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

/**
 * App content component with auth initialization and route announcements.
 */
function AppContent() {
  // Initialize auth on app mount
  useAuthInit();
  // Announce route changes to screen readers
  useRouteAnnouncer();

  return (
    <Layout>
      <Suspense fallback={<FullPageSpinner text="Loading..." />}>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/auth/callback" element={<OAuthCallbackPage />} />
          <Route path="/shared/:token" element={<SharedReaderPage />} />

          {/* Protected routes */}
          <Route
            path="/generate"
            element={
              <ProtectedRoute>
                <GeneratePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/library"
            element={
              <ProtectedRoute>
                <LibraryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reader/:id"
            element={
              <ProtectedRoute>
                <ReaderPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AnnouncerProvider>
            <AppContent />
          </AnnouncerProvider>
        </BrowserRouter>
        <Toaster />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
