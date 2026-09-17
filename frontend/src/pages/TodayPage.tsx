import React, { useEffect, useState } from 'react';
import { 
  Play, Pause, CheckCircle2, Clock, Sparkles, ExternalLink, 
  ThumbsUp, ThumbsDown, Award, HelpCircle, ArrowRight, BookOpen 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { TodayLearning } from '../types';

export const TodayPage: React.FC = () => {
  const [todayData, setTodayData] = useState<TodayLearning | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionActive, setSessionActive] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Checkpoint & Feedback State
  const [selfEval, setSelfEval] = useState<string>('GOT_IT');
  const [isCompleted, setIsCompleted] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<Record<string, boolean>>({});

  const fetchTodayQueue = async () => {
    setLoading(true);
    try {
      const res: any = await apiClient.get('/recommendations/today');
      setTodayData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodayQueue();
  }, []);

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

  const handleCompleteTask = async () => {
    if (!todayData?.task) return;
    try {
      if (sessionId) {
        await apiClient.patch(`/learning-sessions/${sessionId}`, {
          duration_seconds: secondsElapsed,
          status: 'COMPLETED'
        });
      }
      await apiClient.post(`/tasks/${todayData.task.id}/complete`, {
        time_spent_minutes: Math.max(1, Math.round(secondsElapsed / 60)),
        self_evaluation: selfEval
      });
      setIsCompleted(true);
      setSessionActive(false);
    } catch (err) {
      console.error(err);
      setIsCompleted(true);
    }
  };

  const handleFeedback = async (resourceId: string, isUseful: boolean) => {
    try {
      await apiClient.post(`/resources/${resourceId}/feedback`, { is_useful: isUseful });
      setFeedbackSubmitted({ ...feedbackSubmitted, [resourceId]: true });
    } catch (err) {
      console.error(err);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="w-full pt-28 pb-16 flex items-center justify-center min-h-screen">
        <div className="text-sm font-semibold text-on-surface-variant flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary animate-spin" />
          <span>Curating today's optimal learning queue...</span>
        </div>
      </div>
    );
  }

  const task = todayData?.task;

  if (!task || isCompleted) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-primary-fixed/50 text-primary flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-on-surface mb-2">Today's Learning Completed!</h1>
          <p className="text-xs text-on-surface-variant max-w-md mx-auto mb-6 leading-relaxed">
            Your evidence profile and skill scores have been updated based on your self-evaluation. Take a break or explore additional resources.
          </p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => {
                setIsCompleted(false);
                fetchTodayQueue();
              }}
              className="px-5 py-2.5 rounded-xl bg-surface-container-low text-on-surface font-semibold text-xs hover:bg-surface-container"
            >
              Check Next Task
            </button>
          </div>
        </div>
      </div>
    );
  }

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

          <div className="space-y-3 mb-8">
            {task.resources?.map((res, index) => (
              <div
                key={res.resource_id}
                className="p-4 rounded-xl bg-surface-container-low/70 border border-outline-variant/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-surface-container transition-colors"
              >
                <div className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded bg-primary/10 text-primary flex items-center justify-center font-bold text-xs mt-0.5">
                    {index + 1}
                  </span>
                  <div>
                    <a
                      href={res.url}
                      target="_blank"
                      rel="noreferrer"
                      className="font-bold text-sm text-on-surface hover:text-primary flex items-center gap-1.5"
                    >
                      <span>{res.title}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-on-surface-variant" />
                    </a>
                    <p className="text-xs text-on-surface-variant mt-0.5">{res.recommendation_reason}</p>
                    <div className="flex items-center gap-2 mt-1 text-[11px] text-on-surface-variant">
                      <span className="bg-surface-container px-2 py-0.5 rounded font-medium">{res.provider}</span>
                      <span>{res.duration_minutes} min read/lab</span>
                    </div>
                  </div>
                </div>

                {/* Useful Feedback Controls */}
                <div className="flex items-center gap-2 self-end sm:self-center">
                  <span className="text-[10px] text-on-surface-variant">Useful?</span>
                  <button
                    onClick={() => handleFeedback(res.resource_id, true)}
                    className={`p-1.5 rounded hover:bg-primary-fixed/40 transition-colors ${
                      feedbackSubmitted[res.resource_id] ? 'text-primary' : 'text-on-surface-variant'
                    }`}
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleFeedback(res.resource_id, false)}
                    className="p-1.5 rounded hover:bg-error-container/40 text-on-surface-variant transition-colors"
                  >
                    <ThumbsDown className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Reflection Checkpoint */}
          <div className="pt-6 border-t border-outline-variant/40">
            <h2 className="text-xs uppercase tracking-wider font-bold text-on-surface-variant mb-3">
              Reflection Checkpoint
            </h2>

            <div className="flex flex-wrap items-center justify-between gap-4 bg-surface-container-low p-4 rounded-xl mb-6">
              <span className="text-xs font-semibold text-on-surface">How confident do you feel after this session?</span>
              <div className="flex items-center gap-2">
                {[
                  { key: 'GOT_IT', label: 'Got it (Solid)' },
                  { key: 'SHAKY', label: 'Shaky (Needs review)' },
                  { key: 'LOST', label: 'Lost (Reinforce)' }
                ].map((opt) => (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => setSelfEval(opt.key)}
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

            <button
              onClick={handleCompleteTask}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-secondary-container text-on-primary font-bold text-sm hover:brightness-105 transition-all shadow-sm"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Complete Task & Update Skill Baseline</span>
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};
