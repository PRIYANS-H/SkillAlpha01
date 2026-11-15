import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Flame, Clock, CheckCircle2, ShieldCheck, Target, ArrowRight, Trophy } from 'lucide-react';
import { apiClient } from '../api/client';
import { UserSkill } from '../types';
import { PageSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';
import { parseDueDate } from '../utils/dates';

interface ActivityDay {
  date: string;
  minutes: number;
  tasks: number;
  quizzes: number;
}

interface Activity {
  streak_days: number;
  longest_streak: number;
  active_days: number;
  total_minutes: number;
  tasks_completed: number;
  quizzes_taken: number;
  quizzes_passed: number;
  days: ActivityDay[];
}

const STATUS_META: Record<string, { label: string; chip: string; bar: string }> = {
  MASTERED: { label: 'Mastered', chip: 'bg-primary-fixed text-on-primary-fixed', bar: 'bg-primary-container' },
  STRONG: { label: 'Strong', chip: 'bg-primary-fixed/50 text-primary', bar: 'bg-primary-container' },
  NEEDS_REINFORCEMENT: { label: 'Needs practice', chip: 'bg-secondary-fixed text-on-secondary-container', bar: 'bg-secondary-container' },
  MISSING: { label: 'Gap', chip: 'bg-surface-container text-on-surface-variant', bar: 'bg-outline' },
};
const STATUS_ORDER = ['NEEDS_REINFORCEMENT', 'MISSING', 'STRONG', 'MASTERED'];

const formatHours = (minutes: number): string => {
  if (minutes < 60) return `${minutes} min`;
  const hours = minutes / 60;
  return `${hours >= 10 ? Math.round(hours) : hours.toFixed(1)} hrs`;
};

const relativeDay = (iso?: string | null): string => {
  if (!iso) return 'Not assessed yet';
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return 'Not assessed yet';
  const days = Math.floor((Date.now() - then.getTime()) / 86400000);
  if (days <= 0) return 'Updated today';
  if (days === 1) return 'Updated yesterday';
  return `Updated ${days} days ago`;
};

const heatLevel = (day: ActivityDay): string => {
  const load = day.minutes + (day.tasks + day.quizzes) * 20;
  if (load === 0) return 'bg-surface-container-high';
  if (load < 30) return 'bg-primary-container/40';
  if (load < 90) return 'bg-primary-container/70';
  return 'bg-primary-container';
};

export const ProgressPage: React.FC = () => {
  const toast = useToast();
  const [userSkills, setUserSkills] = useState<UserSkill[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [activity, setActivity] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'GAPS' | 'STRONG'>('ALL');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [prof, skillsRes, act] = await Promise.all([
          apiClient.get('/users/me') as Promise<any>,
          apiClient.get('/users/me/skills') as Promise<any>,
          // Older backends do not have this endpoint; the page still works without it
          (apiClient.get('/users/me/activity') as Promise<any>).catch(() => null),
        ]);
        if (cancelled) return;
        setProfile(prof);
        setUserSkills(Array.isArray(skillsRes) ? skillsRes : []);
        setActivity(
          act && Array.isArray(act.days)
            ? {
                ...act,
                quizzes_taken: act.quizzes_taken || 0,
                quizzes_passed: act.quizzes_passed || 0,
                days: act.days.map((d: any) => ({ date: d.date, minutes: d.minutes || 0, tasks: d.tasks || 0, quizzes: d.quizzes || 0 })),
              }
            : null
        );
      } catch (err: any) {
        if (!cancelled) toast.error(err.message || 'Could not load your progress.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [toast]);

  const counts = useMemo(() => {
    const c: Record<string, number> = { MASTERED: 0, STRONG: 0, NEEDS_REINFORCEMENT: 0, MISSING: 0 };
    userSkills.forEach((s) => {
      c[s.status] = (c[s.status] || 0) + 1;
    });
    return c;
  }, [userSkills]);

  const sortedSkills = useMemo(() => {
    const visible = userSkills.filter((s) => {
      if (filter === 'GAPS') return s.status === 'NEEDS_REINFORCEMENT' || s.status === 'MISSING';
      if (filter === 'STRONG') return s.status === 'MASTERED' || s.status === 'STRONG';
      return true;
    });
    return [...visible].sort(
      (a, b) => STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status) || b.skill_score - a.skill_score
    );
  }, [userSkills, filter]);

  if (loading) return <PageSkeleton variant="list" label="Loading your progress" />;

  const total = userSkills.length;
  const solid = counts.MASTERED + counts.STRONG;
  const readiness = total ? Math.round((userSkills.reduce((acc, s) => acc + s.skill_score, 0) / total) * 100) : 0;
  const totalEvidence = userSkills.reduce((acc, s) => acc + (s.evidence_count || 0), 0);
  const streak = activity?.streak_days ?? 0;
  const weeklyTargetMin = (profile?.available_hours || 10) * 60;
  const last7 = activity?.days.slice(-7) ?? [];
  const weekMinutes = last7.reduce((acc, d) => acc + d.minutes, 0);
  const weekPct = Math.min(100, Math.round((weekMinutes / weeklyTargetMin) * 100));

  const statCards = [
    {
      label: 'Study streak',
      value: `${streak} ${streak === 1 ? 'day' : 'days'}`,
      hint: activity && activity.longest_streak > streak ? `Best: ${activity.longest_streak} days` : streak > 0 ? 'Keep it going today' : 'Complete a task to start one',
      icon: Flame,
      accent: streak > 0 ? 'text-secondary-container' : 'text-outline',
    },
    {
      label: 'This week',
      value: formatHours(weekMinutes),
      hint: `${weekPct}% of your ${profile?.available_hours || 10} hrs/week goal`,
      icon: Clock,
      accent: 'text-primary',
      progress: weekPct,
    },
    {
      label: 'Tasks completed',
      value: String(activity?.tasks_completed ?? 0),
      hint: activity ? `${activity.quizzes_passed}/${activity.quizzes_taken} quizzes passed` : 'Across your roadmaps',
      icon: CheckCircle2,
      accent: 'text-primary',
    },
    {
      label: 'Goal readiness',
      value: `${readiness}%`,
      hint: total ? `${solid} of ${total} skills solid` : 'Build a roadmap to begin',
      icon: Target,
      accent: 'text-primary',
      progress: readiness,
    },
  ];

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">Your progress</span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface">
              {profile?.goal || 'Skill progress'}
            </h1>
            <p className="text-sm text-on-surface-variant mt-1 max-w-2xl">
              Scores only move when you prove it: quizzes, diagnostics and completed tasks.
            </p>
          </div>
          {total > 0 && (
            <Link
              to="/learn"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all"
            >
              Continue learning <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
          {statCards.map(({ label, value, hint, icon: Icon, accent, progress }) => (
            <div key={label} className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-4 sm:p-5 shadow-sm">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wide">{label}</span>
                <Icon className={`w-4 h-4 ${accent}`} />
              </div>
              <div className="text-xl sm:text-2xl font-extrabold text-on-surface">{value}</div>
              {progress !== undefined && (
                <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden mt-2">
                  <div className="h-full rounded-full bg-primary-container transition-all" style={{ width: `${progress}%` }} />
                </div>
              )}
              <span className="text-[11px] text-on-surface-variant block mt-1.5">{hint}</span>
            </div>
          ))}
        </div>

        {total === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6 text-center py-14">
            <BookOpen className="w-10 h-10 text-outline mx-auto mb-3" />
            <h2 className="text-base font-bold text-on-surface mb-1">No skills tracked yet</h2>
            <p className="text-xs text-on-surface-variant mb-6 max-w-sm mx-auto">
              Tell us your goal and what you already know. We'll map your skills and show your progress here.
            </p>
            <Link
              to="/create"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs"
            >
              Build my learning path <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left column: activity + mix */}
            <div className="lg:col-span-4 space-y-6">
              {activity && (
                <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-bold text-on-surface">Last 4 weeks</h2>
                    <span className="text-[11px] text-on-surface-variant">
                      {(() => {
                        const n = activity.days.filter((d) => d.minutes + d.tasks + d.quizzes > 0).length;
                        return `${n} active day${n === 1 ? '' : 's'}`;
                      })()}
                    </span>
                  </div>
                  <div className="grid grid-cols-7 gap-1.5" role="img" aria-label="Daily study activity for the last 28 days">
                    {activity.days.map((d) => {
                      const date = parseDueDate(d.date);
                      const label = `${date ? date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : d.date}: ${d.minutes} min, ${d.tasks} task${d.tasks === 1 ? '' : 's'}, ${d.quizzes} quiz${d.quizzes === 1 ? '' : 'zes'}`;
                      return <div key={d.date} title={label} className={`aspect-square rounded-md ${heatLevel(d)}`} />;
                    })}
                  </div>
                  <div className="flex items-center justify-between mt-3 text-[10px] text-on-surface-variant">
                    <span>4 weeks ago</span>
                    <span className="flex items-center gap-1">
                      Less
                      <i className="w-2.5 h-2.5 rounded-sm bg-surface-container-high inline-block" />
                      <i className="w-2.5 h-2.5 rounded-sm bg-primary-container/40 inline-block" />
                      <i className="w-2.5 h-2.5 rounded-sm bg-primary-container/70 inline-block" />
                      <i className="w-2.5 h-2.5 rounded-sm bg-primary-container inline-block" />
                      More
                    </span>
                    <span>Today</span>
                  </div>
                  <div className="mt-4 pt-3 border-t border-outline-variant/40 text-xs text-on-surface-variant flex items-center justify-between">
                    <span>Total study time</span>
                    <strong className="text-on-surface">{formatHours(activity.total_minutes)}</strong>
                  </div>
                </section>
              )}

              <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-5">
                <h2 className="text-sm font-bold text-on-surface mb-3">Skill mix</h2>
                <div className="flex h-3 w-full rounded-full overflow-hidden bg-surface-container-highest mb-4">
                  {(['MASTERED', 'STRONG', 'NEEDS_REINFORCEMENT', 'MISSING'] as const).map((status) =>
                    counts[status] ? (
                      <div
                        key={status}
                        className={`${STATUS_META[status].bar} ${status === 'STRONG' ? 'opacity-60' : ''}`}
                        style={{ width: `${(counts[status] / total) * 100}%` }}
                      />
                    ) : null
                  )}
                </div>
                <ul className="space-y-2 text-xs">
                  {(['MASTERED', 'STRONG', 'NEEDS_REINFORCEMENT', 'MISSING'] as const).map((status) => (
                    <li key={status} className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-on-surface-variant">
                        <i className={`w-2.5 h-2.5 rounded-sm inline-block ${STATUS_META[status].bar} ${status === 'STRONG' ? 'opacity-60' : ''}`} />
                        {STATUS_META[status].label}
                      </span>
                      <strong className="text-on-surface">{counts[status]}</strong>
                    </li>
                  ))}
                </ul>
                <div className="mt-4 pt-3 border-t border-outline-variant/40 text-xs text-on-surface-variant flex items-center gap-2">
                  <Trophy className="w-3.5 h-3.5 text-primary" />
                  {totalEvidence} verified checkpoint{totalEvidence === 1 ? '' : 's'} recorded
                </div>
              </section>
            </div>

            {/* Right column: skills */}
            <section className="lg:col-span-8 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-5 sm:p-6">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h2 className="text-base font-bold text-on-surface">Skills on your path</h2>
                <div className="flex items-center gap-1 p-1 rounded-lg bg-surface-container-low text-xs font-semibold" role="tablist" aria-label="Filter skills">
                  {([['ALL', `All (${total})`], ['GAPS', `Gaps (${total - solid})`], ['STRONG', `Solid (${solid})`]] as const).map(([key, label]) => (
                    <button
                      key={key}
                      type="button"
                      role="tab"
                      aria-selected={filter === key}
                      onClick={() => setFilter(key)}
                      className={`px-3 py-1.5 rounded-md transition-colors ${
                        filter === key ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {sortedSkills.length === 0 ? (
                <p className="text-xs text-on-surface-variant py-8 text-center">No skills in this group.</p>
              ) : (
                <ul className="space-y-3">
                  {sortedSkills.map((sk) => {
                    const pct = Math.round(sk.skill_score * 100);
                    const meta = STATUS_META[sk.status] || STATUS_META.MISSING;
                    return (
                      <li key={sk.id} className="p-4 rounded-xl bg-surface-container-low/50 border border-outline-variant/40">
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                          <div className="flex flex-wrap items-center gap-2 min-w-0">
                            <span className="font-bold text-sm text-on-surface">{sk.skill_name}</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${meta.chip}`}>{meta.label}</span>
                          </div>
                          <span className="text-sm font-extrabold text-on-surface tabular-nums">{pct}%</span>
                        </div>

                        <div
                          className="relative h-2.5 w-full bg-surface-container-highest rounded-full overflow-hidden mb-2.5"
                          role="progressbar"
                          aria-valuenow={pct}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label={`${sk.skill_name} score`}
                        >
                          <div className={`h-full rounded-full transition-all ${meta.bar}`} style={{ width: `${pct}%` }} />
                          {/* 65% = the "solid" threshold used to skip a skill */}
                          <span className="absolute top-0 bottom-0 w-px bg-on-surface/40" style={{ left: '65%' }} />
                        </div>

                        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-[11px] text-on-surface-variant">
                          <span className="flex items-center gap-1">
                            <ShieldCheck className="w-3.5 h-3.5 text-primary" />
                            {sk.evidence_count > 0
                              ? `${sk.evidence_count} checkpoint${sk.evidence_count === 1 ? '' : 's'} of evidence`
                              : 'Estimated baseline, not yet verified'}
                          </span>
                          <span>{sk.evidence_count > 0 ? relativeDay(sk.last_assessed_at) : 'Take a quiz to verify'}</span>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
};
