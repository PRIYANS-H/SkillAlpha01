import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Play, Pause, CheckCircle2, Clock, Sparkles, ExternalLink, 
  ThumbsUp, ThumbsDown, Award, HelpCircle, ArrowRight, BookOpen, RefreshCw,
  Dumbbell, Hammer, Flag, Circle, Database
} from 'lucide-react';
import { apiClient } from '../api/client';
import { TodayLearning } from '../types';
import { ResourceCard } from '../components/resources/ResourceCard';
import { formatDueDate, isOverdue } from '../utils/dates';
import { PageSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

export const TodayPage: React.FC = () => {
  const { taskId } = useParams<{ taskId?: string }>();
  const toast = useToast();
  const [todayData, setTodayData] = useState<TodayLearning | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionActive, setSessionActive] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Checkpoint & Feedback State
  const [selfEval, setSelfEval] = useState<string>('');
  const [completing, setCompleting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<Record<string, boolean>>({});

  // Skill Self-Check Quiz State
  const [assessment, setAssessment] = useState<any | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizResult, setQuizResult] = useState<any | null>(null);
  const [quizError, setQuizError] = useState<string | null>(null);

  // Completion outcome
  const [completeError, setCompleteError] = useState<string | null>(null);
  const [adaptation, setAdaptation] = useState<any | null>(null);

  // Day-by-day plan and phase milestone check
  const [stepBusy, setStepBusy] = useState<number | null>(null);
  const [check, setCheck] = useState<any | null>(null);
  const [checkAnswers, setCheckAnswers] = useState<Record<string, number>>({});
  const [checkResult, setCheckResult] = useState<any | null>(null);
  const [checkSubmitting, setCheckSubmitting] = useState(false);

  const fetchSkillAssessment = async (skillId: string) => {
    try {
      const res: any = await apiClient.get(`/assessments/by-skill/${skillId}`);
      if (res && res.questions && res.questions.length > 0) {
        setAssessment(res);
      } else {
        setAssessment(null);
      }
    } catch (err) {
      setAssessment(null);
    }
  };

  const fetchTodayQueue = async (targetId?: string) => {
    setLoading(true);
    try {
      const effectiveId = targetId || taskId;
      const url = effectiveId ? `/recommendations/today?task_id=${effectiveId}` : '/recommendations/today';
      const res: any = await apiClient.get(url);
      setTodayData(res);
      setCheck(null);
      setCheckAnswers({});
      setCheckResult(null);
      if (res?.task?.kind === 'MILESTONE_CHECK') {
        setAssessment(null);
        setCheck(await apiClient.get(`/milestone-checks/${res.task.id}`));
      } else if (res?.task?.skill_id) {
        fetchSkillAssessment(res.task.skill_id);
      } else {
        setAssessment(null);
      }
    } catch (err: any) {
      toast.error(err.message || "Could not load today's task.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodayQueue();
  }, [taskId]);

  // Timer Effect
  useEffect(() => {
    let interval: any = null;
    if (sessionActive) {
      interval = setInterval(() => {
        setSecondsElapsed((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [sessionActive]);

  const handleStartSession = async () => {
    if (!todayData?.task) return;
    try {
      const res: any = await apiClient.post(`/learning-sessions?task_id=${todayData.task.id}`);
      setSessionId(res.session_id);
      setSessionActive(true);
    } catch (err) {
      setSessionActive(true);
    }
  };

  const handlePauseSession = () => {
    setSessionActive(false);
  };

  const handleToggleDay = async (index: number, done: boolean) => {
    if (!todayData?.task) return;
    setStepBusy(index);
    try {
      const updated: any = await apiClient.post(`/tasks/${todayData.task.id}/steps`, { index, done });
      setTodayData({ ...todayData, task: updated });
    } catch (err: any) {
      toast.error(err.message || 'Could not save that study day.');
    } finally {
      setStepBusy(null);
    }
  };

  const handleSubmitCheck = async () => {
    if (!check || checkSubmitting) return;
    setCheckSubmitting(true);
    try {
      const res: any = await apiClient.post(`/milestone-checks/${check.task_id}/attempt`, {
        answers: checkAnswers,
        time_spent_minutes: Math.max(1, Math.round(secondsElapsed / 60))
      });
      setCheckResult(res);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      toast.error(err.message || 'Could not submit the milestone check.');
    } finally {
      setCheckSubmitting(false);
    }
  };

  const handleRetakeCheck = () => {
    setCheckAnswers({});
    setCheckResult(null);
  };

  const quizReview: Record<string, { is_correct: boolean; correct_option_index: number; explanation?: string }> =
    Object.fromEntries(((quizResult?.review as any[]) || []).map((r: any) => [r.question_id, r]));

  const handleVerifyQuiz = async () => {
    if (!assessment) return;
    setQuizError(null);
    try {
      const res: any = await apiClient.post(`/assessments/${assessment.id}/attempt`, {
        answers: quizAnswers
      });
      setQuizResult(res);
      setQuizSubmitted(true);
    } catch (err: any) {
      setQuizError(err.message || 'Could not submit your answers. Please try again.');
    }
  };

  const handleCompleteTask = async () => {
    if (!todayData?.task || !selfEval || completing) return;
    setCompleteError(null);
    setCompleting(true);
    try {
      if (sessionId) {
        await apiClient.patch(`/learning-sessions/${sessionId}`, {
          duration_seconds: secondsElapsed,
          status: 'COMPLETED'
        });
      }
      const res: any = await apiClient.post(`/tasks/${todayData.task.id}/complete`, {
        time_spent_minutes: Math.max(1, Math.round(secondsElapsed / 60)),
        self_evaluation: selfEval
      });
      setAdaptation(res?.adaptation || null);
      setIsCompleted(true);
      setSessionActive(false);
    } catch (err: any) {
      setCompleteError(err.message || 'Could not save your progress. Please try again.');
    } finally {
      setCompleting(false);
    }
  };

  const handleNextTask = () => {
    setIsCompleted(false);
    setSecondsElapsed(0);
    setSessionId(null);
    setSessionActive(false);
    setSelfEval('');
    setAssessment(null);
    setQuizAnswers({});
    setQuizSubmitted(false);
    setQuizResult(null);
    setQuizError(null);
    setCompleteError(null);
    setAdaptation(null);
    fetchTodayQueue();
  };

  const handleFeedback = async (resourceId: string, isUseful: boolean) => {
    try {
      await apiClient.post(`/resources/${resourceId}/feedback`, { is_useful: isUseful });
      setFeedbackSubmitted({ ...feedbackSubmitted, [resourceId]: true });
      toast.success('Thanks! Your feedback tunes future recommendations.');
    } catch (err: any) {
      toast.error(err.message || 'Could not send your feedback.');
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) return <PageSkeleton variant="article" label="Loading today's task" />;

  const task = todayData?.task;

  // Empty state: No active roadmap found
  if (!todayData?.roadmap_id && !task) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <BookOpen className="w-12 h-12 text-primary mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-on-surface mb-2">No Active Learning Roadmap</h1>
          <p className="text-xs text-on-surface-variant max-w-md mx-auto mb-6 leading-relaxed">
            {todayData?.reason_why_today || "Complete onboarding to generate your personalized learning plan."}
          </p>
          <Link
            to="/create"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span>Build My Learning Path</span>
          </Link>
        </div>
      </div>
    );
  }

  // All roadmap tasks completed state
  if (todayData?.milestone_title === "Roadmap Completed" && !isCompleted) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <div className="w-14 h-14 rounded-full bg-primary-fixed/50 text-primary flex items-center justify-center mx-auto mb-4">
            <Award className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-on-surface mb-2">Roadmap Mastery Achieved!</h1>
          <p className="text-xs text-on-surface-variant max-w-md mx-auto mb-6 leading-relaxed">
            {todayData?.reason_why_today || "Congratulations! You have completed every milestone and practical task in your curriculum."}
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link
              to="/progress"
              className="px-5 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs"
            >
              View Mastery Profile
            </Link>
            <Link
              to={`/roadmap/${todayData.roadmap_id}`}
              className="px-5 py-2.5 rounded-xl bg-surface-container-low text-on-surface font-semibold text-xs hover:bg-surface-container"
            >
              Review Roadmap
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Task completed state
  if (!task || isCompleted) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <div className="w-14 h-14 rounded-full bg-primary-fixed/50 text-primary flex items-center justify-center mx-auto mb-4 animate-pop">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-on-surface mb-2">Task complete. Nice work!</h1>
          <p className="text-xs text-on-surface-variant max-w-md mx-auto mb-6 leading-relaxed">
            {secondsElapsed >= 60 ? `You studied for ${Math.round(secondsElapsed / 60)} minutes. ` : ''}
            Your skill scores have been updated. Take a break, or keep your momentum going with the next task.
          </p>
          {adaptation?.route_reasoning && (
            <div className="p-4 rounded-xl bg-surface-container-low border-l-4 border-secondary-container text-xs text-on-surface text-left mb-6">
              <strong className="text-secondary-container block mb-0.5">Plan update:</strong>
              {adaptation.route_reasoning}
            </div>
          )}
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={handleNextTask}
              className="px-5 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105"
            >
              Next task
            </button>
            <Link
              to={`/roadmap/${todayData?.roadmap_id || 'active'}`}
              className="px-5 py-2.5 rounded-xl bg-surface-container-low text-on-surface font-semibold text-xs hover:bg-surface-container"
            >
              View Full Roadmap
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const quizQuestions: any[] = assessment?.questions || [];
  const allQuestionsAnswered = quizQuestions.every((q) => quizAnswers[q.id] !== undefined);

  const kind = task.kind || 'SKILL';
  const planDays = task.days || [];
  const currentDayIndex = planDays.findIndex((d) => !d.done);
  const checkQuestions: any[] = check?.questions || [];
  const checkReview: Record<string, any> = Object.fromEntries(((checkResult?.review as any[]) || []).map((r: any) => [r.question_id, r]));
  const allCheckAnswered = checkQuestions.length > 0 && checkQuestions.every((q) => checkAnswers[q.id] !== undefined);
  const DAY_LABEL: Record<string, string> = { LEARN: 'Learn', PRACTICE: 'Practice', BUILD: 'Build', REVIEW: 'Review' };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        
        {/* Today's Action Banner */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6 sm:p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-secondary-container" />

          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <span className="px-3 py-1 rounded bg-secondary-fixed text-on-secondary-container text-xs font-bold uppercase tracking-wider">
              {todayData.milestone_title || "Active Focus Task"}
            </span>

            {/* Live Session Timer */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container text-on-surface font-mono text-sm font-bold">
                <Clock className="w-4 h-4 text-primary" />
                <span>{formatTimer(secondsElapsed)}</span>
              </div>

              {!sessionActive ? (
                <button
                  onClick={handleStartSession}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105"
                >
                  <Play className="w-3.5 h-3.5" /> Start Timer
                </button>
              ) : (
                <button
                  onClick={handlePauseSession}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-surface-container-high text-on-surface font-bold text-xs hover:bg-surface-container-highest"
                >
                  <Pause className="w-3.5 h-3.5" /> Pause
                </button>
              )}
            </div>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface mb-2">{task.title}</h1>
          {task.due_date && (
            <p className={`text-xs font-semibold mb-2 ${isOverdue(task.due_date, task.status) ? 'text-on-error-container' : 'text-primary'}`}>
              {isOverdue(task.due_date, task.status)
                ? `Was due ${formatDueDate(task.due_date)}. Use "Re-pace Plan" on your roadmap to shift your schedule.`
                : `Due ${formatDueDate(task.due_date)}`}
            </p>
          )}
          <p className="text-sm text-on-surface-variant mb-6 leading-relaxed">{task.description}</p>

          {/* Rationale Statement */}
          <div className="p-4 rounded-xl bg-surface-container-low border-l-4 border-secondary-container text-xs text-on-surface mb-6">
            <strong className="text-secondary-container block mb-0.5">Why this task today:</strong>
            {todayData.reason_why_today || task.reason_why_next}
          </div>

          {/* Day-by-day plan */}
          {planDays.length > 0 && (
            <div className="mb-8">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">
                  Your {planDays.length}-day plan for this skill
                </h2>
                <span className="text-[11px] font-semibold text-on-surface-variant">
                  {planDays.filter((d) => d.done).length}/{planDays.length} days done
                </span>
              </div>
              <ol className="space-y-3">
                {planDays.map((day) => {
                  const isCurrent = day.index === currentDayIndex;
                  return (
                    <li
                      key={day.index}
                      className={`rounded-xl border p-4 ${
                        day.done
                          ? 'bg-surface-container-low/60 border-outline-variant/40'
                          : isCurrent
                          ? 'bg-secondary-fixed/20 border-secondary-container'
                          : 'bg-surface-container-lowest border-outline-variant/60'
                      }`}
                    >
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-surface-container text-on-surface-variant">
                          Day {day.index + 1} · {DAY_LABEL[day.kind] || day.kind}
                        </span>
                        <span className={`text-sm font-bold text-on-surface ${day.done ? 'line-through opacity-70' : ''}`}>{day.title}</span>
                        {day.date && <span className="text-[11px] text-on-surface-variant">{formatDueDate(day.date)}</span>}
                        {isCurrent && <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-secondary-container text-on-primary">Do this next</span>}
                        <button
                          type="button"
                          onClick={() => handleToggleDay(day.index, !day.done)}
                          disabled={stepBusy === day.index || task.status === 'COMPLETED' || task.status === 'SKIPPED'}
                          aria-pressed={day.done}
                          className={`ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors disabled:opacity-60 ${
                            day.done ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface hover:bg-surface-container-high'
                          }`}
                        >
                          {day.done ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                          {day.done ? 'Done' : 'Mark day done'}
                        </button>
                      </div>
                      <ol className="list-decimal pl-5 space-y-1 text-xs text-on-surface leading-relaxed">
                        {day.steps.map((step, i) => <li key={i}>{step}</li>)}
                      </ol>
                      {day.kind === 'PRACTICE' && task.skill_name && (
                        <Link
                          to={`/practice?skill=${encodeURIComponent(task.skill_name)}`}
                          className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-on-primary text-xs font-bold hover:bg-primary-container"
                        >
                          <Dumbbell className="w-3.5 h-3.5" /> Open practice problems
                        </Link>
                      )}
                      {day.check && (
                        <p className="mt-3 text-xs text-on-surface-variant">
                          <strong className="text-primary">Check yourself:</strong> {day.check}
                        </p>
                      )}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}

          {/* Phase project */}
          {kind === 'PROJECT' && (
            <div className="mb-8 p-5 rounded-xl bg-surface-container-low border border-outline-variant/40">
              <h2 className="text-xs uppercase tracking-wider font-bold text-primary flex items-center gap-1.5 mb-2">
                <Hammer className="w-4 h-4" /> Phase project
              </h2>
              {task.project && (
                <p className="text-xs text-on-surface flex items-start gap-2 mb-1.5">
                  <Database className="w-4 h-4 text-primary flex-shrink-0" />
                  <span>{task.project.dataset} · about {task.project.estimated_hours} hours over {task.day_count} study days</span>
                </p>
              )}
              <p className="text-xs text-on-surface-variant leading-relaxed mb-4">
                Open the brief, build it, then submit a link to your code and tick the checklist. Passing the checklist completes this task.
              </p>
              <Link
                to={`/projects?project=${task.ref_id || ''}`}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105"
              >
                Open project brief <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}

          {/* Phase milestone check */}
          {kind === 'MILESTONE_CHECK' && check && (
            <div className="mb-6">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h2 className="text-xs uppercase tracking-wider font-bold text-primary flex items-center gap-1.5">
                  <Flag className="w-4 h-4" /> Milestone check · pass at {check.pass_percent}%
                </h2>
                <span className="text-[10px] text-on-surface-variant font-semibold">
                  {checkResult
                    ? `${checkResult.score}/${checkResult.max_score} correct`
                    : `${checkQuestions.filter((q) => checkAnswers[q.id] !== undefined).length}/${checkQuestions.length} answered`}
                </span>
              </div>

              {checkResult && (
                <div className={`mb-4 p-4 rounded-xl text-xs leading-relaxed ${checkResult.passed ? 'bg-primary-fixed/40 text-on-surface' : 'bg-error-container text-on-error-container'}`} role="status">
                  <strong className="block text-sm mb-0.5">{checkResult.passed ? `Passed with ${checkResult.percent}%` : `${checkResult.percent}% — not passed yet`}</strong>
                  {checkResult.feedback}
                  {checkResult.adaptation?.route_reasoning && <p className="mt-1">{checkResult.adaptation.route_reasoning}</p>}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {checkResult.passed || task.status === 'COMPLETED' ? (
                      <button type="button" onClick={handleNextTask} className="px-4 py-2 rounded-lg bg-secondary-container text-on-primary font-bold">
                        Go to my next task
                      </button>
                    ) : (
                      <>
                        <button type="button" onClick={handleRetakeCheck} className="px-4 py-2 rounded-lg bg-surface-container-lowest text-on-surface font-bold">
                          Take it again
                        </button>
                        <Link to="/practice" className="px-4 py-2 rounded-lg bg-surface-container-lowest text-on-surface font-bold">
                          Practice first
                        </Link>
                      </>
                    )}
                  </div>
                </div>
              )}

              {checkQuestions.map((question, qIdx) => {
                const r = checkReview[question.id];
                return (
                  <div key={question.id} className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/40 mb-3">
                    <div className="text-[10px] font-bold uppercase text-on-surface-variant mb-1">{question.skill_name}</div>
                    <div className="text-sm font-semibold text-on-surface mb-3">{qIdx + 1}. {question.question_text}</div>
                    <div className="space-y-2">
                      {question.options.map((opt: string, idx: number) => (
                        <label
                          key={idx}
                          className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs cursor-pointer transition-colors ${
                            checkAnswers[question.id] === idx
                              ? 'border-primary bg-primary-fixed/20'
                              : 'border-outline-variant/40 bg-surface-container-lowest hover:border-outline'
                          }`}
                        >
                          <input
                            type="radio"
                            name={`check_${question.id}`}
                            checked={checkAnswers[question.id] === idx}
                            onChange={() => setCheckAnswers({ ...checkAnswers, [question.id]: idx })}
                            disabled={!!checkResult}
                            className="accent-primary"
                          />
                          <span className="text-on-surface">{opt}</span>
                        </label>
                      ))}
                    </div>
                    {r && (
                      <div className="mt-3 text-xs leading-relaxed">
                        <span className={`font-bold ${r.is_correct ? 'text-primary' : 'text-on-error-container'}`}>
                          {r.is_correct ? '✓ Correct' : `✗ Correct answer: ${question.options[r.correct_option_index]}`}
                        </span>
                        {r.explanation && <p className="text-on-surface-variant mt-1">{r.explanation}</p>}
                      </div>
                    )}
                  </div>
                );
              })}

              {!checkResult && (
                <>
                  <button
                    type="button"
                    onClick={handleSubmitCheck}
                    disabled={!allCheckAnswered || checkSubmitting}
                    className="w-full py-3.5 rounded-xl bg-secondary-container text-on-primary font-bold text-sm hover:brightness-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {checkSubmitting ? 'Grading…' : 'Submit milestone check'}
                  </button>
                  {!allCheckAnswered && (
                    <p className="text-[11px] text-on-surface-variant text-center mt-2">Answer every question to submit.</p>
                  )}
                </>
              )}
            </div>
          )}

          {/* Curated Resources List */}
          {(task.resources?.length || 0) > 0 && (
          <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant mb-3">
            Resources for this task ({task.resources?.length || 0}) · start with the first
          </h2>
          )}

          <div className={`space-y-4 ${(task.resources?.length || 0) > 0 ? 'mb-8' : ''}`}>
            {task.resources?.map((res, index) => (
              <ResourceCard
                key={res.resource_id}
                resource={res}
                index={index}
                onFeedback={handleFeedback}
                isFeedbackSubmitted={!!feedbackSubmitted[res.resource_id]}
              />
            ))}
          </div>

          {/* Self-Check Knowledge Verification Quiz */}
          {quizQuestions.length > 0 && (
            <div className="pt-6 border-t border-outline-variant/40 mb-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs uppercase tracking-wider font-bold text-primary flex items-center gap-1.5">
                  <HelpCircle className="w-4 h-4" /> Quick skill check
                </h2>
                <span className="text-[10px] text-on-surface-variant font-semibold">
                  {quizSubmitted
                    ? `${quizResult?.score ?? 0}/${quizResult?.max_score ?? quizQuestions.length} correct`
                    : `${quizQuestions.filter((q) => quizAnswers[q.id] !== undefined).length}/${quizQuestions.length} answered`}
                </span>
              </div>

              {quizQuestions.map((question, qIdx) => (
                <div key={question.id} className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/40 mb-3">
                  <div className="text-sm font-semibold text-on-surface mb-3">
                    {qIdx + 1}. {question.question_text}
                  </div>
                  <div className="space-y-2">
                    {question.options.map((opt: string, idx: number) => (
                      <label
                        key={idx}
                        className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs cursor-pointer transition-colors ${
                          quizAnswers[question.id] === idx
                            ? 'border-primary bg-primary-fixed/20'
                            : 'border-outline-variant/40 bg-surface-container-lowest hover:border-outline'
                        }`}
                      >
                        <input
                          type="radio"
                          name={`self_check_${question.id}`}
                          checked={quizAnswers[question.id] === idx}
                          onChange={() => setQuizAnswers({ ...quizAnswers, [question.id]: idx })}
                          disabled={quizSubmitted}
                          className="accent-primary"
                        />
                        <span className="text-on-surface">{opt}</span>
                      </label>
                    ))}
                  </div>
                  {quizSubmitted && (() => {
                    const r = quizReview[question.id];
                    if (!r) return null;
                    return (
                      <div className="mt-3 text-xs leading-relaxed">
                        <span className={`font-bold ${r.is_correct ? 'text-primary' : 'text-on-error-container'}`}>
                          {r.is_correct ? '✓ Correct' : `✗ Correct answer: ${question.options[r.correct_option_index]}`}
                        </span>
                        {r.explanation && <p className="text-on-surface-variant mt-1">{r.explanation}</p>}
                      </div>
                    );
                  })()}
                </div>
              ))}

              {!quizSubmitted ? (
                <>
                  <button
                    type="button"
                    onClick={handleVerifyQuiz}
                    disabled={!allQuestionsAnswered}
                    className="px-4 py-2 rounded-lg bg-primary text-on-primary text-xs font-semibold hover:bg-primary-container disabled:opacity-50 transition-colors"
                  >
                    Check my answers
                  </button>
                  {quizError && (
                    <p className="mt-2 text-xs text-on-error-container bg-error-container rounded-lg p-2.5">{quizError}</p>
                  )}
                </>
              ) : (
                <div className="mt-2 p-3 rounded-lg bg-surface-container text-xs text-on-surface">
                  <span className="font-bold text-primary block mb-1">
                    {quizResult?.passed ? "✓ Passed! Mastery evidence calibrated." : "Not there yet. Review the explanations above."}
                  </span>
                  <p className="text-on-surface-variant leading-relaxed">{quizResult?.feedback}</p>
                  {quizResult?.adaptation?.route_reasoning && (
                    <p className="text-on-surface-variant leading-relaxed mt-1">{quizResult.adaptation.route_reasoning}</p>
                  )}
                </div>
              )}
            </div>
          )}

          {task.status === 'COMPLETED' || task.status === 'SKIPPED' ? (
            <div className="pt-6 border-t border-outline-variant/40 flex flex-wrap items-center justify-between gap-3">
              <span className="inline-flex items-center gap-2 text-xs font-bold text-primary">
                <CheckCircle2 className="w-4 h-4" /> You've already finished this task. Review it any time.
              </span>
              <Link
                to="/learn"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all"
              >
                Go to my next task <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : kind !== 'SKILL' ? null : (
          <>
          {/* Reflection Checkpoint */}
          <div className="pt-6 border-t border-outline-variant/40">
            <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant mb-3">
              Reflection Checkpoint
            </h2>

            <div className="flex flex-wrap items-center justify-between gap-4 bg-surface-container-low p-4 rounded-xl mb-6">
              <span className="text-xs font-semibold text-on-surface">How confident do you feel after this session?</span>
              <div className="flex flex-wrap items-center gap-2" role="radiogroup" aria-label="Confidence after this session">
                {[
                  { key: 'GOT_IT', label: 'Got it' },
                  { key: 'SHAKY', label: 'Still shaky' },
                  { key: 'LOST', label: 'Lost' }
                ].map((opt) => (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => setSelfEval(opt.key)}
                    role="radio"
                    aria-checked={selfEval === opt.key}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                      selfEval === opt.key
                        ? 'bg-primary text-on-primary shadow-sm'
                        : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {completeError && (
              <p className="mb-3 text-xs text-on-error-container bg-error-container rounded-lg p-2.5">{completeError}</p>
            )}

            <button
              onClick={handleCompleteTask}
              disabled={!selfEval || completing}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-secondary-container text-on-primary font-bold text-sm hover:brightness-105 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{completing ? 'Saving…' : 'Complete task'}</span>
            </button>
            {!selfEval && (
              <p className="text-[11px] text-on-surface-variant text-center mt-2">Choose how confident you feel to finish this task.</p>
            )}
          </div>
          </>
          )}

        </div>

      </div>
    </div>
  );
};
