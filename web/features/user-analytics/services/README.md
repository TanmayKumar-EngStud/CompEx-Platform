# User Analytics Services

This directory contains service functions that handle business logic for the user analytics feature.

## Available Services

-  **analytics-queries.ts**: Functions to fetch analytics data
-  **performance-calculator.ts**: Calculates performance metrics
-  **time-analyzer.ts**: Analyzes time spent on questions
-  **progress-tracker.ts**: Tracks progress through question sets

## Service Details

### analytics-queries.ts

Functions for fetching analytics data:

```typescript
// Fetch user performance metrics
async function fetchPerformanceMetrics(
   userId: string,
   filters?: PerformanceFilters
) {
   // Fetches overall performance metrics
   // Can be filtered by date range, exam type, section
}

// Fetch time spent metrics
async function fetchTimeMetrics(userId: string, filters?: TimeFilters) {
   // Fetches time spent on different question types
   // Includes average, min, max time per question
}

// Fetch session history
async function fetchSessionHistory(userId: string, limit: number = 10) {
   // Fetches recent study sessions
   // Includes session duration, questions attempted, accuracy
}

// Fetch performance by tag
async function fetchPerformanceByTag(userId: string) {
   // Fetches performance metrics grouped by question tags
   // Used for strength/weakness analysis
}
```

### performance-calculator.ts

Functions for calculating performance metrics:

```typescript
// Calculate overall accuracy
function calculateAccuracy(attempts: Attempt[]) {
   // Calculates percentage of correct answers
   // Can be filtered by question type, difficulty
}

// Calculate improvement over time
function calculateImprovement(historicalAttempts: Attempt[]) {
   // Analyzes improvement trends over time
   // Returns percentage improvement and trend data
}

// Calculate strengths and weaknesses
function calculateStrengthsWeaknesses(
   attemptsByTag: Record<string, Attempt[]>
) {
   // Identifies strongest and weakest areas based on tags
   // Returns sorted lists of strengths and weaknesses
}

// Calculate performance percentile
function calculatePercentile(userId: string, metrics: PerformanceMetrics) {
   // Compares user performance to others
   // Returns percentile ranking
}
```

### time-analyzer.ts

Functions for analyzing time spent on questions:

```typescript
// Analyze time efficiency
function analyzeTimeEfficiency(attempts: Attempt[]) {
   // Compares time spent vs. correctness
   // Identifies optimal time spending patterns
}

// Calculate average time by question type
function calculateAverageTimeByType(attempts: Attempt[]) {
   // Groups and averages time spent by question type
   // Used for time management recommendations
}

// Identify time-consuming question types
function identifyTimeConsumingTypes(attempts: Attempt[]) {
   // Finds question types that take longest to answer
   // Used for focused practice recommendations
}
```

### progress-tracker.ts

Functions for tracking progress through question sets:

```typescript
// Calculate completion percentage
function calculateCompletion(
   totalQuestions: number,
   attemptedQuestions: number
) {
   // Returns percentage of questions completed
   // Used for progress indicators
}

// Track daily/weekly goals
function trackGoals(
   userId: string,
   goals: StudyGoals,
   currentProgress: StudyProgress
) {
   // Compares current progress against set goals
   // Returns completion status and recommendations
}

// Calculate streak data
function calculateStreak(userId: string, attemptDates: Date[]) {
   // Calculates current streak of consecutive study days
   // Returns streak count and history
}

// Generate progress report
function generateProgressReport(userId: string, timeframe: string) {
   // Creates comprehensive progress report
   // Includes completion, accuracy, and time metrics
}
```

## Integration with API

These services interact with the following API endpoints:

-  `/api/analytics/performance` - Fetch performance metrics
-  `/api/analytics/time-spent` - Fetch time metrics
-  `/api/analytics/sessions` - Fetch session history
-  `/api/analytics/progress` - Fetch progress data

## Integration with Components

These services are used by:

-  Performance chart components to visualize metrics
-  Progress tracker components to show completion
-  Streak counter components to display streaks
-  Results summary components to show session results

## Error Handling

All services include proper error handling:

-  API request failures
-  Data validation errors
-  Edge cases (no attempts, division by zero)
-  Timeout handling

## Data Processing

These services handle complex data processing:

-  Aggregating metrics across different dimensions
-  Calculating trends and patterns
-  Normalizing data for comparison
-  Formatting data for visualization
