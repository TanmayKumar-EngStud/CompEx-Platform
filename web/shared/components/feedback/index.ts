// Main loading components
export { default as LazyLoader } from './LazyLoader';
export { default as DataLoader } from './DataLoader';
export { default as useAsyncState, useAsyncOperations } from './useAsyncState';

// Skeleton loaders
export {
   default as Skeleton,
   TagSectionSkeleton,
   QuestionTableSkeleton,
   CalendarSkeleton,
   ContentSkeleton
} from './SkeletonLoaders';

// Lazy components
export { LazyCalendar } from './lazy/LazyCalendar';
export { LazyTagSection } from './lazy/LazyTagSection';
export { LazyQuestionTable } from './lazy/LazyQuestionTable';
export { LazyQuestionWindow } from './lazy/LazyQuestionWindow';
export { LazyResultWindow } from './lazy/LazyResultWindow';

export {
   withLazyLoading,
   preloadComponent,
   preloadComponents
} from './LazyComponents';

// Type definitions for loading states
export type LoadingState = "idle" | "loading" | "success" | "error";

// Utility functions for loading management
export const createLoadingConfig = (
   minLoadingTime = 300,
   retryAttempts = 3,
   retryDelay = 1000
) => ({
   minLoadingTime,
   retryAttempts,
   retryDelay,
});

export const isLoadingState = (status: string): status is LoadingState => {
   return ["idle", "loading", "success", "error"].includes(status);
};