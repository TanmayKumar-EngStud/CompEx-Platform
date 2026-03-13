# CompEx Question Generation Automation

Automated AI-powered question generation pipeline for the CompEx GRE/GMAT exam preparation platform. This directory contains the core scripts that generate, insert, maintain, and evolve exam-quality questions using a multi-provider AI fallback chain.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Reference](#file-reference)
3. [AI Provider Chain](#ai-provider-chain)
4. [Chained Generation Pipeline](#chained-generation-pipeline)
5. [Template System](#template-system)
6. [Database Insertion Pattern](#database-insertion-pattern)
7. [RAG Toolkit](#rag-toolkit)
8. [Phase Cache](#phase-cache)
9. [Running the Scripts](#running-the-scripts)
10. [Environment Variables](#environment-variables)
11. [Directory Structure](#directory-structure)

---

## Architecture Overview

```
                     +--------------------+
                     |  paper-generator   |  (CLI batch tool)
                     |  question-bot      |  (continuous daemon)
                     +--------+-----------+
                              |
                              v
                     +--------------------+
                     | QuestionGenerator  |  (AI orchestrator)
                     +--------+-----------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        +-----------+   +-----------+   +-----------+
        | DeepSeek  |   |  Gemini   |   |  OpenAI   |
        | R1 (Tier1)|   | 1.5 Flash |   | GPT-4o-   |
        |           |   | (Tier 2)  |   | mini (T3) |
        +-----------+   +-----------+   +-----------+
              |
              v
        +-----------+
        | DeepSeek  |  (RAG-enabled tool calling
        | Chat      |   for evolve/feedback tasks)
        +-----------+
              |
              v
        +--------------------+
        | DeepSeekToolkit    |  (4 RAG tools)
        |  - search_questions|
        |  - get_pool_stats  |
        |  - read_source_file|
        |  - get_community_  |
        |    feedback        |
        +--------------------+

    +----------------+       +----------------+
    | TemplateEngine |------>| templates/     |
    | (Mustache-     |       |  system/       |
    |  style render) |       |  components/   |
    +----------------+       |  schemas/      |
                             +----------------+

    +----------------+
    | PhaseCache     |------> .cache/ (JSON files, 1-hour TTL)
    +----------------+

    +----------------+
    | evolve.ts      |------> COMMUNITY_FEEDBACK.md --> evolution_log.json
    +----------------+
```

---

## File Reference

### Core Generation Engine

#### `QuestionGenerator.ts`

The central AI orchestrator. All question generation flows through this class.

**Constructor** initializes:
- `TemplateEngine` for prompt template rendering
- `PhaseCache` for intermediate result caching
- `DeepSeekToolkit` for RAG tool execution
- Three AI provider clients (DeepSeek, Gemini, OpenAI)
- Gemini API key rotation array (parsed from comma-separated env var)

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `callAI(prompt, systemPrompt?)` | Main entry point. Routes to RAG-enabled chat for evolve/feedback tasks, otherwise falls through the 3-tier provider chain. |
| `callAIWithTools(prompt, systemPrompt?, recursionDepth?)` | RAG-enabled generation using DeepSeek Chat with tool calling. Recursive up to depth 5. Uses `DeepSeekToolkit` to execute tools and feeds results back to the model. |
| `fallbackAI(prompt, systemPrompt?)` | Tier 2+3 fallback: tries all Gemini keys with rotation on `RESOURCE_EXHAUSTED`, then falls to OpenAI GPT-4o-mini. |
| `generateWithGemini(prompt, apiKey, systemPrompt?)` | Direct Gemini 1.5 Flash REST API call with `responseMimeType: "application/json"`. |
| `generateChainedQuestion(scope, difficulty, templatePrefix, variation?)` | 4-phase chained generation pipeline (see section below). Returns a fully structured question object. |

**RAG routing logic** in `callAI`: If the prompt contains "evolve", "feedback", or "structure" keywords AND DeepSeek is configured, routes to `callAIWithTools` first. Falls back to standard chain on failure.

**One-shot detection**: During the metadata phase, if DeepSeek R1 returns a complete question (with `metadata`, `text`, `options`, and `solution` fields), the generator short-circuits the remaining phases by populating the cache with normalized data.

---

#### `TemplateEngine.ts`

Reads `.txt.template` files from `templates/` and renders them using Mustache-style `{{variable}}` interpolation.

**Methods:**

| Method | Purpose |
|--------|---------|
| `getSystemTemplate(name)` | Reads from `templates/system/{name}.txt.template` |
| `getComponentTemplate(name)` | Reads from `templates/components/{name}.txt.template` |
| `getSchema(name)` | Reads and parses from `templates/schemas/{name}.json.schema` |
| `render(template, values)` | Replaces all `{{key}}` placeholders. Objects are JSON-stringified. |

The template directory is resolved relative to `process.cwd()`, meaning scripts must be run from the project root.

---

#### `PhaseCache.ts`

File-system-based cache for intermediate chained generation results. Stores JSON files in `.cache/` with a 1-hour TTL.

**Cache key format**: `{scopeId}_d{difficulty}_{phase}.json`

Example: `GRE-quants-Data-Analysis_d4_metadata.json`

**Methods:**

| Method | Purpose |
|--------|---------|
| `get(scopeId, difficulty, phase)` | Returns cached data if file exists and is less than 1 hour old. Returns `null` otherwise. |
| `set(scopeId, difficulty, phase, data)` | Writes JSON data to cache file. |
| `clear(scopeId, difficulty)` | Deletes all 4 phase files (metadata, text, options, solution) for a given scope+difficulty. |

The cache enables **resumable generation**: if the pipeline fails at phase 3, phases 1 and 2 remain cached and do not need to be regenerated.

---

#### `DeepSeekToolkit.ts`

RAG (Retrieval-Augmented Generation) tool definitions and execution engine for DeepSeek Chat's function calling capability.

**Registered Tools (exported as `DEEPSEEK_TOOLS`):**

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `search_questions` | Searches existing questions in DB by topic/difficulty to ensure diversity and avoid duplicates. | `topic?: string`, `difficulty?: number`, `limit?: number` (default 5) |
| `get_pool_stats` | Returns question pool distribution stats grouped by difficulty and exam type. | None |
| `read_source_file` | Reads a project source file (max 5000 chars, with path traversal prevention). | `file_path: string` (required) |
| `get_community_feedback` | Returns contents of `COMMUNITY_FEEDBACK.md`. | None |

**Security**: `read_source_file` validates that the resolved absolute path starts with `process.cwd()` to prevent path traversal.

**Import note**: This file imports Prisma from `../../shared/lib/prisma` (the app's shared Prisma instance), unlike other scripts which instantiate their own `PrismaClient`.

---

### Entry Point Scripts

#### `question-bot.ts`

Continuous question generation daemon that runs on a 15-second interval.

**Execution flow per cycle:**
1. Fetches all `tag_scopes` from DB (with joined `tags`, `examtypes`, `sections`)
2. Randomly selects one scope and a random difficulty (1-5)
3. Determines template prefix:
   - **Quants**: Section name contains "quant" OR tag is Algebra/Arithmetic/Geometry
   - **Verbal**: Section name contains "verbal" OR tag includes Reading/Text/Critical
4. Routes to `generator.generateChainedQuestion()` for quants/verbal, or monolithic `callAI()` for other types
5. On AI failure, falls back to `SimulatedAI` (hardcoded procedural question templates for Algebra, Geometry, Reading Comprehension, Arithmetic)
6. Inserts `problems` record with nested `problemoptions` via Prisma
7. Links to `problemtags` via the selected `tagScopeId`

**SimulatedAI** is a static class with blueprint-based procedural generation. It produces:
- Algebra: linear equations, variable relationships
- Geometry: circle area (with SVG diagrams), triangle hypotenuse (with SVG), square perimeter (with SVG)
- Reading Comprehension: hardcoded passage with main-idea question
- Arithmetic: prime factorization from a lookup table
- Default fallback for any unrecognized topic

---

#### `paper-generator.ts`

Batch CLI tool built with Commander.js for generating question papers.

**CLI Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `-e, --exam <type>` | Exam name (GRE, GMAT) | `GMAT` |
| `-c, --count <number>` | Total questions to generate | `10` |
| `-p, --parallel <number>` | Concurrency limit | `5` |
| `-m, --mock <boolean>` | Mock exam batch (true/false) | `false` |
| `-d, --difficulty <number>` | Difficulty level (1-5) | `3` |
| `--cleanup` | Run autonomous garbage collection before generation | `true` |

**Execution flow:**
1. Optionally runs `performAutonomousMaintenance()` (if `--cleanup` is enabled)
2. Fetches all scopes for the specified exam
3. Shuffles scopes using Fisher-Yates algorithm for even distribution
4. Assigns each question a unique variation seed (`Batch-{timestamp}-{index}`) to prevent duplicates
5. Executes generation in parallel chunks limited by the concurrency flag
6. Each question goes through `generateChainedQuestion()` and is inserted to DB

**Autonomous Maintenance** (`performAutonomousMaintenance`):
- Queries `questionQualityMetrics` for questions with `qualityScore < threshold` (default 4.5/10)
- Deactivates low-quality active questions (`isActive = false`)
- For deactivated mock questions: searches for a high-quality practice question in the same tag scope and promotes it to mock status (`isMockQuestion = true`)

---

#### `evolve.ts`

AI-driven self-improvement engine that reads community feedback and proposes code changes.

**Execution flow:**
1. Reads `COMMUNITY_FEEDBACK.md` from project root
2. Scans `app/`, `shared/`, `features/` directories for `.ts/.tsx/.js/.jsx` files (skipping `node_modules`, `.next`, `public`, `.git`, `backups`)
3. Sends feedback + file list to `generator.callAI()` with a system prompt that enables RAG tool access
4. Parses the AI response as a JSON patch: `{ feedback_item, file_path, search_string, replacement_string, rationale }`
5. Validates the target file exists and the `search_string` is found
6. Performs a find-and-replace on the file
7. Appends the proposal to `evolution_log.json`

**RAG context**: The evolve system prompt tells the AI about available tools (`search_questions`, `get_pool_stats`, `read_source_file`, `get_community_feedback`). Because the prompt contains "evolve" and "feedback" keywords, `callAI` automatically routes to the RAG-enabled `callAIWithTools` path.

---

#### `apply-feedback.ts`

Lightweight feedback processing script. Reads `COMMUNITY_FEEDBACK.md`, extracts numbered items using regex, logs them, and writes a `last_run.json` metadata file. This is a simpler, non-AI alternative to `evolve.ts` -- it only identifies and logs feedback items without proposing code changes.

---

#### `deploy-check.ts`

Pre-deployment verification script that checks:
1. `zod` dependency is resolvable
2. `next` version from `package.json`
3. SWC version protection via `pnpm.overrides`
4. `@prisma/client` is available (runs `npx prisma generate` if missing)

---

#### `test-rag.ts`

Manual test script for verifying the DeepSeek RAG toolkit. Sends a prompt that should trigger multiple tool calls (`get_pool_stats` + `read_source_file`) and prints the AI response.

---

#### `idle-xp.ts`

Placeholder/experimental script for a "Presence XP" reward system. Currently only logs messages and does not perform meaningful database operations.

---

## AI Provider Chain

The `QuestionGenerator.callAI()` method implements a 3-tier fallback chain:

```
Tier 0 (Conditional): DeepSeek Chat with RAG Tools
  |  Only for evolve/feedback/structure prompts
  |  Model: deepseek-chat
  |  Recursive tool calling up to depth 5
  v
Tier 1: DeepSeek R1 (Reasoning)
  |  Model: deepseek-reasoner
  |  Timeout: 90 seconds
  |  Strips <think>...</think> tags from response
  |  System prompt injected into user message (R1 limitation)
  v
Tier 2: Google Gemini 1.5 Flash
  |  REST API (not SDK)
  |  Multiple API keys with rotation on RESOURCE_EXHAUSTED
  |  responseMimeType: "application/json"
  |  system_instruction field for system prompt
  v
Tier 3: OpenAI GPT-4o-mini
  |  Timeout: 15 seconds
  |  response_format: { type: "json_object" }
  v
  Error: All providers failed
```

All providers are instructed to return strictly valid JSON. Markdown code fences are stripped from responses as a safety measure.

---

## Chained Generation Pipeline

The `generateChainedQuestion()` method implements a 4-phase pipeline where each phase builds on the previous one:

```
Phase 1: METADATA          Phase 2: TEXT              Phase 3: OPTIONS          Phase 4: SOLUTION
+-----------------+        +-----------------+        +-----------------+       +-----------------+
| Input:          |        | Input:          |        | Input:          |       | Input:          |
|  - exam_type    |        |  - exam_type    |        |  - exam_type    |       |  - exam_type    |
|  - section_name |        |  - section_name |        |  - section_name |       |  - question_text|
|  - difficulty   |        |  - topic (from  |        |  - question_text|       |  - options      |
|  - requested_   |        |    Phase 1)     |        |    (from Ph. 2) |       |    (from Ph. 3) |
|    topic        |        |  - scenario     |        |                 |       |  - answer       |
|  - variation    |        |    (from Ph. 1) |        |                 |       |    (from Ph. 3) |
|    seed         |        |  - difficulty   |        |                 |       |                 |
+-----------------+        +-----------------+        +-----------------+       +-----------------+
| Output:         |        | Output:         |        | Output:         |       | Output:         |
|  topic          |        |  question_text  |        |  options (A-E/F)|       |  solution       |
|  theme          |        |                 |        |  answer         |       |   (markdown)    |
|  difficulty_    |        |                 |        |  explanations   |       |                 |
|  guidelines     |        |                 |        |                 |       |                 |
+-----------------+        +-----------------+        +-----------------+       +-----------------+
```

**Template prefix routing**: The pipeline uses either `quants-*` or `verbal-*` templates based on the `templatePrefix` parameter. Each prefix has its own system template and 4 component templates.

**Cache key includes variation**: Variation seeds (e.g., `Batch-1770246807299-3`) are appended to cache keys as `metadata_v{variation}`, preventing cache collisions when generating multiple questions for the same scope.

**One-shot shortcut**: If DeepSeek R1 returns a complete question during the metadata phase (detected by the presence of `metadata`, `text`, and `options` fields), the pipeline populates all caches except the solution cache, forcing only Phase 4 to run with the strict solution template.

**Return structure:**
```typescript
{
  title: string,           // metadata.topic
  text: string,            // question_text
  options: Array<{
    text: string,
    isCorrect: boolean,
    explanation?: string
  }>,
  explanation: string,     // solution text
  metadata: {
    topic: string,
    theme: string,
    difficulty_guidelines: string,
    explanations: Record<string, string>
  }
}
```

---

## Template System

Templates live in `templates/` and use Mustache-style `{{variable}}` placeholders.

### System Templates (`templates/system/`)

These set the AI's persona and output format constraints. They are passed as the `systemPrompt` parameter.

| Template | Purpose |
|----------|---------|
| `quants-generic.txt.template` | Psychometrician persona for quantitative reasoning. Enforces multi-step logic, ambiguity elimination, plausible distractors, and double-escaped LaTeX. |
| `verbal-generic.txt.template` | Psychometrician persona for verbal reasoning. Enforces nuance, logical rigor, academic tone. Specifies format rules per question type (TC, SE, RC, CR). |

### Component Templates (`templates/components/`)

Each corresponds to one pipeline phase. They are passed as the user-facing prompt (after variable rendering).

| Template | Variables | Output Schema |
|----------|-----------|---------------|
| `quants-metadata.txt.template` | `exam_type`, `section_name`, `difficulty` | `{ topic, theme, difficulty_guidelines }` |
| `quants-text.txt.template` | `exam_type`, `section_name`, `topic`, `difficulty`, `scenario` | `{ question_text }` |
| `quants-options.txt.template` | `exam_type`, `section_name`, `question_text` | `{ options: {A-E}, answer, explanations }` |
| `quants-solution.txt.template` | `exam_type`, `question_text`, `options`, `answer` | `{ solution }` |
| `verbal-metadata.txt.template` | `exam_type`, `section_name`, `requested_topic`, `difficulty` | `{ topic, theme, difficulty_guidelines }` |
| `verbal-text.txt.template` | `exam_type`, `section_name`, `topic`, `scenario`, `difficulty` | `{ question_text }` |
| `verbal-options.txt.template` | `exam_type`, `section_name`, `question_text` | `{ options: {A-F}, answer: [] }` |
| `verbal-solution.txt.template` | `exam_type`, `question_text`, `options`, `answer` | `{ solution }` |

### JSON Schemas (`templates/schemas/`)

Draft-07 JSON Schema files for validating AI output (currently available for quants phases only):

| Schema | Validates |
|--------|-----------|
| `quants-metadata.json.schema` | `{ topic: string, theme: string, difficulty_guidelines: string }` |
| `quants-text.json.schema` | `{ question_text: string }` (minLength: 10) |
| `quants-options.json.schema` | `{ options: {A-E: string}, answer: enum[A-E], explanations: {A-E: string} }` |
| `quants-solution.json.schema` | `{ solution: string }` (minLength: 50) |

Note: The schemas are loaded by `TemplateEngine.getSchema()` but are not currently enforced in the generation pipeline. They exist for reference and potential future validation.

---

## Database Insertion Pattern

All scripts use Prisma ORM with `DATABASE_URL` from `.env.production`.

**Insertion flow (both `question-bot` and `paper-generator`):**

```typescript
// 1. Create problem with nested options
const problem = await prisma.problems.create({
  data: {
    title: string,
    text: string,
    difficulty: number,          // 1-5
    sectionid: number,           // from tag_scope
    examtypeid: number,          // from tag_scope
    isMockQuestion: boolean,     // false for bot, configurable for paper-gen
    type: 'Multiple Choice',
    addedDate: new Date(),
    metadata: {                  // JSONB field
      generatedBy: string,       // 'Bot Swarm' or 'DeepSeek Parallel Batch'
      topic: string,
      explanation: string,
      // ... additional metadata from AI
    },
    problemoptions: {
      create: options.map((opt, idx) => ({
        optiontext: string,
        iscorrect: boolean,
        group: 'A' | 'B' | 'C' | 'D' | 'E'  // String.fromCharCode(65 + idx)
      }))
    }
  }
});

// 2. Link to tag scope
await prisma.problemtags.create({
  data: {
    problemid: problem.problemid,
    tagScopeId: scope.tagScopeId
  }
});
```

**Tables involved:**
- `problems` -- Main question record
- `problemoptions` -- Answer choices (one-to-many from problems)
- `problemtags` -- Links problems to `tag_scopes` (many-to-many join)
- `tag_scopes` -- Defines exam/section/tag combinations (joined with `examtypes`, `sections`, `tags`)
- `questionQualityMetrics` -- Used by maintenance to find low-quality questions

---

## RAG Toolkit

The RAG (Retrieval-Augmented Generation) system enables the AI to query the database and filesystem during generation, primarily used by the `evolve.ts` script.

**How it works:**
1. `QuestionGenerator.callAI()` detects RAG-eligible prompts (containing "evolve", "feedback", or "structure")
2. Routes to `callAIWithTools()` which calls DeepSeek Chat (not R1) with `tools` and `tool_choice: "auto"`
3. If the model requests tool calls, `DeepSeekToolkit.executeTool()` runs them against the DB/filesystem
4. Results are fed back to the model in a recursive call (max depth 5)
5. The model produces its final response incorporating the tool results

This gives the AI access to live database statistics and source code when making evolution decisions.

---

## Phase Cache

The `.cache/` directory stores intermediate generation results as JSON files.

**Cache key naming convention:**
```
{ExamType}-{SectionName}-{TagName}_d{difficulty}_{phase}_v{variation}.json
```

Examples from an actual run:
```
GRE-quants-Data-Analysis_d4_metadata.json
GRE-verbal-Sentence-Equivalence_d3_text_vBatch-1770246533010-3.json
GMAT-Quants-Arithmetic_d3_metadata_vBatch-1770246807299-3.json
```

**TTL**: 1 hour. After that, `PhaseCache.get()` returns `null` and the phase is regenerated.

**Purpose**: Enables resumable generation. If the pipeline fails at Phase 3, cached Phase 1 and Phase 2 results are reused on retry, saving API calls and cost.

---

## Running the Scripts

All scripts must be run from the **project root directory** (`/path/to/CompEx/`), not from the `scripts/automation/` directory. This is because template paths and Prisma schema resolution are relative to `process.cwd()`.

### Continuous Bot (15-second interval)

```bash
npx tsx scripts/automation/question-bot.ts
```

Runs indefinitely. Generates one question per 15-second cycle from a random tag scope. Press Ctrl+C to stop.

### Batch Paper Generation

```bash
# Generate 10 GMAT practice questions at difficulty 3
npx tsx scripts/automation/paper-generator.ts -e GMAT -c 10

# Generate 20 GRE mock exam questions at difficulty 4, 3 parallel
npx tsx scripts/automation/paper-generator.ts -e GRE -c 20 -p 3 -m true -d 4

# Skip garbage collection
npx tsx scripts/automation/paper-generator.ts -e GMAT -c 5 --no-cleanup
```

### Evolution Engine

```bash
pnpm evolve
```

This is defined in `package.json` as `tsx scripts/automation/evolve.ts`. Reads `COMMUNITY_FEEDBACK.md` and proposes one code change per run.

### RAG Test

```bash
npx tsx scripts/automation/test-rag.ts
```

Verifies that DeepSeek tool calling is working correctly.

### Deployment Check

```bash
npx tsx scripts/automation/deploy-check.ts
```

Validates dependencies before build/deploy.

### Feedback Processing

```bash
npx tsx scripts/automation/apply-feedback.ts
```

Reads and logs feedback items from `COMMUNITY_FEEDBACK.md` without AI.

---

## Environment Variables

All scripts load from `.env.production` in the project root via `dotenv.config({ path: '.env.production', override: true })`.

| Variable | Required | Used By | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | All scripts | PostgreSQL connection string for Prisma |
| `DEEPSEEK_API_KEY` | Recommended | QuestionGenerator | DeepSeek R1 (reasoning model). If missing, Tier 1 is skipped. |
| `GOOGLE_AI_STUDIO_KEYS` | Recommended | QuestionGenerator | Comma-separated Gemini API keys for rotation. Also accepts `GOOGLE_AI_STUDIO_KEY` (single key). |
| `OPENAI_API_KEY` | Optional | QuestionGenerator | GPT-4o-mini fallback. Set to `'N/A'` to skip. |
| `DEEPSEEK_CHAT_API_KEY` | Optional | DeepSeekToolkit | Used for RAG tool calling via DeepSeek Chat. Falls back to `DEEPSEEK_API_KEY` if not set (same client). |

**Minimum viable configuration**: `DATABASE_URL` + at least one of `DEEPSEEK_API_KEY`, `GOOGLE_AI_STUDIO_KEYS`, or `OPENAI_API_KEY`. Without any AI key, the question-bot falls back to `SimulatedAI` procedural generation.

---

## Directory Structure

```
scripts/automation/
|-- QuestionGenerator.ts       Core AI orchestrator with 3-tier fallback
|-- TemplateEngine.ts          Mustache-style template renderer
|-- PhaseCache.ts              File-based cache with 1-hour TTL
|-- DeepSeekToolkit.ts         RAG tool definitions and execution
|-- question-bot.ts            Continuous generation daemon (15s interval)
|-- paper-generator.ts         Batch CLI tool (Commander.js)
|-- evolve.ts                  AI-driven code evolution from feedback
|-- apply-feedback.ts          Lightweight feedback log processor
|-- deploy-check.ts            Pre-deployment dependency verification
|-- test-rag.ts                Manual RAG toolkit test script
|-- idle-xp.ts                 Experimental idle reward system (placeholder)
|-- evolution_log.json         Append-only log of evolution proposals
|-- last_run.json              Metadata from last apply-feedback run
|-- .cache/                    Phase cache directory (auto-created)
|   |-- {ScopeId}_d{N}_{phase}.json
|   +-- ...
+-- templates/
    |-- system/
    |   |-- quants-generic.txt.template
    |   +-- verbal-generic.txt.template
    |-- components/
    |   |-- quants-metadata.txt.template
    |   |-- quants-text.txt.template
    |   |-- quants-options.txt.template
    |   |-- quants-solution.txt.template
    |   |-- verbal-metadata.txt.template
    |   |-- verbal-text.txt.template
    |   |-- verbal-options.txt.template
    |   +-- verbal-solution.txt.template
    +-- schemas/
        |-- quants-metadata.json.schema
        |-- quants-text.json.schema
        |-- quants-options.json.schema
        +-- quants-solution.json.schema
```
