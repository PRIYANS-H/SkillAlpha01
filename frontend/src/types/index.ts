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
  resources: RoadmapTaskResource[];
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
