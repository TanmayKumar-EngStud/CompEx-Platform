# User Analytics Feature

This feature tracks and displays user performance metrics, progress, and results.

## Components

* **performance-charts.tsx**: Visual charts showing performance metrics
* **accuracy-meter.tsx**: Visual indicator of answer accuracy
* **streak-counter.tsx**: Displays user's current streak
* **time-tracker.tsx**: Tracks and displays time spent on questions
* **results-summary.tsx**: Summary of session results

## Services

* **analytics-queries.ts**: Functions to fetch analytics data
* **performance-calculator.ts**: Calculates performance metrics
* **time-analyzer.ts**: Analyzes time spent on questions
* **progress-tracker.ts**: Tracks progress through question sets

## Hooks

* **use-performance-metrics.ts**: Manages performance data
* **use-time-tracking.ts**: Handles time tracking logic
* **use-results-processing.ts**: Processes and formats results

## Stores

* **analytics-store.ts**: Zustand store for analytics state
* **timer-store.ts**: Zustand store for timer state

## Integration Flow

1. User answers questions in the question-solving feature
2. `time-tracker.tsx` records time spent on each question
3. `use-performance-metrics.ts` calculates accuracy and other metrics
4. `performance-charts.tsx` displays visual representation of metrics
5. After completing a session, `results-summary.tsx` shows overall performance

## API Interactions

- Fetches user performance from `/api/analytics/performance`
- Fetches time metrics from `/api/analytics/time-spent`
- Submits session results to `/api/analytics/sessions`
- Retrieves historical data from `/api/analytics/history`

## Data Models

This feature interacts with the following database models:
- `UserAttempt`: Records of user's question attempts
- `UserSession`: Information about study sessions
- `UserPerformance`: Aggregated performance metrics
- `TimeMetrics`: Time spent on different question types

## State Management

The analytics state is managed through Zustand stores:

```typescript
// Example of analytics-store.ts structure
interface AnalyticsState {
  accuracy: number;
  questionsAttempted: number;
  correctAnswers: number;
  averageTime: number;
  updateMetrics: (attempt: UserAttempt) => void;
  resetSession: () => void;
}
```

## Integration with Other Features

- **Question Solving**: Receives attempt data for analysis
- **Exam Management**: Uses exam context for categorizing metrics
- **User Management**: Associates analytics with user profiles