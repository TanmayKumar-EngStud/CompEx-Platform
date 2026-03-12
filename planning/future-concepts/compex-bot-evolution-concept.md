# CompEx Bot Evolution Model
## Elo-Style Cohort-Based Learning System

---

## Core Concept

Instead of one "smart bot" that tries to adapt to all students, you have **multiple bot generations**, each:
- Assigned to a cohort of students at launch
- Learns specifically from *that cohort's interactions*
- Reaches a stable "mastery level" for that cohort
- Gets archived/versioned when cohort graduates
- New bot (v2, v3...) trained on next cohort with improved baseline

This mirrors **chess engines**:
- Stockfish 14 → Stockfish 15 (each generation better)
- Each version trained on millions of games
- Previous version becomes a benchmark

---

## Architecture Overview

### Layer 1: Bot Generations & Versioning

```
Bot-GRE-Quants-v1 (Cohort A: Jan 2025)
  ├─ Baseline: QGen-FRESH questions + seed explanations
  ├─ Training data: 500 students × 40 questions = ~20k interactions
  ├─ Elo score: 1600 (end-of-cohort performance metric)
  └─ Status: ARCHIVED (frozen after Cohort A graduates)

Bot-GRE-Quants-v2 (Cohort B: Apr 2025) ← NEW
  ├─ Baseline: v1's final state + insights from v1's cohort
  ├─ Improvements: Better explanations for topics where v1 struggled
  ├─ Training data: 600 students × 40 questions = ~24k interactions
  ├─ Elo score: 1750 (learning in progress)
  └─ Status: ACTIVE

Bot-GRE-Quants-v3 (Cohort C: Jul 2025) ← QUEUED
  └─ Will start training when v2 cohort completes
```

### Layer 2: What Each Bot Learns

For each student interaction, the bot captures:

```json
{
  "interactionId": "INT-20250215-001",
  "botVersion": "Bot-GRE-Quants-v2",
  "cohortId": "Cohort-B-2025",
  "studentId": "STU-5234",
  "questionId": "QID-1849",
  "questionType": "Data Sufficiency",
  "topic": "Ratio and Proportion",
  "studentPerformance": {
    "answered": true,
    "correct": false,
    "timeSpent": 120,
    "attemptNumber": 1
  },
  "botAction": {
    "explanationType": "step-by-step",
    "focusArea": "Statement 1 insufficiency",
    "difficulty": "adjusted_down"
  },
  "outcome": {
    "studentUnderstood": true,  // binary feedback or proxy signal
    "nextQuestionSelected": "QID-1852",
    "difficultyJump": 0  // 0=same, +1=harder, -1=easier
  }
}
```

The bot learns:
- **Which explanations work** for which question types
- **Topic weakness patterns** (if students fail on "Ratio" questions, they often fail on "Percentage" too)
- **Optimal difficulty progression** (how fast to escalate)
- **Timing signals** (if student is taking >5min on a 2min question, flag confusion)

---

## Bot Elo Score

Each bot has an **aggregate Elo score** that measures cohort improvement:

```
Bot-GRE-Quants-v2 Elo Score
├─ Baseline Elo: 1400 (starting assumption)
├─ After 100 interactions: 1520
├─ After 500 interactions: 1650
├─ After 1000 interactions: 1720
├─ Final (cohort complete): 1785 ← Archived with this score
└─ Interpretation: "Average student in this cohort improved from 1400→1785"
```

**Elo calculation per bot:**
```
elo_gain = (student_final_score - student_initial_score) / num_students

Bot's final_elo = baseline_elo + elo_gain
```

This tells you:
- **v1 (1600 Elo)** helped students improve by +200 points
- **v2 (1785 Elo)** should help students improve by +385 points (better!)
- **v3 (goal: 1900 Elo)** targets further improvement

---

## Data Captured for Bot Learning

### Per Student (from analytics):
- **Initial Diagnostic:** baseline skill level on GRE Quants
- **Performance trajectory:** question difficulty over time
- **Concept mastery curve:** when did they master "Percentage"? "Geometry"?
- **Explanation preferences:** did they prefer visual, algebraic, or conceptual explanations?
- **Pace indicators:** are they rushing or overthinking?

### Per Bot Interaction:
- **Which explanation did the student see?**
- **Did they move to next question immediately or review?**
- **Did they get the follow-up question right?** (signal of understanding)
- **Time-to-mastery** for each topic

### Aggregated (cohort level):
```
Bot-GRE-Quants-v2 Learning Report
├─ Total interactions: 24,000
├─ Students: 600
├─ Topics with highest struggle: Geometry (52% wrong), Algebra (48% wrong)
├─ Explanation types most effective:
│   ├─ Visual diagrams: +12% correct next time
│   ├─ Step-by-step algebra: +8% correct next time
│   └─ Concept video: +5% correct next time
├─ Optimal difficulty progression: +1 difficulty every 5 correct answers
├─ Dropout risk signals: >5min per question → 40% likely to disengage
└─ Final cohort improvement: +385 Elo points
```

---

## Bot Training Pipeline

### Phase 1: Initialization (Before cohort starts)
```
1. Load QGen-FRESH questions + seed explanations
2. Set baseline Elo: 1400 (neutral starting point)
3. Define cohort: 600 students
4. Configure bot parameters:
   - difficulty_escalation_rate: +1 per 5 correct
   - explanation_variety: rotate visual → algebraic → conceptual
   - timeout_threshold: 5min = flag confusion
```

### Phase 2: Active Learning (Cohort studying, 12 weeks)
```
Daily:
1. Collect all interactions from previous 24h
2. Aggregate topic-level performance
3. Update bot's "topic knowledge":
   ├─ Geometry → 52% struggling → increase visual explanations
   ├─ Algebra → 48% struggling → add more step-by-step
   └─ Logic → 25% struggling → keep current approach
4. Update difficulty curve (if cohort avg is <30% correct, ease up)
5. Log Elo score snapshot (moving average)

Weekly:
1. Identify students at risk of dropout (>5min median time)
2. Trigger intervention: "Your bot noticed you're taking longer on Geometry. Try this visual explanation."
3. Refine explanation database (prune low-performing ones)
```

### Phase 3: Archival (Cohort completes)
```
1. Freeze bot version (no more updates)
2. Calculate final Elo score (1785 for v2)
3. Export cohort learning data:
   ├─ Topic mastery curves
   ├─ Explanation effectiveness
   ├─ Difficulty progression patterns
   └─ Dropout risk indicators
4. Store in "Bot v2 Retrospective"
```

### Phase 4: Initialization for v3 (Next cohort)
```
1. Use v2's learnings to improve v3:
   ├─ "Geometry explanations need more visuals" → pre-seed v3 with diagrams
   ├─ "Difficulty escalation was too fast" → start slower
   ├─ "Algebra step-by-step worked best" → prioritize that format
2. Set v3 baseline Elo: 1700 (inherits v2's knowledge)
3. Launch with new cohort (600 more students)
4. Target: v3 reaches 1900 Elo (better than v2)
```

---

## Database Schema (Simplified)

```sql
-- Bot versions
TABLE bots (
  bot_id UUID,
  exam_type VARCHAR(10),       -- "GRE", "GMAT"
  section VARCHAR(20),         -- "Quants", "Verbal", "Reasoning"
  version INT,                 -- v1, v2, v3...
  baseline_elo INT,
  final_elo INT,               -- NULL until cohort completes
  status ENUM ('ARCHIVED', 'ACTIVE', 'QUEUED'),
  created_at TIMESTAMP,
  cohort_id UUID
);

-- Cohorts (groups of students trained together)
TABLE cohorts (
  cohort_id UUID,
  name VARCHAR(50),            -- "Cohort-B-2025"
  bot_version INT,
  start_date DATE,
  end_date DATE,               -- NULL if active
  student_count INT,
  status ENUM ('ACTIVE', 'COMPLETED')
);

-- Interactions (every question attempt)
TABLE bot_interactions (
  interaction_id UUID,
  bot_id UUID,
  student_id UUID,
  question_id UUID,
  explanation_id UUID,
  student_correct BOOLEAN,
  time_spent_seconds INT,
  student_understood BOOLEAN,  -- feedback signal
  created_at TIMESTAMP,
  FOREIGN KEY (bot_id) REFERENCES bots
);

-- Topic performance (aggregated)
TABLE topic_performance (
  topic_id VARCHAR(100),       -- "Ratio and Proportion"
  bot_id UUID,
  cohort_id UUID,
  total_attempts INT,
  correct_count INT,
  avg_time_seconds INT,
  effectiveness_score FLOAT,   -- metric for next bot version
  created_at TIMESTAMP
);

-- Explanation effectiveness (what works best)
TABLE explanation_effectiveness (
  explanation_id UUID,
  bot_id UUID,
  topic_id VARCHAR(100),
  explanation_type VARCHAR(20), -- "visual", "algebraic", "conceptual"
  success_rate FLOAT,           -- % students who got follow-up right
  avg_student_satisfaction FLOAT,
  created_at TIMESTAMP
);
```

---

## Feedback Loop: How v2 Learns to Beat v1

**After v1 cohort (Cohort A) completes:**

```
Data analysis on v1's 20k interactions:
├─ Geometry: 52% failure rate ← BOT STRUGGLED HERE
├─ Algebra: 48% failure rate
├─ Logic: 25% failure rate

Root cause analysis:
├─ Geometry: Visual explanations only in 30% of interactions
│   → v2 improvement: Include visual in 80% of geometry explanations
├─ Algebra: Step-by-step was effective (78% follow-up correct)
│   → v2 improvement: Prioritize step-by-step even more
└─ Logic: No significant issues
```

**v2 launches with:**
- Same baseline questions (QGen-FRESH v1)
- Better explanation distribution (80% visual for Geometry)
- Better question sequencing (based on v1's difficulty curve)
- **Result:** Cohort B improves faster, v2 reaches 1785 Elo (vs v1's 1600)

**v3 will improve on v2** by:
- Analyzing where v2 still struggled (likely different topics than v1)
- Refining explanations further
- Potentially adding new question types (if QGen-FRESH v2 generates them)

---

## Dashboard View for You (Product Manager)

```
CompEx Bot Evolution Dashboard

┌─────────────────────────────────────┐
│ Bot Lineage (GRE Quants)            │
├─────────────────────────────────────┤
│                                      │
│  Bot v1 ──→ Bot v2 ──→ Bot v3       │
│ (1600)     (1785)   (target: 1900)  │
│   ✓        Active     Queued        │
│  Cohort A  Cohort B  Cohort C       │
│                                      │
└─────────────────────────────────────┘

Active Bot: v2 (Cohort B)
├─ Students: 587 / 600
├─ Current Elo: 1745 (moving up)
├─ Topics mastered: Arithmetic, Percentages
├─ Topics struggling: Geometry (48%), Set Theory (45%)
├─ Interactions this week: 2,340
├─ Explanation effectiveness top 3:
│  1. Visual diagrams (83% follow-up correct)
│  2. Step-by-step algebra (78% correct)
│  3. Concept mapping (72% correct)
└─ Estimated completion: 6 weeks

Previous Bot: v1 (Cohort A)
├─ Cohort Status: COMPLETED ✓
├─ Final Elo: 1600
├─ Key learnings:
│  - Geometry was weak (52% failure)
│  - Step-by-step algebra worked best
│  - Difficulty escalation too fast initially
└─ Export insights → v2 initialization
```

---

## Implementation Roadmap

### Phase 1: MVP (Bot v1 Launch)
- [ ] Set up Cohort A (200-300 students)
- [ ] Create Bot v1 with QGen-FRESH questions
- [ ] Build interaction logging (bot_interactions table)
- [ ] Deploy basic explanation system (text + maybe 1 visual)
- [ ] Track Elo score (simple avg improvement metric)
- [ ] Goal: Get v1 to 1600 Elo baseline

### Phase 2: Iterative (Bot v2 Preparation)
- [ ] Analyze Cohort A's interaction data
- [ ] Identify weak topics + effective explanations
- [ ] Build content gaps (improve geometry explanations)
- [ ] Version management system (ability to freeze v1, launch v2)
- [ ] Launch Cohort B with Bot v2
- [ ] Goal: v2 reaches 1750+ Elo

### Phase 3: Scaling (v3+)
- [ ] Automate cohort lifecycle (start → archive)
- [ ] Build comparison dashboard (v1 vs v2 vs v3)
- [ ] Multi-exam support (GRE Quants → GRE Verbal → GMAT...)
- [ ] Expand explanation formats (video, interactive simulations)
- [ ] Goal: Each bot generation improves by 150+ Elo

---

## Key Metrics

For each bot version:

| Metric | Description | Target |
|--------|-------------|--------|
| **Final Elo** | Avg student improvement from start to end | +200 (v1), +250 (v2), +300 (v3) |
| **Explanation Effectiveness** | % of students who solve follow-up after explanation | 75%+ |
| **Time-to-Mastery** | Avg interactions to master a topic | 8-12 interactions |
| **Dropout Rate** | % students who quit mid-cohort | <5% |
| **Retention to Next Bot** | % who continue to next cohort/exam | 60%+ |
| **Topic Coverage** | % of topics where bot reaches 70%+ success | 85%+ |

---

## Competitive Advantage

You're building **dynamic IP**:
- Each bot version is a **frozen model** of teaching effectiveness
- v1, v2, v3... become progressively better benchmarks
- Competitors with static test banks can't iterate this way
- Your bot lineage *gets better over time*, not stagnant

It's the **evolutionary advantage** of chess engines: Stockfish 15 > Stockfish 14 > Stockfish 13.

---

## Next Questions for You

1. **Feedback signal:** How will you know if a student "understood" after an explanation?
   - Post-question survey ("Did that help?" Y/N)?
   - Implicit signal (got follow-up question right)?
   - Time-based (didn't re-review the explanation)?

2. **Explanation creation:** Who writes/improves explanations?
   - Claude Code (AI-generated initially)?
   - Domain experts (for v2 improvements)?
   - Hybrid?

3. **Cohort size:** 200-600 students per cohort?
   - Smaller = faster iteration (3-4 months per cycle)
   - Larger = more data per bot (better learning)

4. **Launch timeline:** When does Cohort A start?

