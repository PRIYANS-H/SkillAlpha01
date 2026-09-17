import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, PlayCircle, Flag, Clock as Schedule, TrendingUp, CheckCircle, 
  Target, Ruler as Rule, BarChart2 as Analytics, BookOpen as AutoStories, RefreshCw as Sync, FastForward, Crosshair as FilterCenterFocus, 
  Compass as CompassCalibration, Check, Lock as LockClock, Check as Done, ShieldCheck 
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="w-full pt-16 bg-surface min-h-screen">
      {/* Top Subtle Ambient Light Strip */}
      <div className="relative w-full overflow-hidden">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[840px] h-[340px] bg-gradient-to-b from-primary-fixed/25 via-surface-container-low/40 to-transparent blur-3xl pointer-events-none rounded-full" />

        {/* Hero Section */}
        <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 lg:pt-16 lg:pb-28 w-full">
          <div className="flex flex-col items-center text-center max-w-3xl mx-auto">
            {/* Eyebrow Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container-low shadow-sm mb-6 border border-outline-variant/40">
              <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse" />
              <span className="font-sans text-xs uppercase tracking-wider text-primary font-bold">
                Personalized Learning Intelligence
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="font-sans text-4xl sm:text-5xl lg:text-6xl font-extrabold text-on-surface tracking-tight mb-6 leading-[1.15]">
              Everything you need to learn.<br className="hidden sm:inline" />
              <span className="text-primary-container"> In the right order.</span>
            </h1>

            {/* Supporting Copy */}
            <p className="text-base sm:text-lg text-on-surface-variant max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
              SkillAlpha finds the resources you need, skips what you already know, and gives you a clear next step toward your goal.
            </p>

            {/* CTA Cluster */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto mb-16">
              <Link
                to="/create"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-secondary-container text-on-primary text-sm font-bold shadow-sm hover:brightness-105 active:scale-[0.99] transition-all"
              >
                <span>Build my learning path</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#how-it-works"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-surface-container-lowest text-on-surface text-sm font-semibold border border-outline-variant/60 shadow-sm hover:bg-surface-container-low transition-colors"
              >
                <PlayCircle className="w-4 h-4 text-on-surface-variant" />
                <span>Explore how it works</span>
              </a>
            </div>
          </div>

          {/* Hero Visual Mockup */}
          <div className="relative max-w-5xl mx-auto">
            <div className="rounded-2xl bg-surface-container-lowest shadow-xl border border-outline-variant/60 p-5 sm:p-8 relative z-10">
              {/* Mock Header Bar */}
              <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-6 border-b border-outline-variant/40">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary-container/10 flex items-center justify-center text-primary-container">
                    <Flag className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-[11px] text-on-surface-variant uppercase tracking-wider font-bold">Target Goal</div>
                    <div className="text-base sm:text-lg text-on-surface font-bold">Become a Machine Learning Engineer</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container text-on-surface text-xs">
                    <Schedule className="w-4 h-4 text-primary" />
                    <span>12-Week Pace • Week 2</span>
                  </div>
                  <div className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary-fixed/40 text-primary text-xs font-semibold">
                    <TrendingUp className="w-4 h-4" />
                    <span>On Track (8.5 hrs/wk)</span>
                  </div>
                </div>
              </div>

              {/* Dashboard Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Baseline Meter */}
                <div className="lg:col-span-5 bg-surface-container-low/70 rounded-xl p-5 flex flex-col justify-between border border-outline-variant/40">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs uppercase tracking-wider text-on-surface-variant font-bold">Verified Baseline</span>
                      <span className="text-xs text-primary font-semibold bg-primary-fixed/50 px-2 py-0.5 rounded">4 skills mapped</span>
                    </div>
                    <div className="space-y-3.5">
                      <div>
                        <div className="flex justify-between items-center mb-1 text-xs">
                          <span className="font-medium text-on-surface">Python Architecture</span>
                          <span className="text-primary font-semibold">88% • Bypassed</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-surface-container-highest overflow-hidden">
                          <div className="h-full bg-primary-container rounded-full" style={{ width: '88%' }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between items-center mb-1 text-xs">
                          <span className="font-medium text-on-surface">SQL & Analytical Queries</span>
                          <span className="text-primary font-semibold">71% • Solid</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-surface-container-highest overflow-hidden">
                          <div className="h-full bg-primary-container rounded-full" style={{ width: '71%' }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between items-center mb-1 text-xs">
                          <span className="font-medium text-on-surface">Applied Statistics</span>
                          <span className="text-on-surface-variant font-semibold">63% • Reinforce</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-surface-container-highest overflow-hidden">
                          <div className="h-full bg-primary-container/80 rounded-full" style={{ width: '63%' }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between items-center mb-1 text-xs">
                          <span className="font-medium text-on-surface">Model Validation & Split Hygiene</span>
                          <span className="text-secondary-container font-semibold">35% • Active Focus</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-surface-container-highest overflow-hidden">
                          <div className="h-full bg-secondary-container rounded-full" style={{ width: '35%' }} />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 mt-4 border-t border-outline-variant/30 flex items-center justify-between text-xs text-on-surface-variant">
                    <span>Bypassed 34 basic lessons</span>
                    <span className="text-primary font-semibold flex items-center gap-1">
                      Saved ~18 hours <CheckCircle className="w-3.5 h-3.5 text-primary" />
                    </span>
                  </div>
                </div>

                {/* Prominent Next Action Card */}
                <div className="lg:col-span-7 bg-surface-container-lowest rounded-xl p-6 border border-outline-variant/60 shadow-sm relative overflow-hidden flex flex-col justify-between">
                  <div className="absolute top-0 left-0 right-0 h-1.5 bg-secondary-container" />
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="px-2.5 py-1 rounded bg-secondary-fixed text-on-secondary-container text-xs font-bold uppercase tracking-wider">
                        Recommended Next Step • Week 2
                      </span>
                      <span className="text-xs text-on-surface-variant flex items-center gap-1">
                        <Schedule className="w-3.5 h-3.5" /> 32 min
                      </span>
                    </div>
                    <h2 className="text-xl font-bold text-on-surface mb-2">
                      Model Validation & Split Hygiene
                    </h2>
                    <p className="text-xs text-on-surface-variant mb-4 leading-relaxed">
                      Avoid data leakage across cross-validation folds. Essential prerequisite before starting gradient boosted trees.
                    </p>

                    {/* Curated Resource Stack */}
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center justify-between p-2 rounded-lg bg-surface-container-low text-xs">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px]">1</span>
                          <span className="font-medium text-on-surface">Target Leakage in Time-Series Features</span>
                        </div>
                        <span className="text-on-surface-variant bg-surface-container px-2 py-0.5 rounded text-[10px]">11m doc</span>
                      </div>
                      <div className="flex items-center justify-between p-2 rounded-lg bg-surface-container-low text-xs">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px]">2</span>
                          <span className="font-medium text-on-surface">Interactive Lab: Leak-Free Pipeline</span>
                        </div>
                        <span className="text-on-surface-variant bg-surface-container px-2 py-0.5 rounded text-[10px]">15m lab</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-on-surface-variant">94% match rationale match</span>
                    <Link
                      to="/learn"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-secondary-container text-on-primary text-xs font-bold hover:brightness-105 transition-all"
                    >
                      <span>Start learning</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* 5-Step Methodology */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full" id="how-it-works">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-12 gap-4">
          <div>
            <span className="text-xs uppercase tracking-wider text-primary font-bold mb-2 block">Methodology</span>
            <h2 className="text-3xl font-extrabold text-on-surface tracking-tight">From goal to next action</h2>
          </div>
          <p className="text-sm text-on-surface-variant max-w-md">
            Five algorithmic checkpoints that transform ambition into an actionable, daily curriculum.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="rounded-xl bg-surface-container-lowest p-5 border border-outline-variant/60 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-2xl font-bold text-outline-variant mb-2">01</div>
              <h3 className="text-base font-bold text-on-surface mb-2">Tell us your goal</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Specify a target job role, research paper, framework, or full-stack capstone project.
              </p>
            </div>
            <div className="mt-4 pt-3 flex items-center gap-1.5 text-primary text-xs font-semibold uppercase">
              <Target className="w-4 h-4" /> Outcome-first
            </div>
          </div>

          <div className="rounded-xl bg-surface-container-lowest p-5 border border-outline-variant/60 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-2xl font-bold text-outline-variant mb-2">02</div>
              <h3 className="text-base font-bold text-on-surface mb-2">Understand baseline</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Link your GitHub, past courses, or take a 6-minute adaptive code assessment.
              </p>
            </div>
            <div className="mt-4 pt-3 flex items-center gap-1.5 text-primary text-xs font-semibold uppercase">
              <Rule className="w-4 h-4" /> No redundancy
            </div>
          </div>

          <div className="rounded-xl bg-surface-container-lowest p-5 border border-outline-variant/60 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-2xl font-bold text-outline-variant mb-2">03</div>
              <h3 className="text-base font-bold text-on-surface mb-2">Find your gaps</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Pinpoint precise conceptual blind spots instead of forcing whole chapters you already understand.
              </p>
            </div>
            <div className="mt-4 pt-3 flex items-center gap-1.5 text-secondary-container text-xs font-semibold uppercase">
              <Analytics className="w-4 h-4" /> Precision mapping
            </div>
          </div>

          <div className="rounded-xl bg-surface-container-lowest p-5 border border-outline-variant/60 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-2xl font-bold text-outline-variant mb-2">04</div>
              <h3 className="text-base font-bold text-on-surface mb-2">Curate resources</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Synthesizes top documentation, vetted repo walkthroughs, and peer-reviewed deep-dives.
              </p>
            </div>
            <div className="mt-4 pt-3 flex items-center gap-1.5 text-primary text-xs font-semibold uppercase">
              <AutoStories className="w-4 h-4" /> Noise filtered
            </div>
          </div>

          <div className="rounded-xl bg-surface-container-lowest p-5 border border-outline-variant/60 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-2xl font-bold text-outline-variant mb-2">05</div>
              <h3 className="text-base font-bold text-on-surface mb-2">Learn and adapt</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Miss a day or breeze through a concept? The roadmap continuously repaces automatically.
              </p>
            </div>
            <div className="mt-4 pt-3 flex items-center gap-1.5 text-primary text-xs font-semibold uppercase">
              <Sync className="w-4 h-4" /> Adaptive pacing
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="rounded-3xl bg-primary text-on-primary p-8 sm:p-14 shadow-xl relative overflow-hidden flex flex-col items-center text-center">
          <div className="relative z-10 max-w-2xl">
            <span className="text-xs uppercase tracking-wider text-primary-fixed font-bold mb-3 block">
              Get Started in 2 Minutes
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-on-primary tracking-tight mb-4">
              Ready to learn with total clarity?
            </h2>
            <p className="text-sm text-primary-fixed-dim mb-8 leading-relaxed">
              Tell us your ambition. We'll benchmark what you know and generate your day-by-day learning roadmap immediately.
            </p>
            <Link
              to="/create"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-secondary-container text-on-primary text-sm font-bold shadow-md hover:brightness-105 active:scale-[0.99] transition-all"
            >
              <span>Build your personalized path</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
