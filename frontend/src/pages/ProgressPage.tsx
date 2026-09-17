import React, { useEffect, useState } from 'react';
import { Award, CheckCircle2, TrendingUp, BookOpen, FileCheck, ShieldCheck, Sparkles } from 'lucide-react';
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
      const roadmaps: any = await apiClient.get('/roadmaps');

      // Fetch user skills from API or extract active roadmap skills
      if (roadmaps && roadmaps.length > 0) {
        const rm = roadmaps[0];
        const extractedSkills: UserSkill[] = [];
        
        // Mock/Extracted verified evidence items
        extractedSkills.push({
          id: '1',
          skill_id: 's1',
          skill_name: 'Python Architecture',
          skill_score: 0.88,
          confidence_score: 0.90,
          status: 'MASTERED',
          evidence_count: 4,
          last_assessed_at: new Date().toISOString()
        });
        extractedSkills.push({
          id: '2',
          skill_id: 's2',
          skill_name: 'SQL & Analytical Queries',
          skill_score: 0.71,
          confidence_score: 0.85,
          status: 'STRONG',
          evidence_count: 3,
          last_assessed_at: new Date().toISOString()
        });
        extractedSkills.push({
          id: '3',
          skill_id: 's3',
          skill_name: 'Applied Statistics',
          skill_score: 0.63,
          confidence_score: 0.75,
          status: 'NEEDS_REINFORCEMENT',
          evidence_count: 2,
          last_assessed_at: new Date().toISOString()
        });
        extractedSkills.push({
          id: '4',
          skill_id: 's4',
          skill_name: 'Machine Learning Foundations',
          skill_score: 0.41,
          confidence_score: 0.60,
          status: 'NEEDS_REINFORCEMENT',
          evidence_count: 1,
          last_assessed_at: new Date().toISOString()
        });
        extractedSkills.push({
          id: '5',
          skill_id: 's5',
          skill_name: 'Model Validation & Split Hygiene',
          skill_score: 0.35,
          confidence_score: 0.50,
          status: 'MISSING',
          evidence_count: 0,
          last_assessed_at: new Date().toISOString()
        });

        setUserSkills(extractedSkills);
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
              <span>5 Days</span>
              <Sparkles className="w-5 h-5 text-secondary-container" />
            </div>
            <span className="text-[11px] text-on-surface-variant">Daily learning habit active</span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Weekly Commitment</div>
            <div className="text-2xl font-extrabold text-on-surface">
              {profile?.available_hours || 12} hrs/wk
            </div>
            <span className="text-[11px] text-primary font-semibold">8.5 hrs logged this week</span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Verified Evidence</div>
            <div className="text-2xl font-extrabold text-on-surface">
              10 Points
            </div>
            <span className="text-[11px] text-on-surface-variant">4 resources + 3 quizzes + 3 labs</span>
          </div>

          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
            <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Bypassed Material</div>
            <div className="text-2xl font-extrabold text-primary">
              ~18 Hours
            </div>
            <span className="text-[11px] text-primary font-semibold">Skipped redundant syntax</span>
          </div>
        </div>

        {/* Skill Mastery Graph Table */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6 mb-8">
          <h2 className="text-base font-bold text-on-surface mb-4">Skill Gap & Baseline Breakdown</h2>
          
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
        </div>

      </div>
    </div>
  );
};
