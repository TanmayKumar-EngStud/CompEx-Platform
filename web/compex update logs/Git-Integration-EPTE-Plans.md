# Git Integration: EPTE Plans in Version Control
## AI-Documented Codebase for Future Model Discovery

---

## The Vision

Every code change in your repo has a **companion EPTE plan** that explains:
- What was broken
- How it was fixed
- Steps taken
- Decisions made
- Error handling

Future searches (by you, Opus, Sonnet, or Haiku) find not just code, but the **reasoning behind it**.

```
git log --grep="Text Completion" --oneline
→ Shows all commits related to Text Completion
→ Each commit has full EPTE plan embedded
→ Future Claude knows exactly why each change was made
```

---

## Architecture

### 1. Directory Structure

```
your-repo/
├── .ai-plans/                          # NEW: AI execution plans
│   ├── features/
│   │   ├── mock-exam-fix.md           # Plan that fixed mock exam
│   │   ├── text-completion-layout.md  # Plan for TC display
│   │   └── user-feedback-validation.md
│   ├── bugs/
│   │   ├── cross-blank-selection.md   # Plan for TC selection bug
│   │   └── [issue-name].md
│   └── README.md                       # Index of all plans
├── src/
│   ├── components/
│   ├── pages/
│   └── ...
├── .gitignore
├── DEVELOPMENT.md                      # Links to plans
└── git-hooks/
    └── prepare-commit-msg.sh           # Custom hook
```

### 2. Commit Message Format

Every commit that fixes/implements a feature includes the plan:

```
commit abc123def456
Author: Haiku <haiku@compex.ai>
Date:   2025-02-15 14:30:00

    fix: Text Completion multi-blank display and selection isolation

    ## EPTE Plan: Text Completion Display & Selection Bug

    **Objective:** Fix TC display layout and prevent cross-blank selection

    **Changes Made:**
    - Updated TextCompletion.tsx with CSS Grid layout (1, 2, 3 columns)
    - Fixed Redux state to isolate selections by blankId
    - Updated OptionGroup to accept and use blankId prop
    - Verified all TC variants (TC-1, TC-2, TC-3) work independently

    **Files Modified:**
    - frontend/components/QuestionTypes/TextCompletion.tsx
    - frontend/components/OptionGroup.tsx
    - frontend/store/textCompletion.ts

    **Verification:**
    - [x] TC-1 displays 1 column layout
    - [x] TC-2 displays 2 column layout
    - [x] TC-3 displays 3 column layout
    - [x] Selection isolated per blank
    - [x] Answer verification works correctly

    **Plan Reference:** .ai-plans/bugs/cross-blank-selection.md
    **Executor:** Haiku 4.5
    **Execution Time:** 45 minutes
    **Tokens Used:** 3,200 Haiku tokens
```

---

## Step 1: Store EPTE Plans in `.ai-plans/` Directory

When Opus creates a plan, **save it with a standard naming convention:**

```
.ai-plans/
├── features/
│   └── [feature-name].md
├── bugs/
│   └── [bug-name].md
└── infra/
    └── [infrastructure-task].md
```

**Naming convention:** `kebab-case-descriptive-name.md`

Examples:
- `.ai-plans/bugs/mock-exam-loading-error.md`
- `.ai-plans/features/text-completion-table-layout.md`
- `.ai-plans/bugs/cross-blank-selection-contamination.md`
- `.ai-plans/infra/qgen-fresh-database-import.md`

---

## Step 2: Plan Header with Metadata

Every plan file starts with **YAML frontmatter** for searchability:

```markdown
---
title: "Fix: Text Completion Multi-Blank Display & Selection"
type: bug
status: completed
created: 2025-02-15
completed: 2025-02-15
executor: Haiku 4.5
planner: Opus 4.6
tokens_used: 3200
related_issue: "#142"
files_modified:
  - frontend/components/QuestionTypes/TextCompletion.tsx
  - frontend/components/OptionGroup.tsx
  - frontend/store/textCompletion.ts
tags:
  - text-completion
  - ui-bug
  - redux-state
  - frontend
---

# Plan: Fix Text Completion Multi-Blank Display & Selection Bug

## Objective
[Full plan content here...]
```

This frontmatter enables:
```bash
# Search by tag
git log --grep="text-completion" --all

# Search in .ai-plans/
grep -r "status: completed" .ai-plans/

# Filter by executor
grep -r "executor: Haiku" .ai-plans/
```

---

## Step 3: Commit Message Template

Create `.gitmessage` file in repo root:

```
# EPTE Commit Template
# Follow this format for all feature/bug commits

[type](scope): description

# If you have an EPTE plan, include it below:
---
## EPTE Plan
**Plan File:** .ai-plans/[category]/[name].md
**Planner:** [Opus/Sonnet/You]
**Executor:** [Haiku/You]
**Status:** [completed/in-progress]

## Changes Summary
- [What was changed]
- [How it was fixed]
- [Files modified]

## Verification Checklist
- [ ] All steps from plan were executed
- [ ] All success criteria met
- [ ] Tests pass
- [ ] No console errors

## Additional Notes
[Any deviations from plan, decisions made, etc.]

# Remember: Link to .ai-plans/ file above ☝️
```

Configure Git to use this template:

```bash
git config commit.template .gitmessage
```

Now every commit will prompt you with this template.

---

## Step 4: Git Hook for Automatic Plan Integration

Create `.git/hooks/prepare-commit-msg.sh`:

```bash
#!/bin/bash

# This hook ensures commit messages include EPTE plan references

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# If amending or merging, skip
if [ "$COMMIT_SOURCE" == "merge" ] || [ "$COMMIT_SOURCE" == "squash" ]; then
  exit 0
fi

# Check if .ai-plans/ directory exists
if [ -d ".ai-plans" ]; then
  # Extract the plan file reference if it exists
  PLAN_REF=$(grep -o "\.ai-plans/[^[:space:]]*" "$COMMIT_MSG_FILE" | head -1)
  
  if [ -z "$PLAN_REF" ]; then
    # No plan reference found - warn user
    echo ""
    echo "⚠️  WARNING: No .ai-plans/ reference found in commit message"
    echo "   If this commit fixes a feature/bug with an EPTE plan,"
    echo "   please add: .ai-plans/[category]/[plan-name].md"
    echo ""
  else
    # Plan reference found - verify file exists
    if [ ! -f "$PLAN_REF" ]; then
      echo "❌ ERROR: Plan file not found: $PLAN_REF"
      exit 1
    else
      echo "✅ Plan reference verified: $PLAN_REF"
    fi
  fi
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/prepare-commit-msg
```

---

## Step 5: `.ai-plans/README.md` - Index

Create `.ai-plans/README.md` as a searchable index:

```markdown
# AI Execution Plans Repository

This directory contains all EPTE (Explicit-Plan-Then-Execute) plans used to build CompEx.

Every plan here represents:
- **What was broken** (problem statement)
- **How it was fixed** (step-by-step plan)
- **Who executed it** (Opus/Sonnet/Haiku)
- **Time & cost** (tokens, hours)
- **Result** (success criteria met)

---

## Quick Search

### By Status

**Completed Plans** ✅
- [Text Completion Display Fix](./bugs/cross-blank-selection.md) - Haiku | 3.2k tokens
- [Mock Exam Loading Error](./bugs/mock-exam-loading-error.md) - Haiku | 2.1k tokens
- [User Feedback Validation](./features/user-feedback-validation.md) - Haiku | 1.5k tokens

**In Progress** 🔄
- [Real-time Notifications](./features/real-time-notifications.md) - Opus planning

**Archived** 📦
- [Legacy PDF Export](./features/pdf-export-v1.md) - Replaced by v2

### By Category

**Bugs** 🐛
- `cross-blank-selection.md`
- `mock-exam-loading-error.md`
- [Add more...]

**Features** ✨
- `user-feedback-validation.md`
- `gamification-leaderboard.md`
- [Add more...]

**Infrastructure** ⚙️
- `qgen-fresh-database-import.md`
- `prisma-migration-users-table.md`
- [Add more...]

### By Executor

**Haiku 4.5** 🐤
- [Cross-blank selection](./bugs/cross-blank-selection.md)
- [Mock exam error](./bugs/mock-exam-loading-error.md)
- [User feedback](./features/user-feedback-validation.md)

**Opus 4.6** 🧠
- [Bot evolution architecture](../docs/compex-bot-evolution-concept.md)
- [Database import strategy](./infra/qgen-fresh-database-import.md)

**You** 👨‍💻
- [Manual bug fixes](./manual/)

---

## For Future AI Models

When searching this codebase, check `.ai-plans/`:

```bash
# Find plan for Text Completion
find .ai-plans -name "*text*" -type f

# Search plans by tag
grep -r "tags:" .ai-plans | grep "text-completion"

# Find all completed Haiku tasks
grep -r "executor: Haiku" .ai-plans | grep "status: completed"

# List all plans modified in last month
find .ai-plans -type f -mtime -30
```

---

## Workflow: From Plan to Commit

### Phase 1: Create Plan (Opus)
```
Input: Problem description
Output: .ai-plans/category/name.md (with metadata)
```

### Phase 2: Review Plan (You)
```
Input: .ai-plans/category/name.md
Check: Is plan clear? Executable? 
Output: Approval ✅
```

### Phase 3: Execute (Haiku)
```
Input: .ai-plans/category/name.md
Execute: Step by step
Output: Code changes
```

### Phase 4: Commit (Git)
```
git add src/ .ai-plans/
git commit  # Template prompts you to reference plan

Message includes:
  - What changed
  - Link to .ai-plans/category/name.md
  - Verification checklist
  - Executor & tokens used

Output: Commit with full context
```

### Phase 5: Review (Future Claude)
```
git log --grep="text-completion" --all
→ Find all related commits
→ Each has link to .ai-plans/ file
→ Read full plan to understand decisions
→ Reuse/improve for similar tasks
```

---

## Example: Full Workflow

### 1. Opus Creates Plan

```
# Opus outputs to .ai-plans/bugs/cross-blank-selection.md

---
title: "Fix: Text Completion Cross-Blank Selection"
type: bug
status: in-progress
executor: Haiku 4.5
---

# Plan: Fix Text Completion Cross-Blank Selection Bug

## Objective
Fix issue where selecting option in Blank 1 auto-selects same option in Blank 2

## Steps
[Full plan...]
```

### 2. You Review & Approve

```
✅ Plan is clear
✅ Steps are explicit
✅ Error handling is defined
→ APPROVED

Give to Haiku
```

### 3. Haiku Executes

```
# Haiku modifies files:
frontend/components/QuestionTypes/TextCompletion.tsx
frontend/components/OptionGroup.tsx
frontend/store/textCompletion.ts

# Updates plan status:
status: completed
completed: 2025-02-15
```

### 4. Commit with Context

```bash
git add src/ .ai-plans/
git commit
```

Git template appears:
```
[fix](text-completion): isolate selection per blank

---
## EPTE Plan
**Plan File:** .ai-plans/bugs/cross-blank-selection.md
**Executor:** Haiku 4.5
**Status:** completed

## Changes
- Updated TextCompletion.tsx with CSS Grid layout
- Fixed Redux state to use blankId
- Verified independent selection for TC-1/2/3

## Verification
- [x] No cross-blank contamination
- [x] All TC variants display correctly
- [x] Answer verification works

Tokens Used: 3,200 (Haiku)
Execution Time: 45 minutes
```

### 5. Future Search

```bash
# 6 months later...

git log --all --grep="text-completion"
→ Finds commit with plan reference

cat .ai-plans/bugs/cross-blank-selection.md
→ Full context on why/how it was fixed

# Haiku in next project:
"I see this was fixed before. Let me check the plan..."
→ Learns from previous work
→ Makes better decisions next time
```

---

## Advanced: Plan Versioning

If a plan needs to be updated (bug in original fix):

```
.ai-plans/bugs/cross-blank-selection.md (v1)
.ai-plans/bugs/cross-blank-selection.v2.md (updated version)

In v2 frontmatter:
---
version: 2
supersedes: cross-blank-selection.md
reason: "Original fix had edge case with nullable options"
---
```

Commit message references both:
```
[fix](text-completion): handle nullable options in TC blanks

**Plan File:** .ai-plans/bugs/cross-blank-selection.v2.md
**Supersedes:** cross-blank-selection.md
**Reason:** Edge case with nullable options not handled in v1
```

---

## Dashboard View (for you)

Create `PLANS_SUMMARY.md` at repo root (auto-generated):

```markdown
# AI Plans Summary

Last Updated: 2025-02-15

## Stats
- Total Plans: 27
- Completed: 24 ✅
- In Progress: 2 🔄
- Archived: 1 📦

## Recent Executions
1. Cross-blank selection (Haiku) - 3.2k tokens - 45 min - ✅
2. Mock exam error (Haiku) - 2.1k tokens - 30 min - ✅
3. User feedback (Haiku) - 1.5k tokens - 20 min - ✅

## Token Efficiency
- Opus planning: 2,500 tokens/plan (upfront cost)
- Haiku execution: 2,500 tokens/plan (average)
- Total per feature: 5,000 tokens (vs 8,000 for Opus alone)

## Savings
- 37.5% token reduction from EPTE orchestration
- 100% auditability of decisions
- Reusable plans for similar problems
```

---

## Git Commands Cheat Sheet

```bash
# View all plans
find .ai-plans -name "*.md" -type f | sort

# Search for plans by tag
grep -r "tags:" .ai-plans | grep "text-completion"

# Find plans executed by Haiku
grep -r "executor: Haiku" .ai-plans | cut -d: -f1 | sort -u

# List completed plans
grep -r "status: completed" .ai-plans | wc -l

# Show commits with plan references
git log --all --grep="\.ai-plans" --oneline

# View plan from recent commit
git show HEAD:ai-plans/bugs/cross-blank-selection.md

# Blame to see who executed
git log -p .ai-plans/bugs/cross-blank-selection.md | head -50
```

---

## Integration with CI/CD

In `.github/workflows/plans-check.yml`:

```yaml
name: Verify EPTE Plans

on:
  pull_request:
    paths:
      - '.ai-plans/**'
      - 'src/**'

jobs:
  check-plan-references:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Verify plan files exist
        run: |
          # Extract plan references from commit message
          PLAN_FILES=$(git log --format=%B | grep -o '\.ai-plans/[^[:space:]]*' | sort -u)
          
          for plan in $PLAN_FILES; do
            if [ ! -f "$plan" ]; then
              echo "❌ Plan file not found: $plan"
              exit 1
            fi
          done
          echo "✅ All plan references valid"
      
      - name: Check plan frontmatter
        run: |
          # Verify all plans have required fields
          for plan in .ai-plans/**/*.md; do
            if ! grep -q "^---$" "$plan"; then
              echo "❌ Missing YAML frontmatter: $plan"
              exit 1
            fi
          done
          echo "✅ All plans have valid frontmatter"
```

---

## Setup Instructions (TL;DR)

1. **Create directory:**
   ```bash
   mkdir -p .ai-plans/{features,bugs,infra}
   ```

2. **Create `.ai-plans/README.md`** (template above)

3. **Create `.gitmessage`** (template above)

4. **Configure Git:**
   ```bash
   git config commit.template .gitmessage
   ```

5. **Add Git hook:**
   ```bash
   chmod +x .git/hooks/prepare-commit-msg
   ```

6. **Commit structure:**
   ```bash
   git add src/
   cp [opus-plan] .ai-plans/category/name.md
   git add .ai-plans/
   git commit  # Use template
   ```

7. **Verify:**
   ```bash
   git log --oneline -5
   # Should see commits referencing .ai-plans/ files
   ```

---

## Benefits

| Benefit | How it helps |
|---------|-------------|
| **Searchability** | Future Claude finds plan, not just code |
| **Context preservation** | Why was this changed, not just what changed |
| **Reusability** | Similar problem? Find old plan, adapt it |
| **Learning** | Haiku learns from patterns in completed plans |
| **Auditability** | Full decision trail for every change |
| **Efficiency** | Don't re-solve same problem twice |
| **Onboarding** | New team members understand decisions through plans |

---

## Future Enhancement: AI-Generated Plan Index

Imagine this in 6 months:

```bash
claude --index .ai-plans/

→ Reads all .ai-plans/*.md files
→ Builds semantic search index
→ Creates tags automatically
→ Generates cross-references

"Find plans related to Redux state management"
→ Returns 7 plans tagged with redux/state/frontend
```

This becomes your **codebase's institutional knowledge**.

---

## One More Thing: Plan Diff

Track changes to plans themselves:

```bash
git diff .ai-plans/bugs/cross-blank-selection.md
```

Shows:
- What was in original plan
- What was discovered during execution
- What was added/changed
- Why the change was necessary

This is your **learning feedback loop**.

