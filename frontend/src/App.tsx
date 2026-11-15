import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/layout/Header';
import { MobileTabBar } from './components/layout/MobileTabBar';
import { ToastProvider } from './components/ui/Toast';
import { SkillAlphaLogo } from './components/brand/SkillAlphaLogo';
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
import { supabase } from './api/supabase';
import { apiClient } from './api/client';

const queryClient = new QueryClient();

const PENDING_ROADMAP_KEY = 'skillalpha_pending_roadmap';

/**
 * Sends signed-out visitors to /login and brings them back afterwards. The Supabase session
 * is the source of truth: the backend user sync can lag a moment behind a fresh sign-in.
 */
const RequireAuth: React.FC<{ user: any; loading: boolean; children: React.ReactElement }> = ({ user, loading, children }) => {
  const location = useLocation();
  const [sessionState, setSessionState] = useState<'checking' | 'yes' | 'no'>(user ? 'yes' : 'checking');

  useEffect(() => {
    if (user) {
      setSessionState('yes');
      return;
    }
    let cancelled = false;
    supabase.auth.getSession()
      .then(({ data: { session } }) => { if (!cancelled) setSessionState(session ? 'yes' : 'no'); })
      .catch(() => { if (!cancelled) setSessionState('no'); });
    return () => { cancelled = true; };
  }, [user]);

  if (loading || sessionState === 'checking') {
    return (
      <div className="w-full pt-28 pb-16 flex items-center justify-center min-h-screen text-sm font-semibold text-on-surface-variant">
        Checking your session...
      </div>
    );
  }
  if (sessionState === 'no') {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return children;
};

/** Each navigation starts at the top of the new page. */
const ScrollToTop: React.FC = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

const APP_SECTIONS = ['/roadmap', '/learn', '/resources', '/progress', '/saved', '/profile', '/admin'];

/** Bottom tab bar for signed-in learners on phones, only inside the app sections. */
const AppTabBar: React.FC<{ user: any }> = ({ user }) => {
  const { pathname } = useLocation();
  if (!user || !APP_SECTIONS.some((p) => pathname.startsWith(p))) return null;
  return <MobileTabBar />;
};

/**
 * Onboarding stores the roadmap request before sign-up. Email login/register submit it
 * themselves, but Google OAuth returns to the site root, so finish it here once signed in.
 */
const PendingRoadmapSubmitter: React.FC<{ user: any }> = ({ user }) => {
  const navigate = useNavigate();
  useEffect(() => {
    if (!user) return;
    const pending = localStorage.getItem(PENDING_ROADMAP_KEY);
    if (!pending) return;
    localStorage.removeItem(PENDING_ROADMAP_KEY);
    (async () => {
      try {
        const rm: any = await apiClient.post('/roadmaps', JSON.parse(pending));
        navigate(`/roadmap/${rm.id}`);
      } catch (err) {
        console.error('Failed to submit pending roadmap', err);
      }
    })();
  }, [user, navigate]);
  return null;
};

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const syncBackendUser = async (accessToken?: string) => {
    if (accessToken) {
      localStorage.setItem('skillalpha_token', accessToken);
    }
    try {
      const res: any = await apiClient.get('/auth/me');
      setUser(res);
    } catch (err) {
      console.warn('Could not sync user with backend:', err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 1. Initial session check
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.access_token) {
        syncBackendUser(session.access_token);
      } else {
        setLoading(false);
      }
    });

    // 2. Synchronize with Supabase session changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        localStorage.setItem('skillalpha_token', session.access_token);
        if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
          syncBackendUser(session.access_token);
        }
      } else if (event === 'SIGNED_OUT') {
        localStorage.removeItem('skillalpha_token');
        setUser(null);
        setLoading(false);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {
      console.error('Error signing out of Supabase:', e);
    } finally {
      localStorage.removeItem('skillalpha_token');
      setUser(null);
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
      <Router>
        <ScrollToTop />
        <PendingRoadmapSubmitter user={user} />
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
              <Route path="/roadmap/:id" element={<RequireAuth user={user} loading={loading}><RoadmapPage /></RequireAuth>} />
              <Route path="/learn" element={<RequireAuth user={user} loading={loading}><TodayPage /></RequireAuth>} />
              <Route path="/learn/:taskId" element={<RequireAuth user={user} loading={loading}><TodayPage /></RequireAuth>} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/resources/:id" element={<ResourcesPage />} />
              <Route path="/progress" element={<RequireAuth user={user} loading={loading}><ProgressPage /></RequireAuth>} />
              <Route path="/saved" element={<RequireAuth user={user} loading={loading}><SavedPage /></RequireAuth>} />
              <Route path="/profile" element={<RequireAuth user={user} loading={loading}><ProfilePage /></RequireAuth>} />

              {/* Admin Portal */}
              <Route path="/admin" element={<RequireAuth user={user} loading={loading}><AdminPage /></RequireAuth>} />

              {/* Catch-all fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <footer className={`w-full bg-surface-container-lowest border-t border-outline-variant/40 py-8 ${user ? 'pb-24 md:pb-8' : ''}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-on-surface-variant">
              <div className="flex items-center gap-3">
                <SkillAlphaLogo size="sm" variant="horizontal" />
                <span className="text-[11px] text-on-surface-variant font-normal">© 2026 SkillAlpha Intelligence Inc.</span>
              </div>
              <div className="flex items-center gap-6">
                <span>Everything you need to learn. In the right order.</span>
              </div>
            </div>
          </footer>
          <AppTabBar user={user} />
        </div>
      </Router>
      </ToastProvider>
    </QueryClientProvider>
  );
};
