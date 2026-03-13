# Priority Caching Implementation Guide

## Overview

The Priority Caching system has been implemented to solve the performance issue where all data was being fetched simultaneously on page reload. Now, data is fetched intelligently based on priority levels:

1. **IMMEDIATE** - Current exam/section (highest priority)
2. **HIGH** - Related sections within same exam
3. **MEDIUM** - Other exam types
4. **LOW** - Background/idle loading

## Architecture

### Core Components

- **PriorityCacheManager** (`/shared/lib/cache/priority-cache.ts`) - Main orchestrator
- **BackgroundCacheService** (`/shared/services/background-cache-service.ts`) - Handles background fetching
- **Enhanced Hooks** - Priority-aware versions of existing hooks
- **UI Components** - Progress indicators and feedback

### Key Features

- **Intelligent Prioritization** - Loads critical data first
- **Background Loading** - Non-blocking lower priority data
- **Network Awareness** - Adapts to connection quality
- **User Behavior Learning** - Optimizes based on usage patterns
- **Memory Management** - Automatic cleanup and optimization

## Usage

### 1. Basic Integration

```tsx
// Wrap your app with the priority cache provider
import { PriorityCacheProvider } from '@/shared/components/providers/priority-cache-provider';

function App() {
  return (
    <PriorityCacheProvider showProgress={true}>
      <YourApp />
    </PriorityCacheProvider>
  );
}
```

### 2. Using Enhanced Hooks

```tsx
// Replace existing hooks with priority-aware versions
import { usePaginatedProblemsWithPriority } from '@/features/question-solving/hooks/(pagination)/fetchProblemsWithPriority';

function ProblemsPage() {
  const { data, loadingState, cacheStats } = usePaginatedProblemsWithPriority();
  
  return (
    <div>
      {loadingState.immediate && <div>Loading critical data...</div>}
      {/* Your existing component code */}
    </div>
  );
}
```

### 3. Manual Priority Control

```tsx
import { usePriorityCacheContext } from '@/shared/components/providers/priority-cache-provider';

function ExamSectionSelector() {
  const { initializePriorityCache, updateUserBehavior } = usePriorityCacheContext();
  
  const handleExamChange = async (exam: string, section: string) => {
    // Trigger priority caching for new exam/section
    await initializePriorityCache(exam, section);
    updateUserBehavior(exam, section);
  };
}
```

## Migration Guide

### Step 1: Update Imports

Replace existing imports:
```tsx
// OLD
import { usePaginatedProblems } from '@/features/question-solving/hooks/(pagination)/fetchProblems';

// NEW  
import { usePaginatedProblemsWithPriority as usePaginatedProblems } from '@/features/question-solving/hooks/(pagination)/fetchProblemsWithPriority';
```

### Step 2: Add Provider

```tsx
// In your root layout or app component
import { PriorityCacheProvider } from '@/shared/components/providers/priority-cache-provider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <PriorityCacheProvider>
          {children}
        </PriorityCacheProvider>
      </body>
    </html>
  );
}
```

### Step 3: Update Question Window

```tsx
// Replace existing question window
import QuestionAttemptWithPriority from '@/features/question-solving/components/QuestionWindow/questionwindowWithPriority';

// Use the enhanced version
<QuestionAttemptWithPriority onClose={handleClose} />
```

## Performance Benefits

### Before (Current System)
- All data fetched simultaneously
- Page blocks until all data loaded
- Poor user experience on slow connections
- Unnecessary network requests

### After (Priority System)
- Critical data loads first (immediate UI update)
- Related data loads in background
- Smart prefetching based on user behavior
- Network-aware loading strategies

## Monitoring & Debugging

### 1. Cache Statistics

```tsx
import { usePriorityCacheContext } from '@/shared/components/providers/priority-cache-provider';

function CacheStats() {
  const { cacheStats } = usePriorityCacheContext();
  
  return (
    <div>
      <p>Cache Hit Rate: {cacheStats?.summary?.hitRate}%</p>
      <p>Total Items: {cacheStats?.summary?.totalItems}</p>
    </div>
  );
}
```

### 2. Loading Progress

```tsx
import { PriorityCacheProgress } from '@/shared/components/feedback/PriorityCacheProgress';

function LoadingIndicator() {
  const { loadingState } = usePriorityCacheContext();
  
  return <PriorityCacheProgress loadingState={loadingState} />;
}
```

## Configuration

### Priority Levels

Adjust priority levels in `priority-cache.ts`:

```typescript
export enum CachePriority {
  IMMEDIATE = 1,    // Load immediately
  HIGH = 2,         // Load after immediate
  MEDIUM = 3,       // Background loading
  LOW = 4,          // Idle loading
}
```

### Network Awareness

The system automatically adapts based on:
- Connection speed (`slow-2g`, `2g`, `3g`, `4g`)
- Memory constraints
- Battery level (when available)

### User Behavior Learning

The system learns from:
- Most used exams/sections
- Navigation patterns
- Time-of-day usage
- Session duration

## Best Practices

1. **Use Progress Indicators** - Show users what's loading
2. **Handle Loading States** - Provide feedback during immediate loading
3. **Update User Behavior** - Call `updateUserBehavior()` on navigation
4. **Monitor Performance** - Use cache statistics to optimize
5. **Test on Slow Connections** - Verify priority loading works

## API Reference

### PriorityCacheManager

- `generatePriorityPlan(exam, section, tags)` - Creates priority plan
- `executePriorityPlan(exam, section, tags, onProgress)` - Executes plan
- `getCacheStatsWithPriority()` - Returns cache statistics

### BackgroundCacheService

- `start()` - Starts background service
- `stop()` - Stops background service
- `updateUserBehavior(exam, section)` - Updates usage patterns
- `addPriorityTask(exam, section, priority)` - Adds priority task

### Hooks

- `usePriorityCacheContext()` - Access priority cache context
- `usePaginatedProblemsWithPriority()` - Enhanced problems hook
- `useTagsWithPriority()` - Enhanced tags hook
- `useBackgroundCache()` - Background service hook

## Troubleshooting

### Common Issues

1. **Data Not Loading** - Check network connection and cache configuration
2. **Slow Performance** - Verify priority levels are set correctly
3. **Memory Issues** - Monitor cache size and enable cleanup
4. **Network Errors** - Implement proper error handling and retries

### Debug Mode

Enable debug logging:
```typescript
localStorage.setItem('compex-debug-cache', 'true');
```

This will log cache operations and priority decisions to the console.

## Example Implementation

See the complete implementation in:
- `/features/question-solving/components/QuestionWindow/questionwindowWithPriority.tsx`
- `/features/question-solving/hooks/(pagination)/fetchProblemsWithPriority.tsx`
- `/shared/components/providers/priority-cache-provider.tsx`