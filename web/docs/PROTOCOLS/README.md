# CompEx Professional Development Protocols

_Building Production-Ready Software, Not College Projects_

## 🎯 From College Project to Business Product

### The Mindset Shift

As a fresh BTech graduate building your first serious product, it's crucial to adopt **professional development practices** from day one. This document will transform your development approach from "adding files here and there" to building a **scalable, maintainable business application**.

### Why This Matters

-  **Maintainability**: You'll thank yourself in 6 months when you can find and fix bugs quickly
-  **Scalability**: Your code structure should support growth, not hinder it
-  **Professional Growth**: These practices will make you a better developer
-  **Business Value**: Clean code = faster development = better product

## 🏗️ Production-Ready Architecture Principles

### 1. Domain-Driven Structure

Think of your application as a **business domain**, not just code files:

```
❌ College Project Approach:
/components/QuestionDisplay.tsx
/pages/problems.tsx
/utils/helpers.js
/api/getData.js

✅ Business Product Approach:
/features/exam-management/
/features/question-solving/
/features/user-analytics/
/shared/ui-components/
```

### 2. Feature-First Organization

Every business feature should be **self-contained and discoverable**:

-  Related components, services, and utilities should be co-located
-  A new developer (or future you) should immediately understand the structure
-  Avoid scattering similar functionality across multiple locations

### 3. Clear Separation of Concerns

-  **Presentation Layer**: UI components that only handle display
-  **Business Logic Layer**: Services that handle core application logic
-  **Data Access Layer**: Database queries and API calls
-  **State Management Layer**: Application state and user interactions

## 🏢 Professional Folder Structure

### 1. Feature-First Organization

-  Every feature should be self-contained and easily locatable
-  Related components, services, and utilities should be co-located
-  Avoid scattering similar functionality across multiple locations

### 2. Consistent Naming Conventions

-  Use `kebab-case` for folders and files
-  Use `PascalCase` for React components
-  Use `camelCase` for functions and variables
-  Use descriptive names that indicate purpose and scope

### 3. Single Responsibility Principle

-  Each file should have one clear purpose
-  Services should handle specific business logic areas
-  Components should be focused and reusable

This is your **business-grade folder structure** that scales from startup to enterprise:

```
/compex/                          # Root directory
├── 📁 app/                      # Next.js App Router (Pages & API)
│   ├── 📁 (dashboard)/          # Route groups for layout organization
│   │   ├── 📁 problems/         # Feature: Problem Solving
│   │   │   ├── 📁 components/   # Page-specific components
│   │   │   │   ├── problem-list.tsx
│   │   │   │   ├── question-window.tsx
│   │   │   │   └── answer-form.tsx
│   │   │   ├── 📁 hooks/        # Page-specific hooks
│   │   │   │   ├── use-problem-navigation.ts
│   │   │   │   └── use-answer-submission.ts
│   │   │   ├── page.tsx         # Problems page
│   │   │   └── loading.tsx      # Loading state
│   │   ├── 📁 analytics/        # Feature: User Analytics
│   │   │   ├── 📁 components/
│   │   │   └── page.tsx
│   │   └── layout.tsx           # Dashboard layout
│   ├── 📁 api/                  # API Routes (Business Logic Entry Points)
│   │   ├── 📁 problems/         # Problems API endpoints
│   │   │   ├── route.ts         # GET/POST /api/problems
│   │   │   ├── 📁 [id]/         # Individual problem operations
│   │   │   │   ├── route.ts     # GET/PUT/DELETE /api/problems/[id]
│   │   │   │   └── 📁 attempts/
│   │   │   │       └── route.ts # POST /api/problems/[id]/attempts
│   │   │   └── 📁 tags/
│   │   │       └── route.ts     # GET /api/problems/tags
│   │   ├── 📁 analytics/
│   │   │   └── route.ts
│   │   └── 📁 auth/
│   │       └── route.ts
│   ├── globals.css              # Global styles
│   └── layout.tsx               # Root layout
│
├── 📁 features/                 # 🔥 CORE BUSINESS FEATURES
│   ├── 📁 exam-management/      # Feature: Exam Type & Section Management
│   │   ├── 📁 components/       # Feature-specific UI components
│   │   │   ├── exam-selector.tsx
│   │   │   ├── section-filter.tsx
│   │   │   └── difficulty-badge.tsx
│   │   ├── 📁 services/         # Business logic for this feature
│   │   │   ├── exam-queries.ts  # Data fetching logic
│   │   │   ├── exam-mutations.ts # Data modification logic
│   │   │   └── exam-validations.ts # Business rules
│   │   ├── 📁 stores/          # Feature-specific state
│   │   │   ├── exam-store.ts    # Zustand store
│   │   │   └── exam-selectors.ts # State selectors
│   │   ├── 📁 hooks/           # Feature-specific hooks
│   │   │   ├── use-exam-selection.ts
│   │   │   └── use-section-filtering.ts
│   │   ├── 📁 types/           # Feature-specific types
│   │   │   └── exam.types.ts
│   │   └── index.ts            # Feature exports
│   │
│   ├── 📁 question-solving/    # Feature: Question Display & Solving
│   │   ├── 📁 components/
│   │   │   ├── 📁 templates/   # Question type templates
│   │   │   │   ├── data-sufficiency.tsx
│   │   │   │   ├── reading-comprehension.tsx
│   │   │   │   └── numeric-entry.tsx
│   │   │   ├── question-display.tsx
│   │   │   ├── answer-options.tsx
│   │   │   ├── solution-viewer.tsx
│   │   │   └── progress-tracker.tsx
│   │   ├── 📁 services/
│   │   │   ├── question-queries.ts
│   │   │   ├── answer-mutations.ts
│   │   │   ├── solution-formatter.ts
│   │   │   └── progress-calculator.ts
│   │   ├── 📁 stores/
│   │   │   ├── question-store.ts
│   │   │   ├── answer-store.ts
│   │   │   └── progress-store.ts
│   │   ├── 📁 hooks/
│   │   │   ├── use-question-navigation.ts
│   │   │   ├── use-answer-submission.ts
│   │   │   └── use-solution-display.ts
│   │   ├── 📁 types/
│   │   │   ├── question.types.ts
│   │   │   └── answer.types.ts
│   │   └── index.ts
│   │
│   ├── 📁 user-analytics/      # Feature: Performance Analytics
│   │   ├── 📁 components/
│   │   │   ├── performance-charts.tsx
│   │   │   ├── streak-counter.tsx
│   │   │   └── accuracy-meter.tsx
│   │   ├── 📁 services/
│   │   │   ├── analytics-queries.ts
│   │   │   ├── metrics-calculator.ts
│   │   │   └── report-generator.ts
│   │   ├── 📁 stores/
│   │   │   └── analytics-store.ts
│   │   ├── 📁 hooks/
│   │   │   └── use-performance-metrics.ts
│   │   └── index.ts
│   │
│   └── 📁 user-management/     # Feature: Authentication & User Profile
│       ├── 📁 components/
│       ├── 📁 services/
│       ├── 📁 stores/
│       └── index.ts
│
├── 📁 shared/                  # 🔧 SHARED/REUSABLE CODE
│   ├── 📁 components/          # Reusable UI components
│   │   ├── 📁 ui/             # Design system components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── modal.tsx
│   │   │   └── data-table.tsx
│   │   ├── 📁 forms/          # Form-related components
│   │   │   ├── form-field.tsx
│   │   │   ├── validation-message.tsx
│   │   │   └── submit-button.tsx
│   │   ├── 📁 layouts/        # Layout components
│   │   │   ├── main-layout.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── header.tsx
│   │   └── 📁 feedback/       # User feedback components
│   │       ├── loading-spinner.tsx
│   │       ├── error-boundary.tsx
│   │       └── toast-notification.tsx
│   │
│   ├── 📁 hooks/              # Reusable custom hooks
│   │   ├── use-local-storage.ts
│   │   ├── use-debounce.ts
│   │   ├── use-api.ts
│   │   └── use-theme.ts
│   │
│   ├── 📁 lib/                # Core utilities and configurations
│   │   ├── 📁 utils/          # Helper functions
│   │   │   ├── formatting.ts   # Data formatting utilities
│   │   │   ├── validation.ts   # Common validation functions
│   │   │   ├── api-client.ts   # API client setup
│   │   │   └── math-helpers.ts # Mathematical calculations
│   │   ├── 📁 constants/      # Application constants
│   │   │   ├── exam-types.ts   # Exam type definitions
│   │   │   ├── question-types.ts # Question type constants
│   │   │   ├── routes.ts       # Application routes
│   │   │   └── theme.ts        # Theme configuration
│   │   ├── 📁 types/          # Global TypeScript definitions
│   │   │   ├── api.types.ts    # API response types
│   │   │   ├── database.types.ts # Database model types
│   │   │   └── common.types.ts # Common utility types
│   │   └── 📁 configs/        # Configuration files
│   │       ├── database.ts     # Database configuration
│   │       ├── auth.ts         # Authentication setup
│   │       └── env.ts          # Environment variables
│   │
│   └── 📁 styles/             # Global styles and theme
│       ├── globals.css         # Global CSS
│       ├── components.css      # Component-specific styles
│       └── themes/
│           ├── light.css
│           └── dark.css
│
├── 📁 prisma/                 # 💾 DATABASE LAYER
│   ├── schema.prisma          # Database schema
│   ├── 📁 migrations/         # Database migrations
│   ├── 📁 seeds/             # Database seeding scripts
│   │   ├── problems.ts
│   │   ├── users.ts
│   │   └── index.ts
│   └── 📁 queries/           # Complex raw queries (if needed)
│
├── 📁 docs/                  # 📚 DOCUMENTATION
│   ├── api.md                # API documentation
│   ├── deployment.md          # Deployment guide
│   ├── database.md           # Database schema documentation
│   └── contributing.md       # Development guide
│
├── 📁 tests/                 # 🧪 TESTING
│   ├── 📁 __mocks__/         # Test mocks
│   ├── 📁 features/          # Feature tests
│   │   ├── question-solving.test.ts
│   │   └── user-analytics.test.ts
│   ├── 📁 shared/            # Shared utility tests
│   ├── 📁 e2e/              # End-to-end tests
│   └── setup.ts             # Test configuration
│
├── 📁 public/               # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── 📁 scripts/              # 🛠️ BUILD & DEPLOYMENT SCRIPTS
│   ├── build.js             # Custom build scripts
│   ├── deploy.js            # Deployment scripts
│   └── setup-db.js          # Database setup
│
└── 📁 PROTOCOLS/            # 📋 PROJECT PROTOCOLS
    ├── README.md            # This file
    └── OPTIMIZATION.md      # Performance optimization guide
```

### 🎯 Key Principles Behind This Structure

1. **Feature-Driven Development**: Each business feature is self-contained
2. **Clear Separation**: Shared code vs feature-specific code
3. **Scalable**: Easy to add new features without restructuring
4. **Discoverable**: Anyone can find what they need quickly
5. **Professional**: Follows industry best practices

## 🎓 Solo Developer Success Guidelines

### The Professional Developer Mindset

As a solo developer fresh out of BTech, you need to think like a **senior developer from day one**:

#### 1. **Think Before You Code**

```typescript
// ❌ College approach: "I need a function to get data"
function getData() {
   // Just write code and hope it works
}

// ✅ Professional approach: "I need a reusable service for problem queries"
interface ProblemQuery {
   examType?: string;
   section?: string;
   difficulty?: string;
   limit?: number;
}

class ProblemQueryService {
   async getProblems(query: ProblemQuery): Promise<Problem[]> {
      // Well-structured, typed, testable code
   }
}
```

#### 2. **Always Consider the Future**

-  **Will this code be easy to modify in 6 months?**
-  **Can I add new exam types without breaking existing code?**
-  **Is this component reusable for similar features?**
-  **How will this perform with 10,000 questions?**

#### 3. **Documentation is Code**

```typescript
/**
 * Calculates user performance metrics for a specific exam section
 *
 * @param userId - The user's unique identifier
 * @param examType - Type of exam (GRE, GMAT, CAT)
 * @param sectionId - Specific section within the exam
 * @param timeframe - Period to analyze (7d, 30d, 90d, all)
 * @returns Performance metrics including accuracy, speed, and trends
 *
 * @example
 * const metrics = await calculatePerformanceMetrics('user123', 'GRE', 'verbal', '30d')
 * console.log(`Accuracy: ${metrics.accuracy}%`)
 */
export async function calculatePerformanceMetrics(
   userId: string,
   examType: ExamType,
   sectionId: string,
   timeframe: Timeframe = "30d"
): Promise<PerformanceMetrics> {
   // Implementation
}
```

## 🔧 Professional Development Workflow

### Daily Development Routine

```bash
# Start of day
1. git pull origin main
2. pnpm install  # Check for dependency updates
3. pnpm lint     # Ensure code quality
4. pnpm dev      # Start development

# During development
5. Write tests FIRST (or alongside code)
6. Run tests frequently
7. Commit small, focused changes
8. Write meaningful commit messages

# End of day
9. pnpm build    # Ensure production build works
10. pnpm lint    # Final code quality check
11. Push to remote branch
```

### Feature Development Process

```typescript
// Step 1: Define the problem clearly
interface FeatureRequirement {
   name: string;
   description: string;
   userStory: string;
   acceptanceCriteria: string[];
   technicalRequirements: string[];
}

// Step 2: Design the solution
interface FeatureDesign {
   components: ComponentSpec[];
   services: ServiceSpec[];
   apiEndpoints: ApiSpec[];
   stateManagement: StateSpec[];
   databaseChanges?: SchemaChange[];
}

// Step 3: Implement incrementally
// Step 4: Test thoroughly
// Step 5: Document and deploy
```

## 🛠️ Production-Ready Bug Fixing Protocol

### Step 1: Reproduce and Document

```typescript
// Create a bug report template
interface BugReport {
   title: string;
   description: string;
   stepsToReproduce: string[];
   expectedBehavior: string;
   actualBehavior: string;
   environment: {
      browser: string;
      device: string;
      userAgent: string;
   };
   severity: "critical" | "high" | "medium" | "low";
   affectedFeatures: string[];
}
```

### Step 2: Identify the Root Cause (Professional Approach)

1. **UI/Component Issues** → Check `/features/[feature]/components/`
2. **Business Logic Issues** → Check `/features/[feature]/services/`
3. **Data/API Issues** → Check `/app/api/[feature]/`
4. **State Management Issues** → Check `/features/[feature]/stores/`
5. **Database Issues** → Check `/prisma/` and related services

### Step 3: Fix with Test Coverage

```typescript
// Before fixing, write a test that reproduces the bug
test("should handle empty question list gracefully", () => {
   const { getByText } = render(<QuestionList questions={[]} />);
   expect(getByText("No questions available")).toBeInTheDocument();
});

// Then fix the bug
// Then verify the test passes
```

### Step 2: Locate the Specific File

Follow this naming convention to find files quickly:

```typescript
// For problems-related bug in question display
app / dashboard / problems / components / question - display.tsx;

// For problems service logic
services / problems / queries.ts;

// For problems API endpoint
app / api / problems / route.ts;

// For problems state management
stores / problems / state.ts;
```

### Step 3: Fix and Test

1. Make the minimal necessary change
2. Test the specific feature affected
3. Run `pnpm lint` to ensure code quality
4. Run related tests if available
5. Check for side effects in related components

### Step 4: Professional Fix Documentation

```typescript
// Git commit message template
// Type: Brief description (50 chars max)
//
// Longer explanation if needed
// - What was the problem?
// - How does this fix solve it?
// - Any side effects or considerations?
//
// Fixes: #issue-number

// Example:
// fix: handle empty question list in QuestionDisplay component
//
// The component was crashing when no questions were available
// due to accessing undefined array properties. Added proper
// null checks and empty state handling.
//
// - Added EmptyState component
// - Updated QuestionList to handle empty arrays
// - Added unit tests for edge cases
//
// Fixes: #123
```

### Step 5: Prevent Future Occurrences

-  Add validation to prevent similar issues
-  Update documentation if the issue reveals a knowledge gap
-  Consider if the architecture needs improvement

## 🆕 New Feature Development Protocol

### Step 1: Planning Phase

1. **Define the feature scope** - What exactly needs to be built?
2. **Identify affected areas** - Which existing components/services will be modified?
3. **Plan the data flow** - From API to UI, how will data move?
4. **Design the component hierarchy** - What new components are needed?

### Step 2: Structure Creation

```bash
# Create feature structure
mkdir -p app/[feature-name]
mkdir -p app/[feature-name]/components
mkdir -p services/[feature-name]
mkdir -p stores/[feature-name]

# If API endpoints needed
mkdir -p app/api/[feature-name]
```

### Step 3: Development Order

1. **Database Schema** (if needed) - Update Prisma schema
2. **Types** - Define TypeScript interfaces in `/lib/types/`
3. **Services** - Create business logic in `/services/[feature]/`
4. **API Routes** - Create endpoints in `/app/api/[feature]/`
5. **State Management** - Create stores in `/stores/[feature]/`
6. **Components** - Build UI components
7. **Integration** - Connect everything together
8. **Styling** - Apply theme-consistent styling

### Step 4: Quality Assurance

-  Ensure responsive design
-  Test in both light and dark themes
-  Verify accessibility standards
-  Test error scenarios
-  Check performance implications

## 📋 Professional Naming Conventions

### The Psychology of Good Names

**Good names reduce cognitive load.** Your future self (and other developers) should understand the purpose immediately.

### File Naming Standards

```typescript
// ✅ EXCELLENT - Clear, descriptive, consistent
features / question - solving / components / question - display.tsx;
features / question - solving / services / answer - validation.ts;
features / user - analytics / hooks / use - performance - metrics.ts;

// ❌ AVOID - Unclear, inconsistent, unprofessional
components / QuestionDisplay.tsx;
services / problemsService.ts;
hooks / useStuff.ts;
utils / helpers.ts;
```

### Component Naming Patterns

```typescript
// Feature Components (in features/[feature]/components/)
exam - selector.tsx; // Selects exam type
question - display.tsx; // Displays a single question
answer - form.tsx; // Handles answer submission
progress - tracker.tsx; // Shows user progress

// Shared Components (in shared/components/)
loading - spinner.tsx; // Generic loading indicator
error - boundary.tsx; // Error handling wrapper
data - table.tsx; // Reusable table component
modal - dialog.tsx; // Generic modal
```

### Service Naming Patterns

```typescript
// Feature Services (in features/[feature]/services/)
question - queries.ts; // GET operations for questions
answer - mutations.ts; // POST/PUT operations for answers
performance - calculator.ts; // Business logic for metrics
report - generator.ts; // Generate user reports

// Shared Services (in shared/lib/)
api - client.ts; // HTTP client configuration
validation - rules.ts; // Common validation logic
data - formatter.ts; // Data transformation utilities
```

### API Route Naming (RESTful)

```typescript
// ✅ PROFESSIONAL RESTful structure
app / api / problems / route.ts; // GET/POST /api/problems
app / api / problems / [id] / route.ts; // GET/PUT/DELETE /api/problems/123
app / api / problems / [id] / attempts / route.ts; // POST /api/problems/123/attempts
app / api / users / [id] / analytics / route.ts; // GET /api/users/123/analytics

// ❌ AVOID - Non-RESTful, unclear
app / api / getProblems / route.ts;
app / api / submitAnswer / route.ts;
app / api / userStats / route.ts;
```

### Variable and Function Naming

```typescript
// Business Domain Language (use your exam prep terminology)
interface ExamAttempt {
   problemId: string;
   selectedAnswer: string;
   timeSpentSeconds: number;
   isCorrect: boolean;
   submittedAt: Date;
}

// Clear, descriptive function names
function calculateAccuracyPercentage(attempts: ExamAttempt[]): number;
function generatePerformanceReport(userId: string, timeframe: string): Report;
function validateAnswerFormat(
   answer: string,
   questionType: QuestionType
): boolean;

// Avoid generic names
function processData(); // ❌ What data? How?
function handleClick(); // ❌ Handle what? Do what?
function doStuff(); // ❌ Completely unclear
```

## 🏗️ Professional Component Development

### Production-Ready Component Template

```typescript
'use client'

// External imports (libraries)
import { useState, useEffect, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'

// Internal imports (your code)
import { cn } from '@/shared/lib/utils'
import { Button } from '@/shared/components/ui/button'
import { useQuestionSolving } from '@/features/question-solving/hooks'

// Types (always define interfaces)
interface QuestionDisplayProps {
  questionId: string
  showSolution?: boolean
  onAnswerSubmit?: (answer: string) => void
  className?: string
  'data-testid'?: string  // For testing
}

interface QuestionDisplayState {
  selectedAnswer: string | null
  timeSpent: number
  isSubmitting: boolean
}

/**
 * Displays a single exam question with answer options and solution
 *
 * Features:
 * - Supports all question types (DS, RC, CR, etc.)
 * - Tracks time spent on question
 * - Handles answer validation
 * - Responsive design with accessibility
 *
 * @param questionId - Unique identifier for the question
 * @param showSolution - Whether to show the solution immediately
 * @param onAnswerSubmit - Callback when user submits an answer
 */
export function QuestionDisplay({
  questionId,
  showSolution = false,
  onAnswerSubmit,
  className,
  'data-testid': testId = 'question-display'
}: QuestionDisplayProps) {
  // ===== HOOKS =====
  const {
    question,
    submitAnswer,
    isLoading,
    error
  } = useQuestionSolving(questionId)

  // ===== STATE =====
  const [state, setState] = useState<QuestionDisplayState>({
    selectedAnswer: null,
    timeSpent: 0,
    isSubmitting: false
  })

  // ===== COMPUTED VALUES =====
  const isAnswered = useMemo(() => state.selectedAnswer !== null, [state.selectedAnswer])
  const canSubmit = useMemo(() => isAnswered && !state.isSubmitting, [isAnswered, state.isSubmitting])

  // ===== EFFECTS =====
  useEffect(() => {
    const timer = setInterval(() => {
      setState(prev => ({ ...prev, timeSpent: prev.timeSpent + 1 }))
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // ===== HANDLERS =====
  const handleAnswerSelect = useCallback((answer: string) => {
    setState(prev => ({ ...prev, selectedAnswer: answer }))
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!canSubmit || !state.selectedAnswer) return

    setState(prev => ({ ...prev, isSubmitting: true }))

    try {
      await submitAnswer(state.selectedAnswer)
      onAnswerSubmit?.(state.selectedAnswer)
    } catch (error) {
      console.error('Failed to submit answer:', error)
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }))
    }
  }, [canSubmit, state.selectedAnswer, submitAnswer, onAnswerSubmit])

  // ===== RENDER GUARDS =====
  if (isLoading) {
    return <div data-testid={`${testId}-loading`}>Loading question...</div>
  }

  if (error) {
    return <div data-testid={`${testId}-error`}>Error: {error.message}</div>
  }

  if (!question) {
    return <div data-testid={`${testId}-not-found`}>Question not found</div>
  }

  // ===== MAIN RENDER =====
  return (
    <motion.div
      className={cn(
        "flex flex-col gap-6 p-6 bg-background border border-border rounded-lg",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      data-testid={testId}
    >
      {/* Question Content */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-foreground">
          {question.title}
        </h2>
        <div
          className="prose dark:prose-invert"
          dangerouslySetInnerHTML={{ __html: question.content }}
        />
      </div>

      {/* Answer Options */}
      <div className="space-y-2">
        {question.options.map((option, index) => (
          <Button
            key={option.id}
            variant={state.selectedAnswer === option.value ? "default" : "outline"}
            className="w-full justify-start text-left"
            onClick={() => handleAnswerSelect(option.value)}
            data-testid={`${testId}-option-${index}`}
          >
            {option.label}: {option.text}
          </Button>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          Time: {Math.floor(state.timeSpent / 60)}:{(state.timeSpent % 60).toString().padStart(2, '0')}
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!canSubmit}
          data-testid={`${testId}-submit`}
        >
          {state.isSubmitting ? 'Submitting...' : 'Submit Answer'}
        </Button>
      </div>

      {/* Solution (if enabled) */}
      {showSolution && question.solution && (
        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h3 className="font-semibold mb-2">Solution:</h3>
          <div
            className="prose dark:prose-invert text-sm"
            dangerouslySetInnerHTML={{ __html: question.solution }}
          />
        </div>
      )}
    </motion.div>
  )
}

// Always export as default for better tree-shaking
export default QuestionDisplay
```

### Component Architecture Categories

#### 1. **Feature Components** (`/features/[feature]/components/`)

-  **Purpose**: Handle specific business logic for a feature
-  **Examples**: `question-display.tsx`, `exam-selector.tsx`, `performance-chart.tsx`
-  **Characteristics**:
   -  Contains business logic
   -  May connect to stores/APIs
   -  Feature-specific styling

#### 2. **Shared UI Components** (`/shared/components/ui/`)

-  **Purpose**: Reusable design system components
-  **Examples**: `button.tsx`, `input.tsx`, `modal.tsx`, `data-table.tsx`
-  **Characteristics**:
   -  No business logic
   -  Highly reusable
   -  Consistent styling
   -  Well-documented props

#### 3. **Layout Components** (`/shared/components/layouts/`)

-  **Purpose**: Define page and section structure
-  **Examples**: `main-layout.tsx`, `sidebar.tsx`, `header.tsx`
-  **Characteristics**:
   -  Handle page structure
   -  Responsive design
   -  Consistent spacing

#### 4. **Form Components** (`/shared/components/forms/`)

-  **Purpose**: Handle form inputs and validation
-  **Examples**: `form-field.tsx`, `validation-message.tsx`, `submit-button.tsx`
-  **Characteristics**:
   -  Form validation logic
   -  Accessibility features
   -  Error handling

### Component Quality Checklist

````typescript
// ✅ Every component should have:
interface ComponentQualityChecklist {
  // Type Safety
  hasProperTypeScript: boolean      // All props typed
  hasInterfaceDefinitions: boolean  // Clear interfaces

  // Documentation
  hasJSDocComments: boolean        // Function documentation
  hasUsageExamples: boolean        // How to use it

  // Functionality
  hasErrorHandling: boolean        // Handles edge cases
  hasLoadingStates: boolean        // Loading indicators
  hasAccessibility: boolean        // ARIA labels, keyboard nav

  // Testing
  hasTestId: boolean               // data-testid attributes
  isTestable: boolean              // Can be unit tested

  // Performance
  usesMemoization: boolean         // useMemo, useCallback where needed
  avoidsUnnecessaryRenders: boolean // React.memo if needed

  // User Experience
  hasResponsiveDesign: boolean     // Works on all screen sizes
  hasConsistentStyling: boolean    // Follows design system
  hasProperAnimations: boolean     // Smooth transitions
}

## 🔄 State Management Protocol

### When to Use Different State Solutions
1. **Local Component State** - `useState` for component-only data
2. **Feature State** - Zustand store for feature-wide state
3. **Global State** - Zustand store for cross-feature state
4. **Server State** - React Query/SWR for API data

### Store Organization
```typescript
// stores/problems/state.ts
interface ProblemsState {
  // state shape
}

interface ProblemsActions {
  // actions shape
}

export const useProblemsStore = create<ProblemsState & ProblemsActions>()((set, get) => ({
  // implementation
}))

// stores/problems/selectors.ts
export const selectCurrentProblem = (state: ProblemsState) => state.currentProblem
export const selectFilteredProblems = (state: ProblemsState) => state.filteredProblems
````

## 🎨 Styling Protocol

### CSS Class Organization

```typescript
// Use Tailwind with consistent patterns
const styles = {
   container: "flex flex-col gap-4 p-6",
   header: "text-xl font-semibold text-foreground",
   content: "flex-1 overflow-auto",
   footer: "flex justify-end gap-2 pt-4 border-t",
};

// Use CSS variables for theme consistency
className = "bg-background text-foreground border-border";
```

### Component Styling Guidelines

1. Use Tailwind utility classes first
2. Use CSS variables for theme colors
3. Create custom CSS classes for complex layouts only
4. Ensure consistent spacing using Tailwind's scale

## 🔍 Debugging Protocol

### Quick Debug Checklist

1. **Check Console** - Look for JavaScript errors
2. **Check Network Tab** - Verify API calls and responses
3. **Check React DevTools** - Inspect component state and props
4. **Check Database** - Use Prisma Studio to verify data
5. **Check Service Layer** - Add logging to service functions

### Common Issue Locations

```typescript
// Performance issues
stores/[feature]/state.ts // Large state objects
services/[feature]/queries.ts // Inefficient queries
components/[feature]/ // Unnecessary re-renders

// Data issues
app/api/[feature]/route.ts // API logic errors
services/[feature]/transformers.ts // Data transformation
prisma/schema.prisma // Database schema

// UI issues
components/ui/ // Design system components
app/[feature]/components/ // Feature components
styles/ // Global styles and theme
```

## 📈 Performance Optimization Guidelines

### Code Splitting

```typescript
// Use dynamic imports for heavy components
const HeavyComponent = dynamic(() => import("./heavy-component"), {
   loading: () => <div>Loading...</div>,
});

// Use React.lazy for route-level components
const FeaturePage = lazy(() => import("./feature-page"));
```

### Memoization Strategy

```typescript
// Memoize expensive calculations
const expensiveValue = useMemo(() => {
   return computeExpensiveValue(data);
}, [data]);

// Memoize components with complex props
const MemoizedComponent = memo(Component, (prevProps, nextProps) => {
   return prevProps.id === nextProps.id;
});
```

## 🧪 Testing Protocol

### Test Organization

```
__tests__/
├── components/
│   ├── ui/
│   └── [feature]/
├── services/
│   └── [feature]/
├── hooks/
└── utils/
```

### Testing Strategy

1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - Component interactions
3. **API Tests** - Backend endpoint testing
4. **E2E Tests** - Critical user flows

## 🚀 Deployment and Maintenance

### Pre-deployment Checklist

-  [ ] Run `pnpm lint` and fix all issues
-  [ ] Run `pnpm build` successfully
-  [ ] Test critical user flows
-  [ ] Verify responsive design
-  [ ] Check console for errors
-  [ ] Update documentation if needed

### Code Review Guidelines

1. **Functionality** - Does it work as expected?
2. **Performance** - Any performance implications?
3. **Security** - No exposed secrets or vulnerabilities?
4. **Maintainability** - Is the code readable and well-organized?
5. **Consistency** - Follows established patterns and conventions?

## 📝 Documentation Standards

### Code Comments

-  Explain **why**, not **what**
-  Document complex business logic
-  Add JSDoc comments for public APIs
-  Use TODO comments for known technical debt

### README Updates

-  Update API documentation for new endpoints
-  Document new environment variables
-  Update setup instructions if changed
-  Document breaking changes

## 🔧 Tools and Commands

### Essential Commands

```bash
# Development
pnpm dev                    # Start development server
pnpm build                  # Build for production
pnpm lint                   # Run ESLint
pnpm lint:fix              # Fix auto-fixable lint issues

# Database
pnpm seed                   # Seed database
npx prisma migrate dev      # Run migrations
npx prisma generate         # Generate client
npx prisma studio           # Database GUI

# Maintenance
pnpm audit                  # Check for vulnerabilities
pnpm outdated              # Check for outdated packages
```

### Development Workflow

1. Create feature branch from `main`
2. Follow the protocols above for development
3. Test thoroughly
4. Run linting and fix issues
5. Create pull request with clear description
6. Address review feedback
7. Merge when approved

---

**Remember**: These protocols are living documents. Update them as the project evolves and new patterns emerge.
