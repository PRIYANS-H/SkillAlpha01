export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'USER' | 'ADMIN';
  is_active: boolean;
  created_at?: string;
}

export interface Profile {
  id: string;
  user_id: string;
  goal?: string;
  target_role?: string;
  available_hours: number;
  duration_weeks: number;
  learning_preferences?: string[];
  github_username?: string;
}

export interface Skill {
  id: string;
  name: string;
  slug: string;
  domain: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';
  description?: string;
}

export interface UserSkill {
  id: string;
  skill_id: string;
  skill_name: string;
  skill_score: number;
  confidence_score: number;
  status: 'MASTERED' | 'STRONG' | 'NEEDS_REINFORCEMENT' | 'MISSING' | 'BLOCKED';
  evidence_count: number;
  last_assessed_at: string;
}

export interface Resource {
  id: string;
  title: string;
  url: string;
  provider: string;
  resource_type: 'VIDEO' | 'ARTICLE' | 'DOCUMENTATION' | 'COURSE' | 'GITHUB' | 'PROJECT' | 'PRACTICE' | 'TUTORIAL';
  description?: string;
  duration_minutes: number;
  difficulty: string;
  quality_score: number;
  relevance_score: number;
  verified: boolean;
  is_saved?: boolean;
  match_score?: number;
  match_reason?: string;
  skill_names?: string[];
}

export interface RoadmapTaskResource {
  resource_id: string;
  title: string;
  url: string;
  provider: string;
  resource_type: string;
  duration_minutes: number;
  recommendation_match_score: number;
  recommendation_reason?: string;
}

export interface RoadmapTask {
  id: string;
  milestone_id: string;
  skill_id?: string;
  title: string;
  description?: string;
  estimated_minutes: number;
  sequence_order: number;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED';
  reason_why_next?: string;
  due_date?: string | null;
  kind?: 'SKILL' | 'PROJECT' | 'MILESTONE_CHECK';
  ref_id?: string | null;
  skill_name?: string | null;
  day_count?: number;
  days?: PlanDay[];
  project?: { id: string; title: string; level: string; dataset: string; estimated_hours: number } | null;
  milestone_check?: { phase?: string; skills: string[]; pass_percent: number };
  resources: RoadmapTaskResource[];
}

/** One study day inside a task's day-by-day plan. */
export interface PlanDay {
  index: number;
  kind: 'LEARN' | 'PRACTICE' | 'BUILD' | 'REVIEW';
  title: string;
  steps: string[];
  check?: string | null;
  date?: string | null;
  done: boolean;
}

export interface RoadmapSchedule {
  study_days_per_week: number;
  rest_days_per_week: number;
  minutes_per_day: number;
  total_study_days: number;
  study_days_left: number;
  weeks_needed: number;
  target_weeks: number;
  fits_target: boolean;
  projected_finish?: string | null;
  break_until?: string | null;
  note: string;
}

export interface PracticeProblem {
  id: string;
  skill_name: string;
  type: 'MCQ' | 'NUMERIC' | 'EXTERNAL';
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  points: number;
  title: string;
  prompt: string;
  options?: string[];
  platform?: string;
  url?: string;
  solved: boolean;
  attempts: number;
  points_earned: number;
}

export interface PracticeStats {
  solved: number;
  total: number;
  points: number;
  streak_days: number;
  by_difficulty: Record<'EASY' | 'MEDIUM' | 'HARD', { solved: number; total: number }>;
}

export interface ProjectSubmissionInfo {
  url: string;
  notes?: string | null;
  checklist: boolean[];
  score: number;
  passed: boolean;
  submitted_at?: string | null;
}

export interface Project {
  id: string;
  family: string;
  family_label: string;
  level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  title: string;
  summary: string;
  dataset: string;
  dataset_url: string;
  estimated_hours: number;
  brief: string[];
  rubric: string[];
  pass_items: number;
  submission: ProjectSubmissionInfo | null;
}

export interface RoadmapMilestone {
  id: string;
  title: string;
  description?: string;
  week_number: number;
  sequence_order: number;
  is_completed: boolean;
  tasks: RoadmapTask[];
}

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  goal: string;
  duration_weeks: number;
  hours_per_week: number;
  total_tasks: number;
  completed_tasks: number;
  progress_percent: number;
  route_reasoning?: string;
  is_active: boolean;
  created_at?: string;
  goal_family?: string;
  schedule?: RoadmapSchedule;
  milestones: RoadmapMilestone[];
}

export interface TodayLearning {
  task: RoadmapTask | null;
  milestone_title?: string;
  roadmap_id?: string;
  total_due_today: number;
  reason_why_today?: string;
}

export interface AssessmentQuestion {
  id: string;
  question_text: string;
  options: string[];
  explanation?: string;
}

export interface Assessment {
  id: string;
  skill_id: string;
  skill_name: string;
  title: string;
  description?: string;
  difficulty: string;
  questions: AssessmentQuestion[];
}

export interface AdminMetrics {
  active_users: number;
  roadmaps_created: number;
  resources_indexed: number;
  recommendations_served: number;
  save_rate_percent: number;
  completion_rate_percent: number;
  avg_feedback_score: number;
}
