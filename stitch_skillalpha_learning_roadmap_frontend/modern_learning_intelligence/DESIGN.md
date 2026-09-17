---
name: Modern Learning Intelligence
colors:
  surface: '#f6fbf5'
  surface-dim: '#d6dbd6'
  surface-bright: '#f6fbf5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f5ef'
  surface-container: '#eaefea'
  surface-container-high: '#e5e9e4'
  surface-container-highest: '#dfe4de'
  on-surface: '#181d1a'
  on-surface-variant: '#404943'
  inverse-surface: '#2c322e'
  inverse-on-surface: '#edf2ec'
  outline: '#707973'
  outline-variant: '#c0c9c1'
  surface-tint: '#31694f'
  primary: '#0a4831'
  on-primary: '#ffffff'
  primary-container: '#286047'
  on-primary-container: '#9ed8b9'
  inverse-primary: '#99d3b4'
  secondary: '#ae3200'
  on-secondary: '#ffffff'
  secondary-container: '#fd5920'
  on-secondary-container: '#521300'
  tertiary: '#39413d'
  on-tertiary: '#ffffff'
  tertiary-container: '#505854'
  on-tertiary-container: '#c6cec9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b4f0cf'
  primary-fixed-dim: '#99d3b4'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#165038'
  secondary-fixed: '#ffdbd0'
  secondary-fixed-dim: '#ffb59e'
  on-secondary-fixed: '#3a0b00'
  on-secondary-fixed-variant: '#852400'
  tertiary-fixed: '#dce4df'
  tertiary-fixed-dim: '#c0c8c4'
  on-tertiary-fixed: '#161d1a'
  on-tertiary-fixed-variant: '#414845'
  background: '#f6fbf5'
  on-background: '#181d1a'
  surface-variant: '#dfe4de'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2.5rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
The design system balances Swiss graphic discipline with the warmth of modern pedagogical tooling. Created for deep work, persistent discovery, and daily study, the aesthetic avoids gamification cliches, prioritizing editorial clarity, high information density, and deliberate cognitive calm. 

The interface evokes focus, intentionality, and quiet momentum. Surfaces adopt an organic porcelain cast (#F6F7F3) paired with stark white structural modules, anchoring the user without causing visual fatigue. Typography is geometric yet humanistic, relying on rigorous typographic scales, precise tracking, and clear structural hierarchy to make complex curricula immediately digestible.

## Colors
The palette is rooted in natural paper and ink tones, punctuated by purposeful accents:

- **Primary Canvas & Surfaces**: The core app canvas defaults to `#F6F7F3`. Cards, content segments, and interactive panels use pure `#FFFFFF` to rise above the foundation.
- **Ink Tones**: Headings and essential metrics use deep obsidian ink `#111613`. Secondary explanatory copy, meta tags, and passive states use `#6F7771`.
- **System Borders**: Structural boundaries rely on a hairline border `#E1E5DF`.
- **Deep Forest (Primary Brand)**: `#286047` provides authoritative structure. It represents completion, mastery, verified skills, and deliberate intellectual progress. Its soft wash, `#EAF2ED`, serves as the background for progress states, active navigation indicators, and skill tags.
- **Direct Orange (Action Accent)**: `#FF5B22` is reserved strictly for primary momentum—"Resume Lesson", "Start Assessment", active streaks, and primary calls to action. Paired with `#FFF0E9` for focus highlights and interactive hover states.

## Typography
Plus Jakarta Sans is used across all typographic roles to preserve geometric precision while retaining friendly, accessible counters. 

- **Display & Headlines**: Tightly tracked (down to `-0.03em`) to mimic mid-century Swiss editorial posters, presenting authoritative course titles and milestone headers without excessive weight.
- **Body Text**: Relaxed leading (`26px` on `16px` font) ensures prolonged reading comfort across technical summaries, code documentation, and interactive transcripts.
- **Labels & Overlines**: Uppercase labels use slightly expanded tracking (`+0.04em`) with semibold or bold weights to provide structural demarcations over syllabus tables and module categories.

## Layout & Spacing
The layout follows a 12-column responsive fluid grid with maximum container widths capped at `1440px` to maintain optimal line-length for technical content:

- **Desktop (1024px and above)**: 12 columns, `1.5rem` gutters, `2.5rem` minimum canvas padding. Multi-pane workflows (e.g., resource sidebar + interactive canvas + progress inspector) occupy distinct 3-6-3 or 4-8 column divisions.
- **Tablet (768px - 1023px)**: 8 columns, `1rem` gutters, `1.5rem` canvas padding. Non-critical contextual drawers collapse into slide-over panels.
- **Mobile (under 768px)**: 4 columns, `1rem` gutters, `1.25rem` outer margins. Horizontal layouts compress to single vertical stacks.

## Elevation & Depth
Elevation in this system is driven by 1px structural hairline borders combined with tonal contrast rather than layered drop shadows. The depth philosophy remains grounded and tactile:

- **Canvas Base**: `#F6F7F3` baseline canvas.
- **Resting Layer**: All cards, inputs, and modular blocks sit on `#FFFFFF`, framed by a crisp `1px solid #E1E5DF` border. Shadows are strictly `0 1px 2px rgba(17, 22, 19, 0.04)`.
- **Hover / Interactive Elevation**: Interactive modules translate upwards slightly with an ultra-soft ambient shadow: `0 4px 16px rgba(17, 22, 19, 0.06), 0 1px 3px rgba(17, 22, 19, 0.04)`.
- **Overlays & Modals**: Fixed overlays rely on a neutral tint scrim (`rgba(17, 22, 19, 0.4)`) with dialog surfaces utilizing `0 12px 36px rgba(17, 22, 19, 0.08)` and `1px solid #E1E5DF`. Heavy blurs and floating glassmorphism are avoided.

## Shapes
Geometry is disciplined, using unified 12px to 16px corner radii to balance approachable softness with architectural stability:

- **Structural Cards & Panels**: Fixed at `0.75rem` (12px) or `1rem` (16px) depending on size hierarchy. Outer modal wrappers scale to `1rem`.
- **Input Fields & Action Controls**: Fixed at `0.5rem` (8px) to `0.75rem` (12px) to maintain rectangular integrity for daily utility.
- **Exceptions (Pills)**: Pill radii (`9999px`) are strictly constrained to contextual chips, difficulty tags ("Beginner", "Advanced"), and live status badges. Buttons, dialogue windows, and content blocks must never use full pill radius.

## Components

### Buttons
- **Primary Action (Momentum)**: Solid `#FF5B22` background, `#FFFFFF` text, `0.5rem` border radius, `12px 20px` padding. State changes: hover to `#E04A15`, active press down.
- **Secondary (Completion/Milestone)**: Solid `#286047` background with `#FFFFFF` text. Used for confirming course completion, marking lesson complete, or active study mode.
- **Tertiary / Subtle**: Background `#FFFFFF`, border `1px solid #E1E5DF`, text `#111613`. Hover introduces background `#F6F7F3`.

### Chips & Tags
- **Status & Difficulty Tags**: Pill shape (`9999px`), `4px 10px` padding, font `label-sm`.
  - *Progress/Success*: Background `#EAF2ED`, text `#286047`.
  - *Action/Attention*: Background `#FFF0E9`, text `#FF5B22`.
  - *Neutral Metric*: Background `#FFFFFF`, border `1px solid #E1E5DF`, text `#6F7771`.

### Form Controls & Inputs
- **Text Inputs**: Height `44px`, background `#FFFFFF`, border `1px solid #E1E5DF`, radius `0.5rem`, text `#111613`, placeholder `#6F7771`. Focus state: border `#286047` with a non-blurring `0 0 0 1px #286047` focus ring.
- **Checkboxes & Radios**: Size `18px`, radius `4px` (checkbox) or circular (radio). Unchecked: `1.5px solid #E1E5DF`. Checked: `#286047` background with pure white check mark.

### Content Cards & Modules
- **Resource / Curriculum Card**: Background `#FFFFFF`, border `1px solid #E1E5DF`, radius `0.75rem`, internal padding `1.5rem`. Header features editorial small label overline, title-lg main link, and a bottom progress tracker consisting of a hairline bar (`#E1E5DF`) filled with `#286047`.

### Learning Metrics & Steppers
- **Path Progress Nodes**: Step indicators use a 32px circle. Completed nodes feature `#286047` with white glyphs. Active nodes feature a 2px outer ring of `#FF5B22` with a central dot. Locked or upcoming nodes use `#FFFFFF` with `#E1E5DF` borders and `#6F7771` text.