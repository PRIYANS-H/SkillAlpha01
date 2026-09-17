import React, { useEffect, useState } from 'react';
import { User, Settings, Save, Github, Clock, Award } from 'lucide-react';
import { apiClient } from '../api/client';

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [goal, setGoal] = useState('');
  const [hours, setHours] = useState(12);
  const [duration, setDuration] = useState(12);
  const [github, setGithub] = useState('');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      const res: any = await apiClient.get('/users/me');
      setProfile(res);
      setGoal(res.goal || '');
      setHours(res.available_hours || 12);
      setDuration(res.duration_weeks || 12);
      setGithub(res.github_username || '');
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMsg(null);
    try {
      await apiClient.patch('/users/me', {
        goal,
        available_hours: hours,
        duration_weeks: duration,
        github_username: github
      });
      setMsg('Profile and learning constraints updated successfully!');
    } catch (err: any) {
      setMsg(err.message || 'Error updating profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">Account & Preferences</span>
          <h1 className="text-3xl font-extrabold text-on-surface">Learner Profile</h1>
        </div>

        {msg && (
          <div className="mb-6 p-4 rounded-xl bg-primary-fixed/40 text-primary text-xs font-semibold">
            {msg}
          </div>
        )}

        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
              Email Address
            </label>
            <input
              type="text"
              disabled
              value={profile?.email || ''}
              className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/40 bg-surface-container-low text-xs text-on-surface-variant cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
              Primary Goal Objective
            </label>
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                Available Hours / Week
              </label>
              <input
                type="number"
                value={hours}
                onChange={(e) => setHours(Number(e.target.value))}
                className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                Target Duration (Weeks)
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Github className="w-4 h-4 text-on-surface" /> GitHub Username (Optional)
            </label>
            <input
              type="text"
              value={github}
              onChange={(e) => setGithub(e.target.value)}
              placeholder="e.g. octocat"
              className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 text-xs text-on-surface"
            />
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full flex items-center justify-center gap-2 h-11 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
          </button>
        </div>

      </div>
    </div>
  );
};
