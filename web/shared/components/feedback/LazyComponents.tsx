"use client";

import { lazy, Suspense } from "react";
import LazyLoader from "./LazyLoader";
import {
   TagSectionSkeleton,
   QuestionTableSkeleton,
   CalendarSkeleton,
   ContentSkeleton
} from "./SkeletonLoaders";

// Lazy components have been moved to shared/components/feedback/lazy/
// to improve compilation performance. Import them directly from there.

// Higher-order component for lazy loading with error boundaries
export const withLazyLoading = <T extends object>(
   componentLoader: () => Promise<{ default: React.ComponentType<T> }>,
   fallback?: React.ReactNode,
   loadingMessage?: string
) => {
   const LazyComponent = (props: T) => (
      <LazyLoader
         loader={componentLoader}
         fallback={fallback}
         loadingMessage={loadingMessage}
         props={props}
         errorBoundary={true}
      />
   );
   LazyComponent.displayName = `LazyComponent`;
   return LazyComponent;
};

// Preload function for critical components
export const preloadComponent = (
   componentLoader: () => Promise<{ default: React.ComponentType<any> }>
) => {
   const component = lazy(componentLoader);
   // Trigger the lazy loading immediately
   componentLoader().catch(console.error);
   return component;
};

// Utility function to batch preload multiple components
export const preloadComponents = (
   loaders: Array<() => Promise<{ default: React.ComponentType<any> }>>
) => {
   return Promise.allSettled(
      loaders.map(loader => loader().catch(console.error))
   );
};

export default LazyLoader;