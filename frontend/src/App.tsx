import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/layout/Header';
import { LandingPage } from './pages/LandingPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { TodayPage } from './pages/TodayPage';
import { ResourcesPage } from './pages/ResourcesPage';
import { ProgressPage } from './pages/ProgressPage';
import { SavedPage } from './pages/SavedPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminPage } from './pages/AdminPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { apiClient } from './api/client';

const queryClient = new QueryClient();

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    const token = localStorage.getItem('skillalpha_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const res: any = await apiClient.get('/auth/me');
      setUser(res);
    } catch (err) {
      localStorage.removeItem('skillalpha_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('skillalpha_token');
    setUser(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-surface flex flex-col font-sans">
          <Header user={user} onLogout={handleLogout} />

          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage onLoginSuccess={(u) => setUser(u)} />} />
              <Route path="/register" element={<RegisterPage onLoginSuccess={(u) => setUser(u)} />} />

              {/* Onboarding */}
              <Route path="/create" element={<OnboardingPage />} />

              {/* App Application Routes */}
              <Route path="/roadmap/:id" element={<RoadmapPage />} />
              <Route path="/learn" element={<TodayPage />} />
              <Route path="/learn/:taskId" element={<TodayPage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/resources/:id" element={<ResourcesPage />} />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="/saved" element={<SavedPage />} />
              <Route path="/profile" element={<ProfilePage />} />

              {/* Admin Portal */}
              <Route path="/admin" element={<AdminPage />} />

              {/* Catch-all fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <footer className="w-full bg-surface-container-lowest border-t border-outline-variant/40 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-on-surface-variant">
              <div className="flex items-center gap-2 font-bold text-on-surface">
                <span>SkillAlpha</span>
                <span>© 2026 SkillAlpha Intelligence Inc.</span>
              </div>
              <div className="flex items-center gap-6">
                <span>Everything you need to learn. In the right order.</span>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
};
