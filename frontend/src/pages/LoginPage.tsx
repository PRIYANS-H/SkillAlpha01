import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GraduationCap, ArrowRight, Lock, Mail } from 'lucide-react';
import { apiClient } from '../api/client';

export const LoginPage: React.FC<{ onLoginSuccess?: (user: any) => void }> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res: any = await apiClient.post('/auth/login', { email, password });
      localStorage.setItem('skillalpha_token', res.access_token);
      if (onLoginSuccess) onLoginSuccess(res.user);
      navigate('/roadmap/active');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full pt-28 pb-16 bg-surface min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-lg p-6 sm:p-8">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-primary-container text-on-primary flex items-center justify-center mx-auto mb-3">
            <GraduationCap className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-extrabold text-on-surface">Welcome Back</h1>
          <p className="text-xs text-on-surface-variant mt-1">Sign in to resume your personalized learning sequence.</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-error-container text-on-error-container text-xs font-semibold">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-on-surface-variant uppercase mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="learner@skillalpha.com"
              className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-on-surface-variant uppercase mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full flex items-center justify-center gap-2 h-11 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm"
          >
            <span>{submitting ? 'Signing in...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-4 pt-3 border-t border-outline-variant/30 flex flex-col items-center gap-2">
          <button
            type="button"
            onClick={async () => {
              setSubmitting(true);
              try {
                const res: any = await apiClient.post('/auth/login', {
                  email: 'learner@skillalpha.com',
                  password: 'learner123'
                });
                localStorage.setItem('skillalpha_token', res.access_token);
                if (onLoginSuccess) onLoginSuccess(res.user);
                navigate('/learn');
              } catch (err: any) {
                setError('Demo login failed');
              } finally {
                setSubmitting(false);
              }
            }}
            className="w-full py-2.5 rounded-xl bg-surface-container-low text-primary text-xs font-bold border border-outline-variant/60 hover:bg-surface-container transition-colors"
          >
            ⚡ Try Interactive Demo Account
          </button>
        </div>

        <div className="mt-4 text-center text-xs text-on-surface-variant">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-primary hover:underline">
            Register now
          </Link>
        </div>
      </div>
    </div>
  );
};
