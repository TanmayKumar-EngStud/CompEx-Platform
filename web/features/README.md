# CompEx Features Directory

Feature-sliced architecture for CompEx — a GRE/GMAT exam preparation platform built with Next.js 15, TypeScript, Prisma, and Zustand.

## Architecture Pattern

Every feature follows a consistent modular structure:

```
features/[feature-name]/
├── components/       # React UI components (client-side)
├── hooks/            # Custom React hooks (state, effects, data fetching)
├── services/         # Server-side business logic & Prisma queries
├── stores/           # Zustand state management stores
├── types/            # TypeScript type definitions
├── lib/              # Pure utility functions (no React dependency)
└── index.ts          # Public barrel exports
```

**Key conventions:**
- `services/` files run server-side (Prisma queries, `"use server"` actions)
- `components/` files are client components (`"use client"`)
- `hooks/` bridge between components and services via React Query or direct calls
- `stores/` use Zustand for cross-component state within a feature
- Pages in `/app` import from features — features never import from `/app`

## Feature Overview

| Feature | Files | Purpose |
|---------|-------|---------|
| **question-solving** | 70+ | Question rendering, 20+ templates, pagination, shuffle |
| **user-analytics** | 30+ | D3/Recharts visualizations, timers, results, feedback |
| **exam-management** | 15+ | Exam type/section selection, tag filtering |
| **bot-protection** | 6 | Anti-bot detection, rate limiting, honeypot fields |
| **question-distribution** | 3 | Smart question selection for balanced mock papers |
| **user-management** | 3 | Authentication, profiles (partially implemented) |
| **user-data** | 3 | GDPR-compliant data export/import |
| **exploration** | 1 | Query exploration service |

## Feature Details

### question-solving (Core)

The largest and most complex feature. Handles all question display, interaction, and navigation.

**Component hierarchy:**
```
QuestionWindow/
├── questionwindow.tsx                # Main wrapper (loads question, manages state)
├── questionwindowWithCacheFix.tsx    # Cache-aware variant
├── questionwindowWithPriority.tsx    # Priority-loading variant
├── QuestionDisplay/
│   ├── questionDisplay.tsx           # Type normalization → template routing
│   └── MemoizedQuestionDisplay.tsx   # React.memo wrapper for performance
└── templates/
    ├── CR.tsx          # Critical Reasoning (single correct, radio)
    ├── DS.tsx          # Data Sufficiency (GMAT, 5 fixed options)
    ├── RC.tsx          # Reading Comprehension (passage + questions)
    ├── SE.tsx          # Sentence Equivalence (select exactly 2)
    ├── TC-23.tsx       # Text Completion (1-3 blanks, grouped radio)
    ├── GI.tsx          # Graphic Interpretation (chart + dropdown blanks)
    ├── TA.tsx          # Table Analysis (sortable table + true/false per row)
    ├── TS-TA.tsx       # Two-part / Table Analysis hybrid
    ├── NE.tsx          # Numeric Entry (text input, exact/range match)
    ├── msr.tsx         # Multi-Source Reasoning (tabbed sources)
    ├── Dichotomous.tsx # Binary choice (GMAT)
    ├── ParentChild.tsx # Parent-child question wrapper
    ├── graphs/         # 10+ chart components (BarChart, LineChart, PieChart, ScatterPlot, etc.)
    └── tables/         # DataTable, PivotTable, SortableTable, SourceTable
```

**Template routing logic** (`questionDisplay.tsx`):
1. Reads `options_type` and `type` from the problem record
2. Normalizes to canonical type: `"TC-1"`, `"TC-2"`, `"TC-3"`, `"GI"`, `"CR"`, `"DS"`, `"SE"`, `"NE"`, `"TA"`, `"MSR"`, `"RC"`, etc.
3. Routes to the correct template component
4. TC normalization: counts `problemoptions` length to distinguish TC-1 (<=5), TC-2 (6), TC-3 (7+)
5. All TC variants route to `TC23Template` which groups by the `group` field on each option

**TC-23 blank rendering:**
- Options have `group: "1" | "2" | "3"` in the database
- Template groups options by `group`, renders N columns (one per blank)
- Each column is a RadioGroup; user selects one option per blank
- Fallback: if groups are missing, counts `__` blanks in question text and splits options evenly

**Pagination system:**
```
hooks/(pagination)/
├── fetchProblems.tsx              # React Query hook for problem list
├── fetchProblemsWithPriority.tsx  # Priority-based loading variant
├── fetchTags.tsx                  # Tag filter fetching
└── problemDefinition.ts           # Type definitions

services/
├── question-pagination-service.ts # Server-side pagination logic
├── pagination-cache.service.ts    # Client cache management
├── pre-fetch.service.ts           # Predictive prefetching
└── problemset-queries.ts          # Prisma queries for problem sets

lib/
├── doubly-linked-list.ts          # Navigation data structure
├── question-id-manager.ts         # ID tracking across pages
└── shuffle-methods.ts             # Fisher-Yates and weighted shuffles

stores/
└── pagination-cache.store.ts      # Zustand store for pagination state
```

**Services layer:**
- `question-queries.ts` — Prisma queries to fetch full question data with options, tags
- `question-details-service.ts` — Detailed question info (solution, explanation)
- `question-attempt-service.ts` — Records user answers, calculates correctness
- `shuffle.service.ts` — Server-side shuffle orchestration
- `tag-filter.service.ts` — Tag-based question filtering
- `client-api.ts` — Client-side API wrapper for fetch calls

### user-analytics

Performance tracking and data visualization using D3.js and Recharts.

**D3 visualizations** (in `components/d3/`):
| Component | Purpose |
|-----------|---------|
| `ActivityHeatmap.tsx` | GitHub-style activity calendar |
| `SkillRadar.tsx` | Radar chart of skills by topic |
| `SkillBarChart.tsx` | Horizontal bar chart of topic performance |
| `DifficultyPie.tsx` | Pie chart of attempts by difficulty |
| `SectionDistributionDonut.tsx` | Donut chart of section distribution |
| `TrendChart.tsx` | Line chart of performance over time |
| `PercentileTrendChart.tsx` | Percentile ranking trends |
| `ScoreDistributionChart.tsx` | Bell curve of mock test scores |
| `TopicQuadrantChart.tsx` | 2D scatter: speed vs accuracy per topic |
| `OutcomeTimeDistribution.tsx` | Distribution of time per correct/incorrect |
| `ActionableStats.tsx` | Key metric cards with recommendations |
| `TestTubeDonut.tsx` | Custom donut for test-tube visual |
| `MockDashboard/` | 3 components for mock test analytics |

**Other components:**
- `result-window/resultWindow.tsx` — Post-question result modal (correct/incorrect, solution, explanation)
- `timer/timer.tsx` — Countdown/countup timer with pause, status indicators
- `feedback/QuestionFeedbackModal.tsx` — 1-10 rating modal for question quality
- `feedback/UserCollectibles.tsx` — Badge/achievement display

**Services:**
- `analytics.service.ts` — Aggregates performance data, computes statistics
- `question-stats-service.ts` — Per-question statistics (attempts, success rate)

**Hooks:**
- `use-question-stats.ts` — React Query hook for question statistics
- `resultWindowDefinitions.ts` — Type definitions for result display
- `timerDefinition.ts` — Timer state types and interfaces

### exam-management

Manages exam type selection (GRE/GMAT), section filtering, and tag-based question discovery.

**Components:**
- `panel.tsx` — Main exam panel container
- `parent-panel.tsx` — Top-level panel with exam type tabs
- `tab.tsx` — Individual tab component
- `exam-section-panel.tsx` — Section selector (Quants, Verbal, Data Insights)
- `tag-properties.tsx` — Tag display with topic/theme/type badges

**Services:**
- `exam-section-service.ts` — Fetches exam types and sections from DB
- `tag-queries.ts` — Queries tags filtered by exam type + section

**Hooks:**
- `use-exam-section-logic.ts` — State management for exam/section/tag selection

### bot-protection

Server-side anti-abuse system protecting question attempts and feedback.

**Components:**
- `bot-detection.ts` — Scoring engine (0-100): time-based detection (<5s = suspicious), pattern analysis, IP tracking
- `rate-limiter.ts` — Token bucket: 50 attempts/hour, 200/day per user
- `honeypot.tsx` — Invisible form fields that bots fill but humans don't
- `schema-migrations.ts` — Database table setup for tracking
- `index.ts` — Public exports

**Scoring thresholds:** 0-30 = allow, 30-60 = challenge (CAPTCHA), 60-100 = block

### question-distribution

Algorithmic question selection ensuring balanced mock test papers.

- `question-distribution.ts` — Distribution engine:
  - 60/40 independent/contextual question ratio
  - Difficulty spread: Easy 20%, Medium 50%, Hard 30%
  - Minimum quality score filtering
  - Topic coverage guarantee (all topics represented)

### user-management (Partial)

Authentication and user profiles. Currently has README stubs defining planned structure.

**Planned services:** `auth-service.ts`, `profile-service.ts`, `preferences-service.ts`
**Planned components:** `login-form.tsx`, `signup-form.tsx`, `profile-editor.tsx`

### user-data

GDPR-compliant data portability system.

- `user-data-service.ts` — Export/import user data as JSON
- `PRIVACY.md` — Privacy policy (data collection, retention, deletion rights)

### exploration

Minimal feature with a single query service.

- `services/explore-queries.ts` — Exploratory data queries

## Cross-Feature Data Flow

```
exam-management                    question-solving                  user-analytics
┌──────────────┐                  ┌─────────────────┐               ┌────────────────┐
│ examtypeid   │──── filters ────→│ Pagination       │               │                │
│ sectionid    │                  │ QuestionWindow   │── attempt ───→│ Result Window   │
│ tags[]       │                  │ Templates        │   data        │ D3 Charts       │
└──────────────┘                  └─────────────────┘               │ Timer           │
                                         │                          └────────────────┘
                                         │ submit                          ↑
                                         ↓                                 │
                                  bot-protection                    analytics data
                                  ┌──────────────┐                        │
                                  │ Rate Limiter  │                        │
                                  │ Bot Detection │────── stats ──────────┘
                                  └──────────────┘
```

## Database Models Used by Features

| Feature | Primary Models |
|---------|---------------|
| exam-management | `examtypes`, `sections`, `tags`, `tag_scopes` |
| question-solving | `problems`, `problemoptions`, `ProblemsSet`, `problemtags` |
| user-analytics | `userattempts`, `performance`, `user_overall_performance`, `user_tag_performance`, `user_difficulty_stats` |
| bot-protection | Custom tracking tables (via `schema-migrations.ts`) |
| question-distribution | `problems`, `ProblemsSet`, `QuestionQualityMetrics` |
| user-management | `users`, `userstreaks` |
| user-data | `users`, `userattempts`, `performance` |

## Key Database Fields for Question Rendering

**`problems` table:**
- `options_type` — `"single"` (radio), `"multi"` (checkbox), `"blank"` (TC/GI grouped blanks), `"numeric"` (text input)
- `type` — Display hint (`"Multiple Choice"`, etc.), not always reliable for template selection
- `metadata` (JSON) — `{ generatedBy, questionType, fileName, exam, section, difficulty, tags[] }`
- `solution` (JSON) — Step-by-step solution text

**`problemoptions` table:**
- `optiontext` — The option text displayed to the user
- `iscorrect` — Boolean flag for correct answer(s)
- `group` — For TC/GI: `"1"`, `"2"`, `"3"` (which blank); for flat questions: `"A"`, `"B"`, `"C"`, `"D"`, `"E"`
- `explanation` — Per-option explanation text

## Adding a New Feature

1. Create directory: `features/[feature-name]/`
2. Follow the standard structure (components/, services/, hooks/, types/)
3. Export public API from `index.ts`
4. Server-side code goes in `services/` with `"use server"` or direct Prisma calls
5. Client components use `"use client"` and import from hooks/stores
6. Register any new API routes in `/app/api/`
7. Add Prisma model changes to `/prisma/schema.prisma` and run `npx prisma migrate dev`

## Development Notes

- **State management**: Zustand for client state, React Query for server state
- **Styling**: Tailwind CSS + Radix UI primitives
- **Charts**: D3.js for custom visualizations, Recharts for standard charts
- **Math rendering**: KaTeX/LaTeX support in question text
- **Testing**: Vitest for unit tests (see `/tests/`)
