import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Flag, Clock as Schedule, TrendingUp, CheckCircle, Clock, BookOpen, 
  ExternalLink, RefreshCw, ChevronDown, ChevronUp, Play, Sparkles, 
  Calendar, Layers, Video, Code, FileText, Settings, Bookmark 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { Roadmap, RoadmapMilestone, RoadmapTask } from '../types';
import { formatDueDate, formatDateRange, isOverdue } from '../utils/dates';
import { PageSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

export const RoadmapPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const toast = useToast();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [replanning, setReplanning] = useState(false);
  const [expandedMilestoneId, setExpandedMilestoneId] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<RoadmapTask | null>(null);

  // Format filter for the "resources in your roadmap" list (empty = show every format)
  const [resourcePreferences, setResourcePreferences] = useState<string[]>([]);

  const togglePreference = (pref: string) => {
    if (resourcePreferences.includes(pref)) {
      setResourcePreferences(resourcePreferences.filter(p => p !== pref));
    } else {
      setResourcePreferences([...resourcePreferences, pref]);
    }
  };

  /** Opens the week that holds the learner's next task and selects that task. */
  const focusNextTask = (rm: Roadmap) => {
    const milestones = rm.milestones || [];
    const current = milestones.find((m) => m.tasks.some((t) => t.status === 'NOT_STARTED' || t.status === 'IN_PROGRESS'));
    const target = current || milestones[0];
    setExpandedMilestoneId(target ? target.id : null);
    const next = current?.tasks.find((t) => t.status === 'NOT_STARTED' || t.status === 'IN_PROGRESS') || null;
    setSelectedTask(next);
  };

  const fetchRoadmap = async () => {
    setLoading(true);
    try {
      if (id === 'active' || !id) {
        const roadmaps: any = await apiClient.get('/roadmaps');
        if (roadmaps && roadmaps.length > 0) {
          const current = roadmaps.find((r: Roadmap) => r.is_active) || roadmaps[0];
          setRoadmap(current);
          focusNextTask(current);
        }
      } else {
        const res: any = await apiClient.get(`/roadmaps/${id}`);
        setRoadmap(res);
        focusNextTask(res);
      }
    } catch (err: any) {
      toast.error(err.message || 'Could not load your roadmap.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, [id]);

  const handleRepace = async () => {
    if (!roadmap) return;
    setReplanning(true);
    try {
      const res: any = await apiClient.post(`/roadmaps/${roadmap.id}/repace`);
      setRoadmap(res);
      focusNextTask(res);
      toast.success('Plan re-paced. Your next task is due today.');
    } catch (err: any) {
      toast.error(err.message || 'Could not re-pace your plan. Please try again.');
    } finally {
      setReplanning(false);
    }
  };

  if (loading) return <PageSkeleton variant="list" label="Loading your roadmap" />;

  if (!roadmap) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <Flag className="w-10 h-10 text-primary mx-auto mb-3" />
          <h2 className="text-xl font-bold text-on-surface mb-2">You don't have a roadmap yet</h2>
          <p className="text-sm text-on-surface-variant mb-6 max-w-md mx-auto">
            Tell us your goal and what you already know. In about two minutes you'll get a week-by-week plan that skips what you've mastered.
          </p>
          <Link
            to="/create"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-sm"
          >
            Build Learning Path
          </Link>
        </div>
      </div>
    );
  }

  const allTasks = roadmap.milestones.flatMap((m) => m.tasks);
  const nextTask = allTasks.find((t) => t.status === 'NOT_STARTED' || t.status === 'IN_PROGRESS') || null;
  const overdueCount = allTasks.filter((t) => isOverdue(t.due_date, t.status)).length;
  const scheduleWindow = formatDateRange(allTasks.map((t) => t.due_date));
  const progressPct = Math.round(roadmap.progress_percent || 0);

  const dailyHours = (roadmap.hours_per_week / 5.0).toFixed(1);

  // Extract all active resources across roadmap tasks
  const allActiveResources: any[] = [];
  roadmap.milestones.forEach((m) => {
    m.tasks.forEach((t) => {
      if (t.resources) {
        t.resources.forEach((r) => {
          if (!allActiveResources.some((item) => item.resource_id === r.resource_id)) {
            allActiveResources.push(r);
          }
        });
      }
    });
  });

  const visibleResources = resourcePreferences.length
    ? allActiveResources.filter((r) => resourcePreferences.includes(r.resource_type))
    : allActiveResources;

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header Summary Banner */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6 mb-8">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-container/10 flex items-center justify-center text-primary-container">
                <Flag className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[11px] text-on-surface-variant uppercase tracking-wider font-bold">Target Goal</div>
                <h1 className="text-xl sm:text-2xl font-extrabold text-on-surface">{roadmap.goal}</h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container text-on-surface text-xs font-medium">
                <Schedule className="w-4 h-4 text-primary" />
                <span>{roadmap.duration_weeks}-Week Pace • {roadmap.hours_per_week} hrs/wk</span>
              </div>
              <button
                onClick={handleRepace}
                disabled={replanning}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-fixed/40 text-primary text-xs font-semibold hover:bg-primary-fixed/70 transition-colors"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${replanning ? 'animate-spin' : ''}`} />
                <span>Re-pace Plan</span>
              </button>
            </div>
          </div>

          {/* Progress + next action */}
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-bold text-on-surface">{progressPct}% complete</span>
                <span className="text-on-surface-variant">{roadmap.completed_tasks} of {roadmap.total_tasks} tasks done</span>
              </div>
              <div
                className="h-2.5 w-full bg-surface-container-highest rounded-full overflow-hidden"
                role="progressbar"
                aria-valuenow={progressPct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label="Roadmap progress"
              >
                <div className="h-full rounded-full bg-primary-container transition-all duration-500" style={{ width: `${progressPct}%` }} />
              </div>
            </div>
            {nextTask ? (
              <Link
                to={`/learn/${nextTask.id}`}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm sm:max-w-xs"
              >
                <Play className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{nextTask.status === 'IN_PROGRESS' ? 'Resume' : 'Start'}: {nextTask.title}</span>
              </Link>
            ) : (
              <span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-fixed/50 text-primary font-bold text-xs">
                <CheckCircle className="w-4 h-4" /> Roadmap complete
              </span>
            )}
          </div>

          {overdueCount > 0 && (
            <div className="mt-4 p-3 rounded-xl bg-error-container/60 text-on-error-container text-xs flex flex-wrap items-center justify-between gap-2">
              <span className="font-semibold">
                {overdueCount} task{overdueCount === 1 ? ' is' : 's are'} behind schedule. Re-pacing moves your whole plan forward without losing progress.
              </span>
              <button
                type="button"
                onClick={handleRepace}
                disabled={replanning}
                className="px-3 py-1.5 rounded-lg bg-surface-container-lowest text-on-surface font-bold hover:brightness-95 transition-all"
              >
                {replanning ? 'Re-pacing…' : 'Re-pace now'}
              </button>
            </div>
          )}

          {/* Schedule Metrics Grid: Day-wise, Date-wise, Hour-wise */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4 pt-1">
            <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 flex items-center gap-2.5">
              <Calendar className="w-4 h-4 text-primary" />
              <div className="text-xs">
                <span className="text-on-surface-variant block text-[10px] font-bold uppercase">Schedule Window</span>
                <span className="font-bold text-on-surface">{scheduleWindow || `${roadmap.duration_weeks} weeks`}</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 flex items-center gap-2.5">
              <Clock className="w-4 h-4 text-secondary-container" />
              <div className="text-xs">
                <span className="text-on-surface-variant block text-[10px] font-bold uppercase">Daily Target</span>
                <span className="font-bold text-on-surface">{dailyHours} hrs/day (5 study days/wk)</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 flex items-center gap-2.5">
              <TrendingUp className="w-4 h-4 text-primary" />
              <div className="text-xs">
                <span className="text-on-surface-variant block text-[10px] font-bold uppercase">Time Remaining</span>
                <span className="font-bold text-on-surface">
                  ~{(allTasks.filter((t) => t.status === 'NOT_STARTED' || t.status === 'IN_PROGRESS').reduce((acc, t) => acc + t.estimated_minutes, 0) / 60).toFixed(1)} hrs of study left
                </span>
              </div>
            </div>
          </div>

          {/* Route Reasoning Explanation Banner */}
          {roadmap.route_reasoning && (
            <div className="mt-4 p-3.5 rounded-xl bg-surface-container-low border-l-4 border-primary text-xs text-on-surface leading-relaxed flex items-start gap-2.5">
              <Sparkles className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-primary mr-1">Why your route looks like this:</span>
                <span>{roadmap.route_reasoning}</span>
              </div>
            </div>
          )}
        </div>

        {/* Main Content Grid: Milestones Timeline (8 cols) + Resource & Preference Corner (4 cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Milestones Column (8 cols) */}
          <div className="lg:col-span-8 space-y-4">
            <h2 className="text-sm uppercase tracking-wider font-bold text-on-surface-variant mb-2">
Your plan, week by week
            </h2>

            {roadmap.milestones.map((milestone) => {
              const isExpanded = expandedMilestoneId === milestone.id;
              const doneCount = milestone.tasks.filter((t) => t.status === 'COMPLETED' || t.status === 'SKIPPED').length;
              const allDone = milestone.tasks.length > 0 && doneCount === milestone.tasks.length;
              return (
                <div
                  key={milestone.id}
                  className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm overflow-hidden"
                >
                  {/* Milestone Header */}
                  <div
                    onClick={() => setExpandedMilestoneId(isExpanded ? null : milestone.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setExpandedMilestoneId(isExpanded ? null : milestone.id);
                      }
                    }}
                    role="button"
                    tabIndex={0}
                    aria-expanded={isExpanded}
                    className="p-5 flex items-center justify-between gap-3 cursor-pointer hover:bg-surface-container-low/40 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center font-bold text-xs ${
                        allDone 
                          ? 'bg-primary text-on-primary' 
                          : 'bg-primary-fixed/50 text-primary'
                      }`}>
                        {allDone ? <CheckCircle className="w-4 h-4" /> : milestone.week_number}
                      </div>
                      <div>
                        <div className="text-base font-bold text-on-surface">{milestone.title}</div>
                        {formatDateRange(milestone.tasks.map((t) => t.due_date)) && (
                          <div className="text-[11px] font-semibold text-primary flex items-center gap-1">
                            <Calendar className="w-3 h-3" /> {formatDateRange(milestone.tasks.map((t) => t.due_date))}
                          </div>
                        )}
                        <p className="hidden sm:block text-xs text-on-surface-variant">{milestone.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${allDone ? 'bg-primary-fixed/60 text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
                        {doneCount}/{milestone.tasks.length}
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-on-surface-variant" /> : <ChevronDown className="w-4 h-4 text-on-surface-variant" />}
                    </div>
                  </div>

                  {/* Tasks List */}
                  {isExpanded && (
                    <div className="px-5 pb-5 pt-1 border-t border-outline-variant/30 space-y-3">
                      {milestone.tasks.map((task) => (
                        <div
                          key={task.id}
                          onClick={() => setSelectedTask(task)}
                          className={`p-4 rounded-xl border transition-all cursor-pointer ${
                            selectedTask?.id === task.id ? 'ring-2 ring-primary/40 ' : ''
                          }${
                            task.status === 'COMPLETED' || task.status === 'SKIPPED'
                              ? 'bg-surface-container-low/50 border-outline-variant/40 opacity-75'
                              : task.id === nextTask?.id
                              ? 'bg-secondary-fixed/20 border-secondary-container'
                              : 'bg-surface-container-lowest border-outline-variant/60 hover:border-outline'
                          }`}
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase whitespace-nowrap ${
                                task.status === 'COMPLETED' ? 'bg-primary/10 text-primary' :
                                task.id === nextTask?.id ? 'bg-secondary-container text-on-primary' :
                                'bg-surface-container text-on-surface-variant'
                              }`}>
                                {task.status === 'COMPLETED' ? 'Done' : task.status === 'SKIPPED' ? 'Skipped' : task.id === nextTask?.id ? (task.status === 'IN_PROGRESS' ? 'In progress' : 'Up next') : 'Upcoming'}
                              </span>
                              <span className="text-xs font-bold text-on-surface">{task.title}</span>
                              {task.due_date && (
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  isOverdue(task.due_date, task.status)
                                    ? 'bg-error-container text-on-error-container'
                                    : 'bg-surface-container text-on-surface-variant'
                                }`}>
                                  {isOverdue(task.due_date, task.status) ? 'Overdue · ' : 'Due '}{formatDueDate(task.due_date)}
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-on-surface-variant font-semibold flex items-center gap-1 bg-surface-container-low px-2 py-0.5 rounded">
                              <Clock className="w-3.5 h-3.5 text-primary" /> {task.estimated_minutes} min (~{(task.estimated_minutes / 60.0).toFixed(1)} hrs)
                            </span>
                          </div>

                          <p className="text-xs text-on-surface-variant mb-3">{task.description}</p>

                          {/* Task Resources Bar */}
                          {task.resources && task.resources.length > 0 && (
                            <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-2 border-t border-outline-variant/30">
                              <span>{task.resources.length} curated resource{task.resources.length === 1 ? '' : 's'}</span>
                              <Link
                                to={`/learn/${task.id}`}
                                onClick={(e) => e.stopPropagation()}
                                className="text-primary font-bold flex items-center gap-1 hover:underline"
                              >
                                {task.status === 'COMPLETED' || task.status === 'SKIPPED' ? 'Review' : task.status === 'IN_PROGRESS' ? 'Resume' : 'Start'} <Play className="w-3 h-3" />
                              </Link>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Active Resources & Preferences Corner (4 cols) */}
          <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-20 lg:self-start">
            
            {/* Selected Task Inspection Drawer */}
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6">
              <h3 className="text-xs uppercase tracking-wider font-bold text-primary mb-3">
                {selectedTask && selectedTask.id === nextTask?.id ? 'Your next task' : 'Task details'}
              </h3>

              {selectedTask ? (
                <div>
                  <h2 className="text-base font-bold text-on-surface mb-2">{selectedTask.title}</h2>
                  <p className="text-xs text-on-surface-variant mb-3">{selectedTask.description}</p>

                  {selectedTask.reason_why_next && (
                    <div className="p-3 rounded-xl bg-surface-container-low text-xs text-on-surface-variant mb-4">
                      <strong className="text-primary block mb-0.5">Schedule</strong>
                      {selectedTask.due_date && <span className="block font-semibold text-on-surface">Due {formatDueDate(selectedTask.due_date)}</span>}
                      {selectedTask.reason_why_next}
                    </div>
                  )}

                  <h4 className="text-xs font-bold text-on-surface uppercase mb-2">Curated Resources</h4>
                  <div className="space-y-2 mb-4">
                    {selectedTask.resources.map((res) => (
                      <a
                        key={res.resource_id}
                        href={res.url}
                        target="_blank"
                        rel="noreferrer"
                        className="block p-2.5 rounded-xl bg-surface-container-low hover:bg-surface-container transition-colors text-xs"
                      >
                        <div className="flex items-center justify-between font-semibold text-on-surface mb-1">
                          <span className="truncate">{res.title}</span>
                          <span className="text-[10px] text-primary bg-primary-fixed/40 px-1.5 py-0.5 rounded font-bold">
                            {intToPercent(res.recommendation_match_score)}%
                          </span>
                        </div>
                        <div className="text-[11px] text-on-surface-variant flex items-center justify-between">
                          <span>{res.provider} • {res.resource_type}</span>
                          <span>{res.duration_minutes}m</span>
                        </div>
                      </a>
                    ))}
                  </div>

                  <Link
                    to={`/learn/${selectedTask.id}`}
                    className="w-full inline-flex items-center justify-center gap-2 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm"
                  >
                    <Play className="w-4 h-4" />
                    <span>{selectedTask.status === 'COMPLETED' || selectedTask.status === 'SKIPPED' ? 'Review this task' : 'Start learning session'}</span>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-on-surface-variant">
                  <BookOpen className="w-7 h-7 text-outline mx-auto mb-2" />
                  <p>Select a task to see its schedule and resources.</p>
                </div>
              )}
            </div>

            {/* RESOURCE PREFERENCES & STACK CORNER */}
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6">
              <div className="flex items-center justify-between mb-3 border-b border-outline-variant/40 pb-3">
                <h3 className="text-xs uppercase tracking-wider font-bold text-primary flex items-center gap-1.5">
                  <Bookmark className="w-4 h-4" /> Resources in your roadmap
                </h3>
              </div>

              {/* Format Preference Toggles */}
              <div className="mb-4">
                <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider block mb-2">
                  Filter by format
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { key: 'VIDEO', label: '📹 Video', icon: Video },
                    { key: 'DOCUMENTATION', label: '📖 Docs', icon: BookOpen },
                    { key: 'PRACTICE', label: '💻 Practice', icon: Code },
                    { key: 'ARTICLE', label: '📄 Articles', icon: FileText }
                  ].map(({ key, label }) => {
                    const active = resourcePreferences.includes(key);
                    return (
                      <button
                        key={key}
                        onClick={() => togglePreference(key)}
                        aria-pressed={active}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                          active
                            ? 'bg-primary text-on-primary shadow-sm'
                            : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                        }`}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Active Resources Being Used Across Roadmap */}
              <div>
                <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider block mb-2">
                  {visibleResources.length} of {allActiveResources.length} resources
                </span>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {visibleResources.length === 0 && (
                    <p className="text-xs text-on-surface-variant py-3">No resources in the selected formats.</p>
                  )}
                  {visibleResources.map((res) => (
                    <a
                      key={res.resource_id}
                      href={res.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block p-2.5 rounded-xl bg-surface-container-low hover:bg-surface-container transition-colors text-xs"
                    >
                      <div className="font-bold text-on-surface truncate mb-0.5">{res.title}</div>
                      <div className="flex items-center justify-between text-[11px] text-on-surface-variant">
                        <span className="bg-surface-container px-1.5 py-0.5 rounded text-[10px]">{res.provider}</span>
                        <span>{res.duration_minutes}m • {intToPercent(res.recommendation_match_score)}% match</span>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
};

function intToPercent(score: number): number {
  if (score > 1.0) return Math.min(99, Math.round(score));
  return Math.min(99, Math.round(score * 100));
}
