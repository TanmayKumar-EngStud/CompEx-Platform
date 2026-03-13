# User Analytics Hooks

This directory contains React hooks specific to the user analytics feature.

## Available Hooks

* **use-performance-metrics.ts**: Manages and calculates performance metrics
* **use-time-tracking.ts**: Tracks time spent on questions and sessions
* **use-results-processing.ts**: Processes and formats session results
* **use-analytics-filters.ts**: Manages filters for analytics data
* **use-chart-data.ts**: Prepares data for visualization components

## Hook Details

### use-performance-metrics.ts

Manages performance metrics calculation and state:

```typescript
function usePerformanceMetrics(userId: string) {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Fetches and calculates metrics
  // Updates when new attempts are made
  // Provides methods to filter by date range, exam type, etc.
  
  return { metrics, loading, error, refreshMetrics };
}
```

### use-time-tracking.ts

Handles time tracking for questions and study sessions:

```typescript
function useTimeTracking() {
  const [isActive, setIsActive] = useState(false);
  const [time, setTime] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Start, pause, resume, and reset timer
  // Track time per question
  // Calculate average time metrics
  
  return { time, isActive, start, pause, resume, reset, recordTime };
}
```

## Integration with Components

These hooks are used by analytics components to:
- Fetch and process analytics data
- Manage time tracking state
- Format data for visualization
- Filter and sort analytics information

## Integration with Services

These hooks use services from the analytics feature to:
- Fetch raw analytics data
- Submit timing information
- Process and store results

## Usage Example

```tsx
import { usePerformanceMetrics } from '@/features/user-analytics/hooks/use-performance-metrics';
import { PerformanceChart } from '@/features/user-analytics/components/performance-chart';

function UserPerformance({ userId }) {
  const { metrics, loading, error } = usePerformanceMetrics(userId);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div>
      <h2>Your Performance</h2>
      <PerformanceChart data={metrics.accuracyBySection} />
      <AccuracyMeter value={metrics.overallAccuracy} />
    </div>
  );
}
```