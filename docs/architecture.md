# SkillAlpha System Architecture

SkillAlpha is a personalized learning and resource discovery platform that continuously connects a learner's goals, existing abilities, and available time with curated learning resources.

## System Diagram

```
+-----------------------------------------------------------------------------------+
|                                  React SPA Frontend                               |
|                  (TypeScript + Vite + Tailwind CSS + Lucide Icons)                |
+-----------------------------------------------------------------------------------+
                                         |
                                         | HTTP / JSON REST API
                                         v
+-----------------------------------------------------------------------------------+
|                                 FastAPI Backend Monolith                          |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Auth & Security    |  | Target Skill Graph   |  | Skill Gap Engine          |  |
|  | (JWT + Bcrypt)     |  | (Ontology Builder)   |  | (Prerequisite Aware)      |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Recommendation     |  | Adaptive Replanner   |  | Assessment & Evidence     |  |
|  | (Weighted Ranking) |  | (Evidence Driven)    |  | (Gradual Score Updates)   |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+-----------------------------------------------------------------------------------+
                                         |
                                         | SQLAlchemy 2.0 ORM
                                         v
+-----------------------------------------------------------------------------------+
|                        PostgreSQL / SQLite Database                               |
|   (users, profiles, skills, resources, roadmaps, task_progress, assessments)      |
+-----------------------------------------------------------------------------------+
```

## Core Algorithmic Loops

### 1. Skill Gap Calculation Formula
$$\text{Skill Gap} = \text{Target Skill Score} - \text{User Skill Baseline Score}$$

Skills are classified into:
- `MASTERED` ($\ge 80\%$): Bypassed to save user time.
- `STRONG` ($65\% - 79\%$): Bypassed or assigned light review.
- `NEEDS_REINFORCEMENT` ($40\% - 64\%$): High-priority active task with reinforcement checkpoint.
- `MISSING` ($< 40\%$): Primary focus task in dependency sequence.

### 2. Multi-Signal Recommendation Ranking Score
$$\text{Score} = 0.30 R_{\text{topic}} + 0.20 R_{\text{gap}} + 0.15 Q + 0.10 D_{\text{fit}} + 0.10 F + 0.10 E + 0.05 Div$$

Where:
- $R_{\text{topic}}$: Topic & Skill Relevance
- $R_{\text{gap}}$: Skill Gap Alignment
- $Q$: Quality Score
- $D_{\text{fit}}$: Difficulty Fit
- $F$: Content Freshness
- $E$: Engagement & Feedback Signal
- $Div$: Resource Format Diversity

### 3. Evidence-Based Skill Score Update
$$\text{Score}_{\text{new}} = \text{Score}_{\text{old}} \times 0.60 + \text{Quiz Ratio} \times 0.40$$
$$\text{Confidence}_{\text{new}} = \min(0.95, \text{Confidence}_{\text{old}} + 0.15)$$
