"use client";

import { lazy, Suspense } from 'react';
import { Skeleton } from './skeleton';

/**
 * Pre-configured dynamic imports for common heavy components
 * These will be loaded only when needed, reducing initial bundle size
 */

// Chart components (recharts is heavy - ~200KB)
export const DynamicBarChart = lazy(() => 
  import('recharts').then(mod => ({ default: mod.BarChart }))
);

export const DynamicLineChart = lazy(() => 
  import('recharts').then(mod => ({ default: mod.LineChart }))
);

export const DynamicPieChart = lazy(() => 
  import('recharts').then(mod => ({ default: mod.PieChart }))
);

// KaTeX for math rendering (heavy - ~150KB)
export const DynamicInlineMath = lazy(() => 
  import('react-katex').then(mod => ({ default: mod.InlineMath }))
);

export const DynamicBlockMath = lazy(() => 
  import('react-katex').then(mod => ({ default: mod.BlockMath }))
);

// Wrapper components with loading states
export function DynamicChart({ 
  children, 
  fallback 
}: { 
  children: React.ReactNode; 
  fallback?: React.ReactNode;
}) {
  return (
    <Suspense fallback={fallback || <Skeleton className="w-full h-64" />}>
      {children}
    </Suspense>
  );
}

export function DynamicMath({ 
  children, 
  fallback 
}: { 
  children: React.ReactNode; 
  fallback?: React.ReactNode;
}) {
  return (
    <Suspense fallback={fallback || <span>Loading math...</span>}>
      {children}
    </Suspense>
  );
}