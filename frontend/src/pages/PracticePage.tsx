import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, ExternalLink, Flame, Trophy, Target, ChevronDown, ChevronUp, Dumbbell } from 'lucide-react';
import { apiClient } from '../api/client';
import { PracticeProblem, PracticeStats } from '../types';
import { PageSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

type Difficulty = 'EASY' | 'MEDIUM' | 'HARD';

interface ProblemListResponse {
  scope: 'roadmap' | 'all';
  has_roadmap: boolean;
  skills: string[];
  problems: PracticeProblem[];
  stats: PracticeStats;
}

interface SubmitResult {
  correct: boolean;
  solved: boolean;
  attempts: number;
  points_awarded: number;
  explanation?: string | null;
  correct_answer?: string | null;
  tries_before_reveal: number;
}

const DIFFICULTY_LABEL: Record<Difficulty, string> = { EASY: 'Easy', MEDIUM: 'Medium', HARD: 'Hard' };
const DIFFICULTY_STYLE: Record<Difficulty, string> = {
  EASY: 'bg-primary-fixed/50 text-primary',
  MEDIUM: 'bg-secondary-fixed text-on-secondary-container',
  HARD: 'bg-error-container text-on-error-container',
};

export const PracticePage: React.FC = () => {
  const toast = useToast();
  const [data, setData] = useState<ProblemListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [scope, setScope] = useState<'roadmap' | 'all'>('roadmap');
  const [skill, setSkill] = useState<string>(() => new URLSearchParams(window.location.search).get('skill') || '');
  const [difficulty, setDifficulty] = useState<'' | Difficulty>('');
  const [hideSolved, setHideSolved] = useState(false);
  const [openId, setOpenId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, SubmitResult>>({});
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = async (nextScope: 'roadmap' | 'all', showSpinner: boolean) => {
    if (showSpinner) setLoading(true);
    try {
      const res: any = await apiClient.get(`/problems?scope=${nextScope}`);
      setData(res);
      // A skill from the URL that is not on the learner's path lives in the full library
      if (nextScope === 'roadmap' && skill && !res.skills.includes(skill)) {
        setScope('all');
      }
    } catch (err: any) {
      toast.error(err.message || 'Could not load practice problems.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(scope, data === null);
  }, [scope]);

  const visible = useMemo(() => {
    if (!data) return [];
    return data.problems.filter(
      (p) => (!skill || p.skill_name === skill) && (!difficulty || p.difficulty === difficulty) && !(hideSolved && p.solved)
    );
  }, [data, skill, difficulty, hideSolved]);

  const grouped = useMemo(() => {
    const groups: { skill: string; problems: PracticeProblem[] }[] = [];
    visible.forEach((p) => {
      const last = groups[groups.length - 1];
      if (last && last.skill === p.skill_name) last.problems.push(p);
      else groups.push({ skill: p.skill_name, problems: [p] });
    });
    return groups;
  }, [visible]);

  const patchProblem = (id: string, patch: Partial<PracticeProblem>) => {
    setData((prev) => (prev ? { ...prev, problems: prev.problems.map((p) => (p.id === id ? { ...p, ...patch } : p)) } : prev));
  };

  const handleSubmit = async (problem: PracticeProblem) => {
    const raw = answers[problem.id];
    if (raw === undefined || raw === '') return;
    setBusyId(problem.id);
    try {
      const answer = problem.type === 'MCQ' ? raw : Number(raw);
      const res: any = await apiClient.post(`/problems/${problem.id}/submit`, { answer });
      setResults((prev) => ({ ...prev, [problem.id]: res }));
      patchProblem(problem.id, {
        solved: res.solved,
        attempts: res.attempts,
        points_earned: res.points_awarded || problem.points_earned,
      });
      if (res.correct && res.points_awarded > 0) toast.success(`Correct! +${res.points_awarded} points`);
      if (res.solved) load(scope, false);
    } catch (err: any) {
      toast.error(err.message || 'Could not check your answer.');
    } finally {
      setBusyId(null);
    }
  };

  const handleMark = async (problem: PracticeProblem, solved: boolean) => {
    setBusyId(problem.id);
    try {
      const res: any = await apiClient.post(`/problems/${problem.id}/mark`, { solved });
      patchProblem(problem.id, { solved: res.solved, points_earned: res.points_earned });
      load(scope, false);
    } catch (err: any) {
      toast.error(err.message || 'Could not update this problem.');
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <PageSkeleton variant="list" label="Loading practice problems" />;
  if (!data) return null;

  const stats = data.stats;
  const solvedPct = stats.total ? Math.round((stats.solved / stats.total) * 100) : 0;

  return (
    <div className="w-full pt-20 pb-24 bg-surface min-h-screen">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface flex items-center gap-2">
            <Dumbbell className="w-6 h-6 text-primary" /> Practice
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {data.scope === 'roadmap'
              ? 'Problems for the skills on your roadmap, in the order you will meet them.'
              : 'Every problem in the library, across all tracks.'}{' '}
            Answers are checked on the server; the explanation appears once you solve a problem or after two tries.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <div className="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/60">
            <div className="text-[10px] font-bold uppercase text-on-surface-variant flex items-center gap-1"><Target className="w-3.5 h-3.5 text-primary" /> Solved</div>
            <div className="text-xl font-extrabold text-on-surface mt-1">{stats.solved}<span className="text-sm font-semibold text-on-surface-variant"> / {stats.total}</span></div>
            <div className="h-1.5 mt-2 rounded-full bg-surface-container-highest overflow-hidden" role="progressbar" aria-valuenow={solvedPct} aria-valuemin={0} aria-valuemax={100} aria-label="Problems solved">
              <div className="h-full bg-primary-container rounded-full" style={{ width: `${solvedPct}%` }} />
            </div>
          </div>
          <div className="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/60">
            <div className="text-[10px] font-bold uppercase text-on-surface-variant flex items-center gap-1"><Trophy className="w-3.5 h-3.5 text-secondary-container" /> Points</div>
            <div className="text-xl font-extrabold text-on-surface mt-1">{stats.points}</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Easy 10 · Medium 20 · Hard 40</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/60">
            <div className="text-[10px] font-bold uppercase text-on-surface-variant flex items-center gap-1"><Flame className="w-3.5 h-3.5 text-secondary-container" /> Streak</div>
            <div className="text-xl font-extrabold text-on-surface mt-1">{stats.streak_days} day{stats.streak_days === 1 ? '' : 's'}</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Solve one problem a day to keep it</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/60">
            <div className="text-[10px] font-bold uppercase text-on-surface-variant mb-1.5">By difficulty</div>
            {(['EASY', 'MEDIUM', 'HARD'] as Difficulty[]).map((d) => (
              <div key={d} className="flex items-center justify-between text-xs text-on-surface">
                <span>{DIFFICULTY_LABEL[d]}</span>
                <span className="font-bold">{stats.by_difficulty[d].solved}/{stats.by_difficulty[d].total}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 mb-5">
          {data.has_roadmap && (
            <div className="inline-flex rounded-lg border border-outline-variant/60 overflow-hidden text-xs font-semibold">
              {(['roadmap', 'all'] as const).map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => { setScope(s); if (s === 'roadmap') setSkill(''); }}
                  aria-pressed={scope === s}
                  className={`px-3 py-2 ${scope === s ? 'bg-primary text-on-primary' : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container'}`}
                >
                  {s === 'roadmap' ? 'My roadmap' : 'All tracks'}
                </button>
              ))}
            </div>
          )}
          <select
            aria-label="Filter by skill"
            value={skill}
            onChange={(e) => setSkill(e.target.value)}
            className="h-9 px-2 rounded-lg border border-outline-variant/60 text-xs text-on-surface bg-surface-container-lowest max-w-[230px]"
          >
            <option value="">All skills</option>
            {data.skills.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select
            aria-label="Filter by difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as '' | Difficulty)}
            className="h-9 px-2 rounded-lg border border-outline-variant/60 text-xs text-on-surface bg-surface-container-lowest"
          >
            <option value="">Any difficulty</option>
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
          </select>
          <label className="inline-flex items-center gap-1.5 text-xs text-on-surface-variant cursor-pointer">
            <input type="checkbox" checked={hideSolved} onChange={(e) => setHideSolved(e.target.checked)} className="accent-primary" />
            Hide solved
          </label>
        </div>

        {!data.has_roadmap && (
          <div className="mb-5 p-3 rounded-xl bg-surface-container-low text-xs text-on-surface-variant">
            You are seeing every track. <Link to="/create" className="text-primary font-bold hover:underline">Build a roadmap</Link> to get the problems that match your goal, in order.
          </div>
        )}

        {grouped.length === 0 && (
          <div className="p-8 rounded-2xl bg-surface-container-lowest border border-outline-variant/60 text-center text-sm text-on-surface-variant">
            No problems match these filters.
          </div>
        )}

        <div className="space-y-6">
          {grouped.map((group) => (
            <section key={group.skill}>
              <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant mb-2">
                {group.skill} · {group.problems.filter((p) => p.solved).length}/{group.problems.length} solved
              </h2>
              <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 divide-y divide-outline-variant/30 overflow-hidden">
                {group.problems.map((problem) => {
                  const open = openId === problem.id;
                  const result = results[problem.id];
                  return (
                    <div key={problem.id}>
                      <button
                        type="button"
                        onClick={() => setOpenId(open ? null : problem.id)}
                        aria-expanded={open}
                        className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-surface-container-low/50 transition-colors"
                      >
                        <CheckCircle2 className={`w-4 h-4 flex-shrink-0 ${problem.solved ? 'text-primary' : 'text-outline-variant'}`} aria-label={problem.solved ? 'Solved' : 'Not solved'} />
                        <span className="flex-1 min-w-0 text-sm font-semibold text-on-surface truncate">{problem.title}</span>
                        {problem.type === 'EXTERNAL' && (
                          <span className="hidden sm:inline text-[10px] font-bold px-2 py-0.5 rounded bg-surface-container text-on-surface-variant whitespace-nowrap">{problem.platform}</span>
                        )}
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded whitespace-nowrap ${DIFFICULTY_STYLE[problem.difficulty]}`}>{DIFFICULTY_LABEL[problem.difficulty]}</span>
                        <span className="text-[11px] font-bold text-on-surface-variant w-12 text-right whitespace-nowrap">
                          {problem.solved ? `+${problem.points_earned}` : `${problem.type === 'EXTERNAL' ? Math.floor(problem.points / 2) : problem.points} pts`}
                        </span>
                        {open ? <ChevronUp className="w-4 h-4 text-on-surface-variant flex-shrink-0" /> : <ChevronDown className="w-4 h-4 text-on-surface-variant flex-shrink-0" />}
                      </button>

                      {open && (
                        <div className="px-4 pb-4 pt-1 bg-surface-container-low/40">
                          <p className="text-sm text-on-surface leading-relaxed mb-3 whitespace-pre-line">{problem.prompt}</p>

                          {problem.type === 'MCQ' && (
                            <div className="space-y-2 mb-3">
                              {(problem.options || []).map((opt) => (
                                <label
                                  key={opt}
                                  className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs cursor-pointer transition-colors ${
                                    answers[problem.id] === opt ? 'border-primary bg-primary-fixed/20' : 'border-outline-variant/40 bg-surface-container-lowest hover:border-outline'
                                  }`}
                                >
                                  <input
                                    type="radio"
                                    name={`problem_${problem.id}`}
                                    checked={answers[problem.id] === opt}
                                    onChange={() => setAnswers({ ...answers, [problem.id]: opt })}
                                    disabled={problem.solved}
                                    className="accent-primary"
                                  />
                                  <span className="text-on-surface">{opt}</span>
                                </label>
                              ))}
                            </div>
                          )}

                          {problem.type === 'NUMERIC' && (
                            <div className="mb-3">
                              <label htmlFor={`answer_${problem.id}`} className="block text-[11px] font-bold uppercase text-on-surface-variant mb-1">Your answer (number)</label>
                              <input
                                id={`answer_${problem.id}`}
                                type="number"
                                step="any"
                                inputMode="decimal"
                                value={answers[problem.id] ?? ''}
                                onChange={(e) => setAnswers({ ...answers, [problem.id]: e.target.value })}
                                onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(problem); }}
                                disabled={problem.solved}
                                className="w-40 h-10 px-3 rounded-lg border border-outline-variant/60 text-sm text-on-surface bg-surface-container-lowest"
                              />
                            </div>
                          )}

                          {problem.type === 'EXTERNAL' ? (
                            <div className="flex flex-wrap items-center gap-2">
                              <a
                                href={problem.url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-on-primary text-xs font-bold hover:bg-primary-container"
                              >
                                Open on {problem.platform} <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                              <button
                                type="button"
                                onClick={() => handleMark(problem, !problem.solved)}
                                disabled={busyId === problem.id}
                                className="px-4 py-2 rounded-lg bg-surface-container text-on-surface text-xs font-bold hover:bg-surface-container-high disabled:opacity-50"
                              >
                                {problem.solved ? 'Mark as not solved' : 'I solved it'}
                              </button>
                            </div>
                          ) : !problem.solved ? (
                            <button
                              type="button"
                              onClick={() => handleSubmit(problem)}
                              disabled={busyId === problem.id || !answers[problem.id]}
                              className="px-4 py-2 rounded-lg bg-primary text-on-primary text-xs font-bold hover:bg-primary-container disabled:opacity-50"
                            >
                              {busyId === problem.id ? 'Checking…' : 'Check answer'}
                            </button>
                          ) : null}

                          {result && (
                            <div className="mt-3 text-xs leading-relaxed" role="status">
                              <span className={`font-bold ${result.correct ? 'text-primary' : 'text-on-error-container'}`}>
                                {result.correct
                                  ? '✓ Correct'
                                  : result.correct_answer
                                  ? `✗ Not quite. Answer: ${result.correct_answer}`
                                  : `✗ Not quite. ${result.tries_before_reveal} more ${result.tries_before_reveal === 1 ? 'try' : 'tries'} before the answer is shown.`}
                              </span>
                              {result.explanation && <p className="text-on-surface-variant mt-1">{result.explanation}</p>}
                            </div>
                          )}
                          {!result && problem.solved && problem.type !== 'EXTERNAL' && (
                            <p className="text-xs font-bold text-primary">✓ Solved in {problem.attempts} {problem.attempts === 1 ? 'try' : 'tries'}</p>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
};
