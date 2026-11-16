import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, Clock, Database, ExternalLink, Hammer, ChevronDown, ChevronUp } from 'lucide-react';
import { apiClient } from '../api/client';
import { Project } from '../types';
import { PageSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

interface ProjectListResponse {
  family: string;
  own_family: string | null;
  families: { key: string; label: string }[];
  projects: Project[];
  completed: number;
}

interface Draft {
  url: string;
  notes: string;
  checklist: boolean[];
}

const LEVEL_LABEL: Record<Project['level'], string> = { BEGINNER: 'Beginner', INTERMEDIATE: 'Intermediate', ADVANCED: 'Advanced' };
const LEVEL_STYLE: Record<Project['level'], string> = {
  BEGINNER: 'bg-primary-fixed/50 text-primary',
  INTERMEDIATE: 'bg-secondary-fixed text-on-secondary-container',
  ADVANCED: 'bg-error-container text-on-error-container',
};

const draftFor = (project: Project): Draft => ({
  url: project.submission?.url || '',
  notes: project.submission?.notes || '',
  checklist: project.submission?.checklist || project.rubric.map(() => false),
});

export const ProjectsPage: React.FC = () => {
  const toast = useToast();
  const [data, setData] = useState<ProjectListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [family, setFamily] = useState<string>('');
  const [openId, setOpenId] = useState<string | null>(() => new URLSearchParams(window.location.search).get('project'));
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  const load = async (nextFamily: string, showSpinner: boolean) => {
    if (showSpinner) setLoading(true);
    try {
      const res: any = await apiClient.get(nextFamily ? `/projects?family=${nextFamily}` : '/projects');
      setData(res);
    } catch (err: any) {
      toast.error(err.message || 'Could not load projects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(family, data === null);
  }, [family]);

  const getDraft = (project: Project): Draft => drafts[project.id] || draftFor(project);
  const setDraft = (project: Project, patch: Partial<Draft>) =>
    setDrafts((prev) => ({ ...prev, [project.id]: { ...getDraft(project), ...patch } }));

  const handleSubmit = async (project: Project) => {
    const draft = getDraft(project);
    if (!/^https?:\/\/\S+$/.test(draft.url.trim())) {
      toast.error('Enter a full link to your work, starting with https://');
      return;
    }
    setSavingId(project.id);
    try {
      const res: any = await apiClient.post(`/projects/${project.id}/submit`, {
        url: draft.url.trim(),
        notes: draft.notes.trim() || null,
        checklist: draft.checklist,
      });
      setData((prev) => {
        if (!prev) return prev;
        const projects = prev.projects.map((p) => (p.id === project.id ? { ...p, submission: res.submission } : p));
        return { ...prev, projects, completed: projects.filter((p) => p.submission?.passed).length };
      });
      setDrafts((prev) => {
        const next = { ...prev };
        delete next[project.id];
        return next;
      });
      if (res.passed) {
        toast.success(res.task_completed ? 'Project passed. The project task on your roadmap is now complete.' : 'Project passed. Nice work!');
      } else {
        toast.info(`Saved. Meet ${res.items_needed} of ${project.rubric.length} checklist items to pass, then resubmit.`);
      }
    } catch (err: any) {
      toast.error(err.message || 'Could not save your submission.');
    } finally {
      setSavingId(null);
    }
  };

  if (loading) return <PageSkeleton variant="cards" label="Loading projects" />;
  if (!data) return null;

  const selected = family || (data.family !== 'all' ? data.family : 'all');

  return (
    <div className="w-full pt-20 pb-24 bg-surface min-h-screen">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3 mb-6">
          <div className="max-w-2xl">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface flex items-center gap-2">
              <Hammer className="w-6 h-6 text-primary" /> Projects
            </h1>
            <p className="text-sm text-on-surface-variant mt-1">
              Real datasets, a clear brief and a checklist to grade yourself against. Build it, put it on GitHub or Kaggle, and submit the link.
              Each roadmap phase ends with one of these.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold text-on-surface-variant whitespace-nowrap">{data.completed} of {data.projects.length} passed</span>
            <select
              aria-label="Project track"
              value={selected}
              onChange={(e) => setFamily(e.target.value)}
              className="h-9 px-2 rounded-lg border border-outline-variant/60 text-xs text-on-surface bg-surface-container-lowest"
            >
              {data.families.map((f) => (
                <option key={f.key} value={f.key}>{f.label}{f.key === data.own_family ? ' (your track)' : ''}</option>
              ))}
              <option value="all">All tracks</option>
            </select>
          </div>
        </div>

        {!data.own_family && (
          <div className="mb-5 p-3 rounded-xl bg-surface-container-low text-xs text-on-surface-variant">
            <Link to="/create" className="text-primary font-bold hover:underline">Build a roadmap</Link> and the projects for your goal are scheduled into it automatically.
          </div>
        )}

        <div className="space-y-4">
          {data.projects.map((project) => {
            const open = openId === project.id;
            const draft = getDraft(project);
            const met = draft.checklist.filter(Boolean).length;
            const passed = !!project.submission?.passed;
            return (
              <article key={project.id} className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm overflow-hidden">
                <button
                  type="button"
                  onClick={() => setOpenId(open ? null : project.id)}
                  aria-expanded={open}
                  className="w-full p-5 text-left hover:bg-surface-container-low/40 transition-colors"
                >
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${LEVEL_STYLE[project.level]}`}>{LEVEL_LABEL[project.level]}</span>
                    {selected === 'all' && <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">{project.family_label}</span>}
                    {passed ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-primary text-on-primary inline-flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Passed</span>
                    ) : project.submission ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">Submitted, not passed yet</span>
                    ) : null}
                    <span className="ml-auto text-[11px] text-on-surface-variant inline-flex items-center gap-1 whitespace-nowrap"><Clock className="w-3.5 h-3.5" /> about {project.estimated_hours} hrs</span>
                    {open ? <ChevronUp className="w-4 h-4 text-on-surface-variant" /> : <ChevronDown className="w-4 h-4 text-on-surface-variant" />}
                  </div>
                  <h2 className="text-base font-bold text-on-surface">{project.title}</h2>
                  <p className="text-xs text-on-surface-variant mt-0.5">{project.summary}</p>
                </button>

                {open && (
                  <div className="px-5 pb-5 border-t border-outline-variant/30 pt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant mb-2">Data</h3>
                      <a href={project.dataset_url} target="_blank" rel="noreferrer" className="flex items-start gap-2 p-3 rounded-xl bg-surface-container-low hover:bg-surface-container text-xs text-on-surface mb-4">
                        <Database className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                        <span className="flex-1">{project.dataset}</span>
                        <ExternalLink className="w-3.5 h-3.5 text-on-surface-variant flex-shrink-0 mt-0.5" />
                      </a>
                      <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant mb-2">What to build</h3>
                      <ol className="space-y-1.5 text-xs text-on-surface list-decimal pl-4 leading-relaxed">
                        {project.brief.map((step) => <li key={step}>{step}</li>)}
                      </ol>
                    </div>

                    <div>
                      <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant mb-2">
                        Grade yourself · {met}/{project.rubric.length} met (pass at {project.pass_items})
                      </h3>
                      <div className="space-y-1.5 mb-4">
                        {project.rubric.map((item, index) => (
                          <label key={item} className="flex items-start gap-2 p-2 rounded-lg bg-surface-container-low text-xs text-on-surface cursor-pointer">
                            <input
                              type="checkbox"
                              checked={!!draft.checklist[index]}
                              onChange={(e) => setDraft(project, { checklist: project.rubric.map((_, i) => (i === index ? e.target.checked : !!draft.checklist[i])) })}
                              className="accent-primary mt-0.5"
                            />
                            <span>{item}</span>
                          </label>
                        ))}
                      </div>
                      <label htmlFor={`url_${project.id}`} className="block text-[11px] font-bold uppercase text-on-surface-variant mb-1">Link to your work</label>
                      <input
                        id={`url_${project.id}`}
                        type="url"
                        placeholder="https://github.com/you/your-project"
                        value={draft.url}
                        onChange={(e) => setDraft(project, { url: e.target.value })}
                        className="w-full h-10 px-3 rounded-lg border border-outline-variant/60 text-sm text-on-surface bg-surface-container-lowest mb-3"
                      />
                      <label htmlFor={`notes_${project.id}`} className="block text-[11px] font-bold uppercase text-on-surface-variant mb-1">Notes (optional)</label>
                      <textarea
                        id={`notes_${project.id}`}
                        rows={2}
                        maxLength={2000}
                        placeholder="What worked, what did not, what you would try next"
                        value={draft.notes}
                        onChange={(e) => setDraft(project, { notes: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-outline-variant/60 text-sm text-on-surface bg-surface-container-lowest mb-3"
                      />
                      <button
                        type="button"
                        onClick={() => handleSubmit(project)}
                        disabled={savingId === project.id || !draft.url.trim()}
                        className="w-full py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 disabled:opacity-50"
                      >
                        {savingId === project.id ? 'Saving…' : project.submission ? 'Update submission' : 'Submit project'}
                      </button>
                    </div>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      </div>
    </div>
  );
};
