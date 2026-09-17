import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Target, CheckCircle2, ArrowRight, ArrowLeft, Clock, Sparkles, 
  BookOpen, Video, Code, FileText, Check, HelpCircle 
} from 'lucide-react';
import { apiClient } from '../api/client';

const GOAL_PRESETS = [
  { 
    title: "Become a Machine Learning Engineer", 
    domain: "Machine Learning", 
    desc: "Master ML algorithms, model validation, feature engineering, and MLOps deployment.",
    defaultSkills: [
      { skill_name: "Python Architecture", self_reported_level: "Advanced" },
      { skill_name: "SQL & Analytical Queries", self_reported_level: "Intermediate" }
    ]
  },
  { 
    title: "Become a Data Scientist", 
    domain: "Data Science", 
    desc: "Master EDA, statistics, pandas, regression models, and data storytelling.",
    defaultSkills: [
      { skill_name: "Python Architecture", self_reported_level: "Intermediate" },
      { skill_name: "Exploratory Data Analysis", self_reported_level: "Familiar" }
    ]
  },
  { 
    title: "Become a Backend Developer", 
    domain: "Backend", 
    desc: "Master Python REST APIs, PostgreSQL ORM hygiene, Docker, and async concurrency.",
    defaultSkills: [
      { skill_name: "Python Architecture", self_reported_level: "Advanced" },
      { skill_name: "RESTful API Architecture", self_reported_level: "Intermediate" }
    ]
  },
  { 
    title: "Learn React & TypeScript", 
    domain: "Frontend", 
    desc: "Master modern component architecture, state management, and TypeScript integrations.",
    defaultSkills: [
      { skill_name: "JavaScript Fundamentals & ES6+", self_reported_level: "Advanced" },
      { skill_name: "React Component Architecture", self_reported_level: "Familiar" }
    ]
  },
  { 
    title: "Learn Data Engineering", 
    domain: "Data Engineering", 
    desc: "Master SQL pipelines, ETL architecture, data warehouses, and orchestration.",
    defaultSkills: [
      { skill_name: "SQL & Analytical Queries", self_reported_level: "Advanced" },
      { skill_name: "Python Architecture", self_reported_level: "Intermediate" }
    ]
  }
];

const SKILL_LEVELS = ["Beginner", "Familiar", "Intermediate", "Advanced", "Expert"];

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(1);
  const [goal, setGoal] = useState<string>("Become a Machine Learning Engineer");
  const [knownSkills, setKnownSkills] = useState<{ skill_name: string; self_reported_level: string }[]>([
    { skill_name: "Python Architecture", self_reported_level: "Advanced" },
    { skill_name: "SQL & Analytical Queries", self_reported_level: "Intermediate" }
  ]);
  const [customSkillName, setCustomSkillName] = useState("");
  const [hoursPerWeek, setHoursPerWeek] = useState<number>(10);
  const [durationWeeks, setDurationWeeks] = useState<number>(12);
  const [preferences, setPreferences] = useState<string[]>(["VIDEO", "DOCUMENTATION", "PRACTICE"]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Goal-Specific Diagnostic Questions State
  const [diagnosticQuestions, setDiagnosticQuestions] = useState<any[]>([]);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, number>>({});
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  // When goal changes, update pre-filled known skills & fetch goal-specific quiz
  const handleSelectGoal = (selectedGoal: string, defaultSkills?: any[]) => {
    setGoal(selectedGoal);
    if (defaultSkills && defaultSkills.length > 0) {
      setKnownSkills(defaultSkills);
    }
  };

  useEffect(() => {
    if (step === 3) {
      fetchDiagnosticQuestions();
    }
  }, [step, goal]);

  const fetchDiagnosticQuestions = async () => {
    setLoadingQuiz(true);
    try {
      const res: any = await apiClient.get(`/assessments/diagnostic-by-goal?goal=${encodeURIComponent(goal)}`);
      setDiagnosticQuestions(res.questions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleAddSkill = () => {
    if (!customSkillName.trim()) return;
    setKnownSkills([...knownSkills, { skill_name: customSkillName.trim(), self_reported_level: "Familiar" }]);
    setCustomSkillName("");
  };

  const handleRemoveSkill = (index: number) => {
    setKnownSkills(knownSkills.filter((_, i) => i !== index));
  };

  const handleLevelChange = (index: number, level: string) => {
    const updated = [...knownSkills];
    updated[index].self_reported_level = level;
    setKnownSkills(updated);
  };

  const togglePreference = (pref: string) => {
    if (preferences.includes(pref)) {
      setPreferences(preferences.filter(p => p !== pref));
    } else {
      setPreferences([...preferences, pref]);
    }
  };

  const handleGenerateRoadmap = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      let token = localStorage.getItem('skillalpha_token');
      if (!token) {
        const regRes: any = await apiClient.post('/auth/register', {
          email: `learner_${Date.now()}@skillalpha.io`,
          password: 'password123',
          full_name: 'Learner'
        });
        token = regRes.access_token;
        localStorage.setItem('skillalpha_token', token);
      }

      const res: any = await apiClient.post('/roadmaps', {
        goal,
        known_skills: knownSkills,
        available_hours: hoursPerWeek,
        duration_weeks: durationWeeks,
        learning_preferences: preferences
      });

      navigate(`/roadmap/${res.id}`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to generate roadmap. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        
        {/* Step Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-xs font-semibold text-on-surface-variant mb-2">
            <span>STEP {step} OF 4</span>
            <span className="text-primary font-bold">
              {step === 1 && "Target Goal"}
              {step === 2 && "Knowledge Baseline"}
              {step === 3 && `Diagnostic Check (${goal.split(' ')[0]} Specific)`}
              {step === 4 && "Pace & Preferences"}
            </span>
          </div>
          <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary-container transition-all duration-300"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-error-container text-on-error-container text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        {/* STEP 1: What are you trying to achieve? */}
        {step === 1 && (
          <div className="bg-surface-container-lowest rounded-2xl p-6 sm:p-8 border border-outline-variant/60 shadow-sm">
            <div className="mb-6">
              <span className="text-xs uppercase tracking-wider text-secondary font-bold block mb-1">Step 01</span>
              <h1 className="text-2xl font-extrabold text-on-surface">What are you trying to achieve?</h1>
              <p className="text-sm text-on-surface-variant mt-1">Select a target career objective or type your custom learning goal.</p>
            </div>

            <div className="space-y-3 mb-6">
              {GOAL_PRESETS.map((preset) => {
                const selected = goal === preset.title;
                return (
                  <div
                    key={preset.title}
                    onClick={() => handleSelectGoal(preset.title, preset.defaultSkills)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selected
                        ? 'border-primary bg-surface-container-low/70 ring-1 ring-primary'
                        : 'border-outline-variant/60 hover:border-outline hover:bg-surface-container-low/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-bold text-sm text-on-surface">{preset.title}</div>
                      <span className="text-[10px] font-semibold text-primary bg-primary-fixed/40 px-2 py-0.5 rounded">
                        {preset.domain}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1">{preset.desc}</p>
                  </div>
                );
              })}
            </div>

            {/* Custom Goal Input */}
            <div className="mb-8">
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                Or enter custom goal
              </label>
              <input
                type="text"
                value={goal}
                onChange={(e) => handleSelectGoal(e.target.value)}
                placeholder="e.g. Master PyTorch for Computer Vision"
                className="w-full h-11 px-3.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-sm text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!goal.trim()}
              className="w-full flex items-center justify-center gap-2 h-12 rounded-xl bg-secondary-container text-on-primary font-bold text-sm hover:brightness-105 transition-all shadow-sm"
            >
              <span>Continue to Knowledge Baseline</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* STEP 2: What do you already know? */}
        {step === 2 && (
          <div className="bg-surface-container-lowest rounded-2xl p-6 sm:p-8 border border-outline-variant/60 shadow-sm">
            <div className="mb-6">
              <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">Step 02</span>
              <h1 className="text-2xl font-extrabold text-on-surface">What do you already know?</h1>
              <p className="text-sm text-on-surface-variant mt-1">
                Tell SkillAlpha what skills you've already learned for <strong className="text-primary font-bold">{goal}</strong> so introductory modules can be safely bypassed.
              </p>
            </div>

            {/* Added Skills List */}
            <div className="space-y-3 mb-6">
              {knownSkills.map((sk, idx) => (
                <div key={idx} className="flex items-center justify-between p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/40">
                  <div className="font-semibold text-xs text-on-surface">{sk.skill_name}</div>
                  <div className="flex items-center gap-2">
                    <select
                      value={sk.self_reported_level}
                      onChange={(e) => handleLevelChange(idx, e.target.value)}
                      className="h-8 px-2 rounded border border-outline-variant/60 bg-surface-container-lowest text-xs text-on-surface focus:outline-none"
                    >
                      {SKILL_LEVELS.map(lvl => (
                        <option key={lvl} value={lvl}>{lvl}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => handleRemoveSkill(idx)}
                      className="text-xs text-error hover:underline px-1"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Add Custom Skill */}
            <div className="flex items-center gap-2 mb-8">
              <input
                type="text"
                value={customSkillName}
                onChange={(e) => setCustomSkillName(e.target.value)}
                placeholder={`Add another skill relevant to ${goal}`}
                className="flex-1 h-10 px-3 rounded-lg border border-outline-variant/60 text-xs text-on-surface focus:outline-none focus:border-primary"
              />
              <button
                type="button"
                onClick={handleAddSkill}
                className="h-10 px-4 rounded-lg bg-primary text-on-primary text-xs font-semibold hover:bg-primary-container transition-colors"
              >
                Add Skill
              </button>
            </div>

            <div className="flex items-center justify-between gap-4 pt-4 border-t border-outline-variant/40">
              <button
                onClick={() => setStep(1)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg border border-outline-variant/60 text-xs font-semibold text-on-surface hover:bg-surface-container-low"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all"
              >
                <span>Continue to Diagnostic Check</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Goal-Specific Diagnostic Baseline Check */}
        {step === 3 && (
          <div className="bg-surface-container-lowest rounded-2xl p-6 sm:p-8 border border-outline-variant/60 shadow-sm">
            <div className="mb-6">
              <span className="text-xs uppercase tracking-wider text-secondary font-bold block mb-1">Step 03</span>
              <h1 className="text-2xl font-extrabold text-on-surface">Diagnostic Baseline Check</h1>
              <p className="text-sm text-on-surface-variant mt-1">
                Diagnostic questions tailored specifically for <strong className="text-primary font-bold">{goal}</strong> so we don't rely strictly on self-reported ratings.
              </p>
            </div>

            {loadingQuiz ? (
              <div className="py-12 text-center text-xs text-on-surface-variant font-semibold">
                Loading goal-specific diagnostic questions...
              </div>
            ) : (
              <div className="space-y-6 mb-8">
                {diagnosticQuestions.map((q, qIdx) => (
                  <div key={q.id} className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/40">
                    <div className="text-xs font-bold text-primary uppercase mb-1">
                      Question {qIdx + 1} • {q.title}
                    </div>
                    <div className="text-sm font-semibold text-on-surface mb-3">
                      {q.question_text}
                    </div>
                    <div className="space-y-2 text-xs">
                      {q.options.map((optText: string, oIdx: number) => (
                        <label
                          key={oIdx}
                          className="flex items-center gap-2 p-2.5 rounded-lg bg-surface-container-lowest border border-outline-variant/40 cursor-pointer hover:border-primary transition-colors"
                        >
                          <input
                            type="radio"
                            name={`q_${q.id}`}
                            checked={quizAnswers[q.id] === oIdx}
                            onChange={() => setQuizAnswers({ ...quizAnswers, [q.id]: oIdx })}
                            className="accent-primary"
                          />
                          <span className="text-on-surface">{optText}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-center justify-between gap-4 pt-4 border-t border-outline-variant/40">
              <button
                onClick={() => setStep(2)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg border border-outline-variant/60 text-xs font-semibold text-on-surface hover:bg-surface-container-low"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                onClick={() => setStep(4)}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all"
              >
                <span>Continue to Pace & Preferences</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: Pace & Preferences */}
        {step === 4 && (
          <div className="bg-surface-container-lowest rounded-2xl p-6 sm:p-8 border border-outline-variant/60 shadow-sm">
            <div className="mb-6">
              <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">Step 04</span>
              <h1 className="text-2xl font-extrabold text-on-surface">Pace & Format Preferences</h1>
              <p className="text-sm text-on-surface-variant mt-1">
                Configure your available weekly commitment and preferred learning mediums.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
              <div>
                <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                  Weekly Commitment
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="3"
                    max="30"
                    value={hoursPerWeek}
                    onChange={(e) => setHoursPerWeek(Number(e.target.value))}
                    className="w-full accent-primary"
                  />
                  <span className="text-sm font-bold text-primary min-w-[70px]">{hoursPerWeek} hrs/wk</span>
                </div>
                <span className="text-[11px] text-on-surface-variant mt-1 block">
                  Daily Allocation: ~{(hoursPerWeek / 5.0).toFixed(1)} hrs/day (5 study days/wk)
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                  Target Duration
                </label>
                <select
                  value={durationWeeks}
                  onChange={(e) => setDurationWeeks(Number(e.target.value))}
                  className="w-full h-11 px-3 rounded-lg border border-outline-variant/60 text-sm text-on-surface bg-surface-container-lowest"
                >
                  <option value={4}>4 Weeks (Accelerated Sprint)</option>
                  <option value={8}>8 Weeks (Balanced Pace)</option>
                  <option value={12}>12 Weeks (Standard Mastery)</option>
                  <option value={16}>16 Weeks (In-Depth Path)</option>
                </select>
              </div>
            </div>

            <div className="mb-8">
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-3">
                Preferred Resource Formats
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { key: 'VIDEO', label: 'Video Walkthroughs', icon: Video },
                  { key: 'DOCUMENTATION', label: 'Official Docs', icon: BookOpen },
                  { key: 'PRACTICE', label: 'Interactive Notebooks', icon: Code },
                  { key: 'ARTICLE', label: 'Technical Articles', icon: FileText }
                ].map(({ key, label, icon: Icon }) => {
                  const active = preferences.includes(key);
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => togglePreference(key)}
                      className={`p-3 rounded-xl border text-left flex items-center gap-2.5 transition-colors ${
                        active
                          ? 'border-primary bg-primary-fixed/30 text-primary font-semibold'
                          : 'border-outline-variant/60 text-on-surface-variant hover:border-outline'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-xs">{label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center justify-between gap-4 pt-4 border-t border-outline-variant/40">
              <button
                onClick={() => setStep(3)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg border border-outline-variant/60 text-xs font-semibold text-on-surface hover:bg-surface-container-low"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                onClick={handleGenerateRoadmap}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-7 py-3 rounded-xl bg-secondary-container text-on-primary font-bold text-sm hover:brightness-105 transition-all shadow-sm"
              >
                {isSubmitting ? (
                  <span>Generating your learning path...</span>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Build My Learning Path</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
