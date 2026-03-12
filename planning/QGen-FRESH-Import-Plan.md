# QGen-FRESH Database Import Plan

## Context

QGen-FRESH (Python question generator at commit `86fbe027`) has 22 JSON files in `~/Desktop/QGen-FRESH/log_json_files/paper/mega_papers/` containing 1,319 parent questions + 530 child questions = 1,849 total questions for GRE and GMAT exams. These need to be loaded into the CompEx production PostgreSQL database (Neon) using Prisma, following the exact insertion patterns already established in CompEx.

The DB connection string is already in `~/Desktop/CompEx/.env` as `DATABASE_URL`.

---

## Scope

- **22 JSON files:** 2 root files + 10 in `29-Dec/` + 10 in `30-Dec/`
- **~1,849 questions total** across GRE (Quants, Verbal) and GMAT (Quants, Verbal, Integrated Reasoning)
- **Question types:** Problem Solving, Critical Reasoning, Data Sufficiency, Reading Comprehension (parent+child), Text Completion, Sentence Equivalence, Numerical Entry, Quantitative Comparison, Table Analysis, Graphic Interpretation, Multi-Source Reasoning, Two-Part Analysis

---

## Access Required

| Action | Sensitivity | Who | Details |
|--------|-------------|-----|---------|
| Read `.env` for `DATABASE_URL` | Sensitive — contains DB credentials | You verify the connection string is correct, then grant permission to use it via `process.env.DATABASE_URL` |
| Write a TypeScript import script in `~/Desktop/CompEx/scripts/` | Not sensitive | Claude Code | |
| Run `npx prisma generate` in CompEx | Not sensitive | Claude Code | |
| Run the import script with `npx tsx` | Writes to production DB | Claude Code (with your approval before execution) |
| Create new tags/tag_scopes if topics from QGen-FRESH don't exist yet | DB writes | Claude Code (as part of import script) |

**No manual actions needed from you** — just need your go-ahead to run the script against production.

---

## Implementation Plan

### Step 1: Create import script at `~/Desktop/CompEx/scripts/data-management/import-qgen-fresh.ts`

#### 1a. Setup & Configuration

- Use `PrismaClient` with `process.env.DATABASE_URL` (loaded via dotenv from `.env`)
- Define section ID mapping (matching existing seed scripts):
  - **GRE:** `examtypeid=1`, Quants → `sectionid=101`, Verbal → `sectionid=102`
  - **GMAT:** `examtypeid=2`, Quantitative → `sectionid=201`, Verbal → `sectionid=202`, Data Insights → `sectionid=203`
- Map QGen-FRESH section names to CompEx IDs:
  - "Quants" (GRE) → 101
  - "Verbal" (GRE) → 102
  - "Quants" (GMAT) → 201
  - "Verbal" (GMAT) → 202
  - "Integrated Reasoning" (GMAT) → 203 (confirmed: IR = Data Insights)
- Use `process.env.DATABASE_URL` from `.env` via dotenv (confirmed)

#### 1b. Tag Resolution

- Parse tags from each question's `tags` array (format: "topic: Ratio and Proportion")
- Extract tag name and category from the prefix ("topic:", "theme:", "question-type:")
- Upsert into `tags` table (name is unique)
- Upsert into `tag_scopes` table (unique on `tagid+examtypeid+sectionid`)
- Cache resolved `tagScopeIds` to avoid repeated DB lookups

#### 1c. Question Type Mapping

Map QGen-FRESH question-type to CompEx type + options_type:

| QGen-FRESH question-type | CompEx type | CompEx options_type |
|--------------------------|-------------|-------------------|
| Problem Solving Simple | Multiple Choice | single |
| Problem Solving Meta | Multiple Choice | single |
| Quantitative Comparison | Multiple Choice | single |
| Critical Reasoning | Multiple Choice | single |
| Data Sufficiency | Multiple Choice | single |
| Sentence Equivalence | Multiple Choice | multi |
| Text Completion (1/2/3 blank) | Multiple Choice | multi |
| Numerical Entry | Numeric Entry | single |
| Reading Comprehension | Multiple Choice | single |
| Graphic Interpretation | Multiple Choice | single |
| Table Analysis | Multiple Choice | single |
| Two-Part Analysis | Multiple Choice | single |
| Multi-Source Reasoning | Multiple Choice | single |

#### 1d. Standard Question Insertion (non-parent, non-child)

For each regular question (has question field, no child-questions):

```typescript
// Follow exact pattern from question-bot.ts (lines 212-243)
const problem = await prisma.problems.create({
  data: {
    title: q.title.substring(0, 200),         // VARCHAR(200) limit
    text: q.question,                          // Full question text
    difficulty: q.difficulty,                  // 1-5 (matches QGen-FRESH scale)
    sectionid: resolvedSectionId,
    examtypeid: resolvedExamTypeId,
    isMockQuestion: false,
    isActive: true,
    isChildren: false,
    type: mappedType,                          // e.g. "Multiple Choice"
    options_type: mappedOptionsType,           // "single" or "multi"
    prompt: q.prompt || null,
    solution: { text: q.solution, answer: q.answer },  // JSON field
    metadata: {
      generatedBy: 'QGen-FRESH-Import',
      questionType: q['question-type'],
      ...q.metadata                            // Passages, tables, graphs
    },
    addedDate: new Date(),
    problemoptions: {
      create: buildOptions(q.options, q.answer)
    }
  }
})

// Link to tag_scopes
for (const tagScopeId of resolvedTagScopeIds) {
  await prisma.problemtags.create({
    data: { problemid: problem.problemid, tagScopeId }
  })
}
```

#### 1e. Options Builder Logic

```typescript
function buildOptions(options, answer) {
  if (!options || options === null) return [];  // Numerical Entry has null options

  // Standard A-G options with text+explanation
  return Object.entries(options).map(([key, val]) => ({
    optiontext: val.text || String(val),
    iscorrect: determineCorrect(key, answer),
    group: key,                               // "A", "B", etc.
    explanation: val.explanation || null
  }));
}

function determineCorrect(key, answer) {
  if (typeof answer === 'string') return key === answer;
  if (Array.isArray(answer)) return answer.includes(key);
  return false;  // numeric/object answers → no option is "correct" in traditional sense
}
```

#### 1f. Parent-Child (RC/MSR) Question Insertion

For questions with `child-questions` array:

1. Create a `ProblemsSet` record:
   - `title`: parent.title
   - `type`: parent['question-type']
   - `sectionid`, `examtypeid`
   - `content`: { passage: parent.metadata.Passage, ...parent.metadata }

2. For each child-question, create a `problems` record:
   - `isChildren`: true
   - `problemsSetId`: the created ProblemsSet ID
   - `text`: child.question
   - All other fields same as standard questions
   - Link to parent's tag_scopes via `problemtags`

#### 1g. Deduplication

- Before inserting, check for existing questions with same `title + examtypeid + sectionid`
- Skip duplicates and log them
- This prevents re-running the script from creating duplicates

#### 1h. Execution & Reporting

- Process files one at a time, sections sequentially
- Wrap each question in try/catch (don't fail entire batch for one bad question)
- Log progress: file → section → question count
- Final summary: total inserted, skipped, errored

---

### Step 2: Generate Prisma client

```bash
cd ~/Desktop/CompEx && npx prisma generate
```

---

### Step 3: Run the import (with your approval)

```bash
cd ~/Desktop/CompEx && npx tsx scripts/data-management/import-qgen-fresh.ts
```

---

## Key Files

| File | Role |
|------|------|
| `~/Desktop/CompEx/scripts/data-management/import-qgen-fresh.ts` | NEW — the import script |
| `~/Desktop/CompEx/prisma/schema.prisma` | Reference for exact model fields |
| `~/Desktop/CompEx/scripts/automation/question-bot.ts` | Reference pattern for insertion (lines 212-243) |
| `~/Desktop/CompEx/scripts/data-management/seed-gmat-prod.ts` | Reference for section/exam IDs |
| `~/Desktop/CompEx/scripts/data-management/seed-tags-prod.ts` | Reference for tag upsert pattern |
| `~/Desktop/QGen-FRESH/log_json_files/paper/mega_papers/` | Source JSON files |

---

## Verification

After import completes:

- **Count check:** Query `SELECT COUNT(*) FROM problems WHERE metadata->>'generatedBy' = 'QGen-FRESH-Import'` — should be ~1,849
- **Options check:** Spot-check that `problemoptions` records exist for inserted problems
- **Tags check:** Verify `problemtags` links exist
- **ProblemsSet check:** Verify RC parent-child sets were created
- **Live check:** Visit https://www.compex.live/dashboard/problems and verify new questions appear
- **Type coverage:** Query distinct question-type values in metadata to confirm all types imported
