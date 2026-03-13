# User Analytics Types

This directory contains TypeScript type definitions for the user analytics feature.

## Overview

Currently, type definitions are distributed across various files in the user-analytics feature. This directory serves as a central location for shared type definitions and interfaces.

## Current Type Locations

### Timer Types

**timerDefinition.ts**
```typescript
interface QuestionTimer {
  questionId: number;
  startTime: number;
  elapsedTime: number; // in milliseconds
  isRunning: boolean;
  lastRecordedTime: number; // the time when user selected an option
  hasRecordedTime: boolean; // whether user has selected an option
}

interface TimerState {
  questionTimers: { [questionId: number]: QuestionTimer };
  currentQuestionId: number | null;
  showTimer: boolean; // global setting to show/hide timer in UI
  
  // Timer management methods
  startTimer: (questionId: number) => void;
  stopTimer: (questionId: number) => void;
  pauseTimer: (questionId: number) => void;
  resumeTimer: (questionId: number) => void;
  recordOptionSelectedTime: (questionId: number) => void;
  clearRecordedTime: (questionId: number) => void;
  getElapsedTime: (questionId: number) => number;
  getFormattedTime: (questionId: number) => string;
  
  // Settings
  setShowTimer: (show: boolean) => void;
}
```

### Result Types

**resultWindowDefinitions.ts**
```typescript
interface questionResult {
  type: string;
  problemid: number;
  correctoption: string[];
  title: string;
  selectedoption: string[];
  timetaken: string;
  
  // Display properties
  text: string;
  diagram: string | null;
  options: { optiontext: string; group: string }[];
  solution: string;
  difficulty: number;
  metadata: any;
}

interface resultdatadefinition {
  resultData: null | questionResult[];
  setResultData: (data: questionResult[]) => void;
}
```

### Component Props Types

**Timer Component**
```typescript
interface TimerProps {
  questionId: number;
  className?: string;
}
```

**Result Window Component**
```typescript
interface QuestionFloatingWindowProps {
  onClose: () => void;
}
```

## Recommended Type Definitions

The following types should be centralized in this directory:

### Performance Metrics Types

```typescript
interface PerformanceMetrics {
  userId: string;
  accuracy: number;
  totalQuestions: number;
  correctAnswers: number;
  averageTime: number;
  timeframe: string;
  examType?: string;
  sectionId?: string;
}

interface PerformanceFilters {
  dateRange?: {
    start: Date;
    end: Date;
  };
  examType?: string;
  section?: string;
  difficulty?: number[];
  tags?: string[];
}

interface PerformanceChartsProps {
  userId: string;
  timeframe?: string;
  examType?: string;
  sectionId?: string;
}
```

### Analytics Data Types

```typescript
interface UserAttempt {
  attemptId: string;
  userId: string;
  questionId: number;
  selectedOptions: string[];
  correctOptions: string[];
  isCorrect: boolean;
  timeSpent: number; // in milliseconds
  timestamp: Date;
  examType: string;
  section: string;
  tags: string[];
}

interface UserSession {
  sessionId: string;
  userId: string;
  startTime: Date;
  endTime: Date;
  totalQuestions: number;
  correctAnswers: number;
  accuracy: number;
  totalTime: number;
  examType: string;
  section: string;
}

interface TimeMetrics {
  questionId: number;
  averageTime: number;
  minTime: number;
  maxTime: number;
  questionType: string;
  difficulty: number;
}
```

### Chart Data Types

```typescript
interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

interface AccuracyTrendData {
  data: ChartDataPoint[];
  timeframe: string;
  examType?: string;
}

interface PerformanceByTypeData {
  type: string;
  accuracy: number;
  count: number;
  averageTime: number;
}

interface TimeVsAccuracyData {
  timeSpent: number;
  accuracy: number;
  questionCount: number;
}
```

### Store State Types

```typescript
interface AnalyticsState {
  currentSession: UserSession | null;
  performanceMetrics: PerformanceMetrics | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  updateMetrics: (attempt: UserAttempt) => void;
  startSession: (examType: string, section: string) => void;
  endSession: () => void;
  resetSession: () => void;
}

interface ResultsState {
  results: questionResult[];
  currentQuestionIndex: number;
  showResults: boolean;
  
  // Actions
  setResults: (results: questionResult[]) => void;
  navigateToQuestion: (index: number) => void;
  toggleResultsVisibility: (show: boolean) => void;
}
```

## Migration Plan

To improve type safety and maintainability, consider:

1. **Centralize Types**: Move all analytics-related types to this directory
2. **Create Index File**: Export all types from a single `index.ts` file
3. **Update Imports**: Update all feature files to import from centralized types
4. **Add Validation**: Create runtime type validation utilities

## Usage Guidelines

### Importing Types

```typescript
// Recommended approach (once centralized)
import type { 
  QuestionTimer, 
  PerformanceMetrics, 
  UserAttempt,
  AnalyticsState 
} from '@/features/user-analytics/types';

// Current approach (distributed)
import type { QuestionTimer } from '../hooks/timerDefinition';
import type { questionResult } from '../hooks/resultWindowDefinitions';
```

### Type Guards

```typescript
// Example type guards for runtime validation
function isValidTimer(value: any): value is QuestionTimer {
  return (
    typeof value === 'object' &&
    typeof value.questionId === 'number' &&
    typeof value.startTime === 'number' &&
    typeof value.isRunning === 'boolean'
  );
}

function isValidPerformanceMetrics(value: any): value is PerformanceMetrics {
  return (
    typeof value === 'object' &&
    typeof value.accuracy === 'number' &&
    value.accuracy >= 0 && value.accuracy <= 100
  );
}
```

## Integration Points

### With Other Features

- **Question Solving**: Receives attempt data and timing information
- **Exam Management**: Uses exam context for performance categorization
- **User Management**: Associates analytics with user profiles

### With External Libraries

- **Zustand**: Store state types should extend these base types
- **React Query**: API response types should use these interfaces
- **Chart Libraries**: Chart data should conform to these formats

## Future Enhancements

- Add strict typing for different chart types
- Create discriminated unions for different analytics views
- Add validation schemas using libraries like Zod
- Generate API client types from these definitions
- Add types for real-time analytics updates
