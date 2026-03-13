# Shared Stores

This directory contains Zustand stores that provide global state management across the application.

## Overview

The shared stores contain state that needs to be accessed by multiple features or components throughout the application. These stores follow Zustand patterns for state management.

## Available Stores

### problems/ Directory

Contains stores related to problem/question management:

* **attempts.ts**: Manages user attempts and answer selections
* **cache.ts**: Handles caching of question data for performance
* **index.ts**: Main export file for problem-related stores
* **navigation.ts**: Manages navigation between questions
* **pagination.ts**: Handles pagination state for question lists
* **question-cache.ts**: Specialized caching for individual questions
* **ui-state.ts**: Manages UI state for problem-solving interface

## Store Architecture

### State Management Pattern

All stores follow a consistent pattern:

```typescript
interface StoreState {
  // State properties
  data: SomeDataType;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setData: (data: SomeDataType) => void;
  clearError: () => void;
  reset: () => void;
}

export const useStore = create<StoreState>((set, get) => ({
  // Initial state
  data: null,
  isLoading: false,
  error: null,
  
  // Actions
  setData: (data) => set({ data }),
  clearError: () => set({ error: null }),
  reset: () => set({ data: null, isLoading: false, error: null })
}));
```

### Store Categories

#### Problem Management Stores
- Handle question data, user attempts, and navigation
- Provide caching mechanisms for performance
- Manage pagination and filtering state

#### UI State Stores
- Control global UI elements and modals
- Manage theme and layout preferences
- Handle loading and error states

#### User Session Stores
- Track user authentication state
- Manage user preferences and settings
- Handle session persistence

## Integration Points

### With Features

- **Question Solving**: Primary consumer of problem-related stores
- **User Analytics**: Uses attempt data for performance calculations
- **Exam Management**: Integrates with filtering and navigation stores

### With Components

- **Shared Components**: Access global UI state and theme settings
- **Layout Components**: Use navigation and session stores
- **Form Components**: Integrate with validation and submission stores

## Usage Guidelines

### Importing Stores

```typescript
// Import specific stores
import { useAttemptsStore } from '@/shared/stores/problems/attempts';
import { useNavigationStore } from '@/shared/stores/problems/navigation';

// Import from index for convenience
import { useQuestionStores } from '@/shared/stores/problems';
```

### Store Composition

```typescript
// Example of using multiple stores in a component
function QuestionComponent() {
  const { currentQuestion, setCurrentQuestion } = useNavigationStore();
  const { attempts, recordAttempt } = useAttemptsStore();
  const { cachedQuestions, cacheQuestion } = useQuestionCacheStore();
  
  // Component logic
}
```

### State Persistence

```typescript
// Example of persistent store
const usePersistentStore = create(
  persist(
    (set, get) => ({
      // Store implementation
    }),
    {
      name: 'app-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
```

## Performance Considerations

### Selective Subscriptions

```typescript
// Subscribe to specific parts of the store
const currentQuestion = useNavigationStore(state => state.currentQuestion);
const isLoading = useNavigationStore(state => state.isLoading);

// Avoid subscribing to entire store
const store = useNavigationStore(); // This causes re-renders on any change
```

### Store Splitting

- Keep stores focused on specific domains
- Split large stores into smaller, more focused ones
- Use store composition for complex state management

### Caching Strategy

- Implement intelligent caching for frequently accessed data
- Use time-based cache invalidation
- Provide manual cache clearing mechanisms

## Best Practices

### State Structure

- Keep state flat when possible
- Use normalized data structures for complex relationships
- Separate derived state from base state

### Action Design

- Make actions pure and predictable
- Batch related state updates
- Provide both sync and async action variants

### Error Handling

- Include error states in all stores
- Provide error recovery mechanisms
- Log errors for debugging

### Testing

- Create store test utilities
- Test actions and state transitions
- Mock stores for component testing

## Migration Notes

### Legacy State Management

If migrating from other state management solutions:

- Redux: Map actions to Zustand actions, combine reducers into single store
- Context API: Convert context providers to Zustand stores
- Local State: Identify state that should be global vs. local

### Backward Compatibility

- Maintain existing API contracts during migration
- Provide compatibility layers for gradual migration
- Document breaking changes and migration paths

## Future Enhancements

- Add TypeScript strict mode support
- Implement store devtools integration
- Add automatic state persistence options
- Create store composition utilities
- Add real-time synchronization capabilities
