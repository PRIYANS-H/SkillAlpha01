import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Play, Pause, CheckCircle2, Clock, Sparkles, ExternalLink, 
  ThumbsUp, ThumbsDown, Award, HelpCircle, ArrowRight, BookOpen, RefreshCw 
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
      if (res?.task?.skill_id) {
        fetchSkillAssessment(res.task.skill_id);
      }
    } catch (err) {
      console.error(err);
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
      console.error(err);
      setSessionActive(true);
    }
  };

  const handlePauseSession = () => {
    setSessionActive(false);
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

          {/* Curated Resources List */}
          <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant mb-3">
            Recommended Resource Stack ({task.resources?.length || 0})
          </h2>

          <div className="space-y-4 mb-8">
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
          ) : (
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
