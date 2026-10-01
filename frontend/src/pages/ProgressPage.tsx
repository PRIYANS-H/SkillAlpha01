import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Award, CheckCircle2, TrendingUp, BookOpen, FileCheck, ShieldCheck, Sparkles, RefreshCw } from 'lucide-react';
import { apiClient } from '../api/client';
import { UserSkill } from '../types';

export const ProgressPage: React.FC = () => {
  const [userSkills, setUserSkills] = useState<UserSkill[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const prof: any = await apiClient.get('/users/me');
      setProfile(prof);

      const skillsRes: any = await apiClient.get('/users/me/skills');
      if (skillsRes && Array.isArray(skillsRes)) {
        setUserSkills(skillsRes);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProgress();
  }, []);

  const totalEvidence = userSkills.reduce((acc, s) => acc + (s.evidence_count || 0), 0);
  const masteredCount = userSkills.filter(s => s.status === 'MASTERED' || s.status === 'STRONG').length;

  if (loading) {
    return (
      <div className="w-full pt-28 pb-16 flex items-center justify-center min-h-screen text-on-surface-variant">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-primary" />
          <span className="text-sm font-semibold">Loading your verified mastery profile...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">
            Learning Evidence & Mastery Profile
          </span>
          <h1 className="text-3xl font-extrabold text-on-surface">Demonstrated Skill Progress</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Progress in SkillAlpha is measured strictly by verified evidence, assessments, and completed practical tasks.
          </p>
        </div>

        {/* Top Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Active Streak</div>
            <div className="text-2xl font-extrabold text-primary flex items-center gap-1.5">
              <span>{totalEvidence > 0 ? '1 Day' : '0 Days'}</span>
              <Sparkles className="w-5 h-5 text-secondary-container" />
            </div>
            <span className="text-[11px] text-on-surface-variant">Daily learning habit active</span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Weekly Commitment</div>
            <div className="text-2xl font-extrabold text-on-surface">
              {profile?.available_hours || 10} hrs/wk
            </div>
            <span className="text-[11px] text-primary font-semibold">
              ~{((profile?.available_hours || 10) / 5.0).toFixed(1)} hrs/day target
            </span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Verified Evidence</div>
            <div className="text-2xl font-extrabold text-on-surface">
              {totalEvidence} Points
            </div>
            <span className="text-[11px] text-on-surface-variant">Checkpoints & completed tasks</span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Bypassed Material</div>
            <div className="text-2xl font-extrabold text-primary">
              ~{masteredCount * 6} Hours
            </div>
            <span className="text-[11px] text-primary font-semibold">Skipped redundant topics</span>
          </div>
        </div>

        {/* Skill Mastery Graph Table */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6 mb-8">
          <h2 className="text-base font-bold text-on-surface mb-4">Skill Gap & Baseline Breakdown</h2>
          
          {userSkills.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="w-10 h-10 text-outline mx-auto mb-3" />
              <h3 className="text-base font-bold text-on-surface mb-1">No verified skills recorded yet</h3>
              <p className="text-xs text-on-surface-variant mb-6 max-w-sm mx-auto">
                Complete onboarding and start your first daily session to track skill calibrations and evidence.
              </p>
              <Link
                to="/create"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs"
              >
                Create Learning Path
              </Link>
            </div>
          ) : (
            <div className="space-y-6">
              {userSkills.map((sk) => {
                const pct = Math.round(sk.skill_score * 100);
                return (
                  <div key={sk.id} className="p-4 rounded-xl bg-surface-container-low/50 border border-outline-variant/40">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-on-surface">{sk.skill_name}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          sk.status === 'MASTERED' ? 'bg-primary-fixed text-on-primary-fixed' :
                          sk.status === 'STRONG' ? 'bg-primary-fixed/40 text-primary' :
                          sk.status === 'NEEDS_REINFORCEMENT' ? 'bg-secondary-fixed text-on-secondary-container' :
                          'bg-surface-container text-on-surface-variant'
                        }`}>
                          {sk.status}
                        </span>
                      </div>

                      <div className="text-xs font-semibold text-on-surface">
                        Score: <span className="text-primary font-bold">{pct}%</span> • Confidence: {(sk.confidence_score * 100).toFixed(0)}%
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-2.5 w-full bg-surface-container-highest rounded-full overflow-hidden mb-3">
                      <div 
                        className={`h-full rounded-full transition-all ${
                          sk.status === 'MASTERED' || sk.status === 'STRONG' ? 'bg-primary-container' : 'bg-secondary-container'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>

                    {/* Evidence Record */}
                    <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-2 border-t border-outline-variant/30">
                      <span className="flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-primary" />
                        Evidence Logs: {sk.evidence_count} checkpoints recorded
                      </span>
                      <span>Last benchmarked: Today</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
