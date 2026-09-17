import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Flag, Clock as Schedule, TrendingUp, CheckCircle, Clock, BookOpen, 
  ExternalLink, RefreshCw, ChevronDown, ChevronUp, Play, Sparkles, 
  Calendar, Layers, Video, Code, FileText, Settings, Bookmark 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { Roadmap, RoadmapMilestone, RoadmapTask } from '../types';

export const RoadmapPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [replanning, setReplanning] = useState(false);
  const [expandedMilestoneId, setExpandedMilestoneId] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<RoadmapTask | null>(null);

  // Active Resource Preferences Corner State
  const [resourcePreferences, setResourcePreferences] = useState<string[]>([
    'VIDEO', 'DOCUMENTATION', 'PRACTICE'
  ]);

  const togglePreference = (pref: string) => {
    if (resourcePreferences.includes(pref)) {
      setResourcePreferences(resourcePreferences.filter(p => p !== pref));
    } else {
      setResourcePreferences([...resourcePreferences, pref]);
    }
  };

  const fetchRoadmap = async () => {
    setLoading(true);
    try {
      if (id === 'active' || !id) {
        const roadmaps: any = await apiClient.get('/roadmaps');
        if (roadmaps && roadmaps.length > 0) {
          setRoadmap(roadmaps[0]);
          if (roadmaps[0].milestones && roadmaps[0].milestones.length > 0) {
            setExpandedMilestoneId(roadmaps[0].milestones[0].id);
          }
        }
      } else {
        const res: any = await apiClient.get(`/roadmaps/${id}`);
        setRoadmap(res);
        if (res.milestones && res.milestones.length > 0) {
          setExpandedMilestoneId(res.milestones[0].id);
        }
      }
    } catch (err) {
      console.error(err);
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
    } catch (err) {
      console.error(err);
    } finally {
      setReplanning(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full pt-28 pb-16 flex items-center justify-center min-h-screen text-on-surface-variant">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-primary" />
          <span className="text-sm font-semibold">Loading your day-by-day personalized roadmap...</span>
        </div>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="w-full pt-28 pb-16 max-w-3xl mx-auto px-4 text-center">
        <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 shadow-sm">
          <h2 className="text-xl font-bold text-on-surface mb-2">No active roadmap found</h2>
          <p className="text-sm text-on-surface-variant mb-6">Create a new personalized path to get started.</p>
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

  // Calculate dates for header schedule banner
  const startDate = new Date();
  const endDate = new Date();
  endDate.setDate(startDate.getDate() + (roadmap.duration_weeks * 7));

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

          {/* Schedule Metrics Grid: Day-wise, Date-wise, Hour-wise */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4 pt-1">
            <div className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 flex items-center gap-2.5">
              <Calendar className="w-4 h-4 text-primary" />
              <div className="text-xs">
                <span className="text-on-surface-variant block text-[10px] font-bold uppercase">Schedule Window</span>
                <span className="font-bold text-on-surface">
                  {startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – {endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
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
                <span className="text-on-surface-variant block text-[10px] font-bold uppercase">Overall Completion</span>
                <span className="font-bold text-primary">{roadmap.progress_percent}% ({roadmap.completed_tasks}/{roadmap.total_tasks} tasks done)</span>
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
              Day-by-Day Curriculum Sequence ({roadmap.milestones.length} Milestones)
            </h2>

            {roadmap.milestones.map((milestone) => {
              const isExpanded = expandedMilestoneId === milestone.id;
              return (
                <div
                  key={milestone.id}
                  className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm overflow-hidden"
                >
                  {/* Milestone Header */}
                  <div
                    onClick={() => setExpandedMilestoneId(isExpanded ? null : milestone.id)}
                    className="p-5 flex items-center justify-between cursor-pointer hover:bg-surface-container-low/40 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${
                        milestone.is_completed 
                          ? 'bg-primary text-on-primary' 
                          : 'bg-primary-fixed/50 text-primary'
                      }`}>
                        {milestone.week_number}
                      </div>
                      <div>
                        <div className="text-base font-bold text-on-surface">{milestone.title}</div>
                        <p className="text-xs text-on-surface-variant">{milestone.description}</p>
                      </div>
                    </div>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-on-surface-variant" /> : <ChevronDown className="w-4 h-4 text-on-surface-variant" />}
                  </div>

                  {/* Tasks List */}
                  {isExpanded && (
                    <div className="px-5 pb-5 pt-1 border-t border-outline-variant/30 space-y-3">
                      {milestone.tasks.map((task) => (
                        <div
                          key={task.id}
                          onClick={() => setSelectedTask(task)}
                          className={`p-4 rounded-xl border transition-all cursor-pointer ${
                            task.status === 'COMPLETED'
                              ? 'bg-surface-container-low/50 border-outline-variant/40 opacity-75'
                              : task.status === 'IN_PROGRESS'
                              ? 'bg-secondary-fixed/20 border-secondary-container'
                              : 'bg-surface-container-lowest border-outline-variant/60 hover:border-outline'
                          }`}
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                task.status === 'COMPLETED' ? 'bg-primary/10 text-primary' :
                                task.status === 'IN_PROGRESS' ? 'bg-secondary-container text-on-primary' :
                                'bg-surface-container text-on-surface-variant'
                              }`}>
                                {task.status.replace('_', ' ')}
                              </span>
                              <span className="text-xs font-bold text-on-surface">{task.title}</span>
                            </div>
                            <span className="text-xs text-on-surface-variant font-semibold flex items-center gap-1 bg-surface-container-low px-2 py-0.5 rounded">
                              <Clock className="w-3.5 h-3.5 text-primary" /> {task.estimated_minutes} min (~{(task.estimated_minutes / 60.0).toFixed(1)} hrs)
                            </span>
                          </div>

                          <p className="text-xs text-on-surface-variant mb-3">{task.description}</p>

                          {/* Task Resources Bar */}
                          {task.resources && task.resources.length > 0 && (
                            <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-2 border-t border-outline-variant/30">
                              <span>{task.resources.length} Curated Resources</span>
                              <span className="text-primary font-semibold flex items-center gap-1">
                                Inspect Task Resources <ExternalLink className="w-3 h-3" />
                              </span>
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
          <div className="lg:col-span-4 space-y-6">
            
            {/* Selected Task Inspection Drawer */}
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6">
              <h3 className="text-xs uppercase tracking-wider font-bold text-primary mb-3">
                Selected Task Inspection
              </h3>

              {selectedTask ? (
                <div>
                  <h2 className="text-base font-bold text-on-surface mb-2">{selectedTask.title}</h2>
                  <p className="text-xs text-on-surface-variant mb-3">{selectedTask.description}</p>

                  {selectedTask.reason_why_next && (
                    <div className="p-3 rounded-xl bg-surface-container-low text-xs text-on-surface-variant mb-4">
                      <strong className="text-primary block mb-0.5">Day & Hour Schedule:</strong>
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
                    to="/learn"
                    className="w-full inline-flex items-center justify-center gap-2 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start Learning Session</span>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-on-surface-variant">
                  <BookOpen className="w-7 h-7 text-outline mx-auto mb-2" />
                  <p>Click any task in the sequence to inspect its day/hour schedule and resources.</p>
                </div>
              )}
            </div>

            {/* RESOURCE PREFERENCES & STACK CORNER */}
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6">
              <div className="flex items-center justify-between mb-3 border-b border-outline-variant/40 pb-3">
                <h3 className="text-xs uppercase tracking-wider font-bold text-primary flex items-center gap-1.5">
                  <Bookmark className="w-4 h-4" /> Resource Stack & Preferences Corner
                </h3>
              </div>

              {/* Format Preference Toggles */}
              <div className="mb-4">
                <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider block mb-2">
                  Active Resource Preferences
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
                  Curated Resources in Your Roadmap ({allActiveResources.length})
                </span>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {allActiveResources.map((res) => (
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
