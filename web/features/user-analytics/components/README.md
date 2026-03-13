# User Analytics Components

This directory contains React components specific to the user analytics feature.

## Available Components

### Actual Components

-  **timer/**: Timer-related components for tracking question time
-  **result-window/**: Components for displaying results and analysis

### Example Components (Documentation)

-  **performance-charts.tsx**: Visual charts showing performance metrics (example)
-  **accuracy-meter.tsx**: Visual indicator of answer accuracy (example)
-  **streak-counter.tsx**: Displays user's current streak (example)
-  **time-tracker.tsx**: Tracks and displays time spent on questions (example)
-  **results-summary.tsx**: Summary of session results (example)

## Component Details

### performance-charts.tsx

Charts for visualizing performance metrics:

```tsx
interface PerformanceChartsProps {
   userId: string;
   timeframe?: string;
   examType?: string;
   sectionId?: string;
}

function PerformanceCharts({
   userId,
   timeframe = "30d",
   examType,
   sectionId,
}: PerformanceChartsProps) {
   const { metrics, loading, error } = usePerformanceMetrics(userId, {
      timeframe,
      examType,
      sectionId,
   });

   if (loading) return <LoadingSpinner />;
   if (error) return <ErrorMessage error={error} />;

   return (
      <div className="performance-charts">
         <div className="chart-container">
            <h3>Accuracy Over Time</h3>
            <LineChart
               data={metrics.accuracyTrend}
               xKey="date"
               yKey="accuracy"
               yAxisLabel="Accuracy (%)"
            />
         </div>

         <div className="chart-container">
            <h3>Performance by Question Type</h3>
            <BarChart
               data={metrics.accuracyByType}
               xKey="type"
               yKey="accuracy"
               yAxisLabel="Accuracy (%)"
            />
         </div>

         <div className="chart-container">
            <h3>Time Spent vs. Accuracy</h3>
            <ScatterChart
               data={metrics.timeVsAccuracy}
               xKey="timeSpent"
               yKey="accuracy"
               xAxisLabel="Avg. Time (seconds)"
               yAxisLabel="Accuracy (%)"
            />
         </div>
      </div>
   );
}
```

### accuracy-meter.tsx

Visual indicator of answer accuracy:

```tsx
interface AccuracyMeterProps {
   value: number;
   size?: "small" | "medium" | "large";
   showLabel?: boolean;
}

function AccuracyMeter({
   value,
   size = "medium",
   showLabel = true,
}: AccuracyMeterProps) {
   // Determine color based on accuracy value
   const getColor = (accuracy: number) => {
      if (accuracy >= 80) return "#4CAF50"; // Green
      if (accuracy >= 60) return "#FFC107"; // Yellow
      return "#F44336"; // Red
   };

   const color = getColor(value);
   const sizeClass = `accuracy-meter-${size}`;

   return (
      <div className={`accuracy-meter ${sizeClass}`}>
         <div className="meter-container">
            <svg viewBox="0 0 100 100">
               <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e6e6e6"
                  strokeWidth="10"
               />
               <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={color}
                  strokeWidth="10"
                  strokeDasharray={`${value * 2.83} 283`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
               />
            </svg>
            <div className="meter-value" style={{ color }}>
               {Math.round(value)}%
            </div>
         </div>
         {showLabel && <div className="meter-label">Accuracy</div>}
      </div>
   );
}
```

### timer (Directory)

Contains timer-related components for tracking time spent on questions:

#### timer.tsx

Real-time timer component that tracks time spent on individual questions:

```tsx
interface TimerProps {
   questionId: number;
   className?: string;
}

function Timer({ questionId, className = "" }: TimerProps) {
   // Uses useTimerStore for state management
   // Displays formatted time (MM:SS)
   // Shows running/paused/completed status indicators
   // Includes blink animation when user selects an option
   // Can be globally enabled/disabled via settings

   return (
      <div className={`flex items-center gap-2 ${className}`}>
         {/* Timer display with icon */}
         {/* Status indicators (running, paused, completed) */}
         {/* Last recorded time tooltip */}
      </div>
   );
}
```

**Features:**

-  Real-time timer updates every second
-  Visual status indicators (green dot for running, yellow for paused)
-  Blink animation when user records time by selecting an option
-  Displays last recorded time in tooltip
-  Respects global timer visibility settings

### result-window (Directory)

Contains components for displaying question results and analysis:

#### resultWindow.tsx

Modal component that displays detailed results after completing a question set:

```tsx
interface ResultWindowProps {
   Attempt: any[];
   resultData: any[];
   onClose: () => void;
}

function ResultWindow({ Attempt, resultData, onClose }: ResultWindowProps) {
   // Displays overall session results
   // Shows individual question details
   // Provides navigation between questions
   // Calculates accuracy and performance metrics

   return (
      <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
         {/* Modal content with results summary */}
         {/* Question navigation and details */}
         {/* Performance metrics display */}
      </div>
   );
}
```

**Features:**

-  Modal overlay with backdrop blur
-  Results summary with total questions, score, and accuracy
-  Individual question review with correct/incorrect indicators
-  Navigation between questions in the result set
-  Solution display for each question
-  Performance metrics and time analysis

## Component Architecture

### State Management

The components use Zustand stores for state management:

-  **Timer Store**: Manages timer state for all questions
-  **Results Store**: Handles result data and navigation

### Integration Points

-  **Question Solving Feature**: Receives attempt data and question IDs
-  **Timer System**: Tracks time spent per question
-  **Performance Analytics**: Calculates metrics from attempt data

## Usage Examples

### Timer Component

```tsx
// Basic usage in a question component
<Timer questionId={123} />

// With custom styling
<Timer questionId={123} className="absolute top-4 right-4" />
```

### Result Window

```tsx
// Display results after completing a question set
<ResultWindow
   Attempt={userAttempts}
   resultData={processedResults}
   onClose={() => setShowResults(false)}
/>
```

## Styling

Components use Tailwind CSS classes and follow the application's design system:

-  Consistent color scheme with theme support
-  Responsive design for different screen sizes
-  Smooth animations and transitions
-  Accessible color contrasts and indicators
