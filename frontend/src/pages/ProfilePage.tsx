import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Save, Github, Sun, Moon, RefreshCw } from 'lucide-react';
import { apiClient } from '../api/client';
import { useTheme } from '../hooks/useTheme';
import { useToast } from '../components/ui/Toast';
import { PageSkeleton } from '../components/ui/Skeleton';

const FORMATS = [
  { key: 'VIDEO', label: 'Video' },
  { key: 'DOCUMENTATION', label: 'Docs' },
  { key: 'PRACTICE', label: 'Practice' },
  { key: 'PROJECT', label: 'Projects' },
  { key: 'ARTICLE', label: 'Articles' },
];

const inputClass =
  'w-full h-11 px-3.5 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm text-on-surface focus:outline-none focus:border-primary';
const labelClass = 'block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2';

export const ProfilePage: React.FC = () => {
  const toast = useToast();
  const { theme, toggleTheme } = useTheme();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [goal, setGoal] = useState('');
  const [hours, setHours] = useState(10);
  const [duration, setDuration] = useState(12);
  const [github, setGithub] = useState('');
  const [preferences, setPreferences] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res: any = await apiClient.get('/users/me');
        setProfile(res);
        setGoal(res.goal || '');
        setHours(res.available_hours || 10);
        setDuration(res.duration_weeks || 12);
        setGithub(res.github_username || '');
        setPreferences(Array.isArray(res.learning_preferences) ? res.learning_preferences : []);
      } catch (err: any) {
        toast.error(err.message || 'Could not load your profile.');
      } finally {
        setLoading(false);
      }
    })();
  }, [toast]);

  const hoursValid = Number.isFinite(hours) && hours >= 1 && hours <= 80;
  const durationValid = Number.isFinite(duration) && duration >= 1 && duration <= 52;
  const paceChanged = !!profile && (hours !== (profile.available_hours || 10) || duration !== (profile.duration_weeks || 12) || goal !== (profile.goal || ''));

  const togglePreference = (key: string) => {
    setPreferences((prev) => (prev.includes(key) ? prev.filter((p) => p !== key) : [...prev, key]));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hoursValid || !durationValid) {
      toast.error('Please fix the highlighted fields first.');
      return;
    }
    setSaving(true);
    try {
      await apiClient.patch('/users/me', {
        goal: goal.trim(),
        available_hours: hours,
        duration_weeks: duration,
        github_username: github.trim(),
        learning_preferences: preferences,
      });
      setProfile({ ...profile, goal: goal.trim(), available_hours: hours, duration_weeks: duration });
      toast.success('Profile saved.');
    } catch (err: any) {
      toast.error(err.message || 'Could not save your profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <PageSkeleton variant="article" label="Loading your profile" />;

  const displayName = profile?.full_name || profile?.email?.split('@')[0] || 'Learner';

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <div className="mb-6">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">Account & Preferences</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface">Profile</h1>
        </div>

        {/* Account */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 sm:p-6 shadow-sm mb-6 flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-primary text-on-primary flex items-center justify-center font-extrabold text-xl flex-shrink-0">
            {displayName[0].toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-base font-bold text-on-surface truncate">{displayName}</div>
            <div className="text-xs text-on-surface-variant truncate">{profile?.email}</div>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-container-low text-on-surface text-xs font-semibold hover:bg-surface-container transition-colors whitespace-nowrap"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {theme === 'dark' ? 'Light theme' : 'Dark theme'}
          </button>
        </div>

        <form onSubmit={handleSave} className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 sm:p-8 shadow-sm space-y-6">
          <div>
            <label htmlFor="profile-goal" className={labelClass}>Learning goal</label>
            <input id="profile-goal" type="text" value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="e.g. Become a Machine Learning Engineer" className={inputClass} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label htmlFor="profile-hours" className={labelClass}>Hours per week</label>
              <input
                id="profile-hours"
                type="number"
                min={1}
                max={80}
                value={Number.isFinite(hours) ? hours : ''}
                onChange={(e) => setHours(e.target.value === '' ? NaN : Number(e.target.value))}
                aria-invalid={!hoursValid}
                className={`${inputClass} ${hoursValid ? '' : 'border-error'}`}
              />
              <p className={`text-[11px] mt-1.5 ${hoursValid ? 'text-on-surface-variant' : 'text-error font-semibold'}`}>
                {hoursValid ? `About ${(hours / 5).toFixed(1)} hrs on each of 5 study days` : 'Enter between 1 and 80 hours.'}
              </p>
            </div>

            <div>
              <label htmlFor="profile-duration" className={labelClass}>Target duration (weeks)</label>
              <input
                id="profile-duration"
                type="number"
                min={1}
                max={52}
                value={Number.isFinite(duration) ? duration : ''}
                onChange={(e) => setDuration(e.target.value === '' ? NaN : Number(e.target.value))}
                aria-invalid={!durationValid}
                className={`${inputClass} ${durationValid ? '' : 'border-error'}`}
              />
              {!durationValid && <p className="text-[11px] mt-1.5 text-error font-semibold">Enter between 1 and 52 weeks.</p>}
            </div>
          </div>

          <div>
            <span className={labelClass}>Preferred formats</span>
            <div className="flex flex-wrap gap-2">
              {FORMATS.map(({ key, label }) => {
                const active = preferences.includes(key);
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => togglePreference(key)}
                    aria-pressed={active}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                      active ? 'bg-primary text-on-primary shadow-sm' : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                    }`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label htmlFor="profile-github" className={`${labelClass} flex items-center gap-1.5`}>
              <Github className="w-4 h-4 text-on-surface" /> GitHub username (optional)
            </label>
            <input id="profile-github" type="text" value={github} onChange={(e) => setGithub(e.target.value)} placeholder="e.g. octocat" className={inputClass} />
          </div>

          {paceChanged && (
            <div className="p-3.5 rounded-xl bg-surface-container-low text-xs text-on-surface-variant flex flex-wrap items-center justify-between gap-3">
              <span>Goal and pace changes apply to your next roadmap. Your current roadmap keeps its schedule.</span>
              <Link to="/create" className="inline-flex items-center gap-1.5 font-bold text-primary hover:underline whitespace-nowrap">
                <RefreshCw className="w-3.5 h-3.5" /> Rebuild roadmap
              </Link>
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full flex items-center justify-center gap-2 h-11 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm disabled:opacity-60"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving…' : 'Save changes'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
