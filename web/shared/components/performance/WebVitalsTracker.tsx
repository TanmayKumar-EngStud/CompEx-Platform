"use client";
// Force Rebuild

import { useEffect, useState } from 'react';
import { initWebVitals, setupCustomPerformanceObserver } from '@/shared/lib/performance/web-vitals';

/**
 * Props for WebVitalsTracker component
 */
interface WebVitalsTrackerProps {
   /** Enable analytics reporting (default: production only) */
   enableAnalytics?: boolean;
   /** Enable console logging (default: development only) */
   enableConsoleLog?: boolean;
   /** Custom endpoint for sending metrics */
   endpoint?: string;
   /** Sample rate for metric collection (0-1) */
   sampleRate?: number;
   /** Enable custom performance observers */
   enableCustomObservers?: boolean;
}

/**
 * WebVitalsTracker - Client-side component for monitoring Core Web Vitals
 * 
 * This component initializes performance monitoring and should be placed
 * in the root layout or main app component.
 * 
 * @example
 * ```tsx
 * // In layout.tsx or app.tsx
 * <WebVitalsTracker 
 *    enableAnalytics={true}
 *    endpoint="/api/metrics"
 *    sampleRate={0.1}
 * />
 * ```
 */
export function WebVitalsTracker({
   enableAnalytics,
   enableConsoleLog,
   endpoint,
   sampleRate = 1.0,
   enableCustomObservers = true,
}: WebVitalsTrackerProps) {
   useEffect(() => {
      // Initialize Web Vitals monitoring
      initWebVitals({
         enableAnalytics,
         enableConsoleLog,
         endpoint,
         sampleRate,
      });

      // Set up custom performance observers
      if (enableCustomObservers) {
         setupCustomPerformanceObserver();
      }

      // Performance budget warning (development only)
      if (process.env.NODE_ENV === 'development') {
         setTimeout(() => {
            if (typeof window !== 'undefined' && 'performance' in window) {
               const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
               if (navigation) {
                  const pageLoadTime = navigation.loadEventEnd - navigation.requestStart;
                  if (pageLoadTime > 3000) {
                     console.warn(`Page load time (${Math.round(pageLoadTime)}ms) exceeds recommended threshold (3000ms)`);
                  }
               }
            }
         }, 2000);
      }

   }, [enableAnalytics, enableConsoleLog, endpoint, sampleRate, enableCustomObservers]);

   // This component doesn't render anything
   return null;
}

/**
 * Display current Web Vitals metrics (development only)
 * 
 * Shows a floating debug panel with current performance metrics
 */
export function WebVitalsDebugPanel() {
   const [metrics, setMetrics] = useState<Record<string, number>>({});
   const [isVisible, setIsVisible] = useState(false);

   useEffect(() => {
      if (process.env.NODE_ENV !== 'development') {
         return;
      }

      setIsVisible(true);

      // Listen for custom metric events
      const handleMetric = (event: CustomEvent) => {
         setMetrics(prev => ({
            ...prev,
            [event.detail.name]: event.detail.value
         }));
      };

      window.addEventListener('web-vitals-metric' as any, handleMetric);

      return () => {
         window.removeEventListener('web-vitals-metric' as any, handleMetric);
      };
   }, []);

   if (!isVisible || process.env.NODE_ENV !== 'development') {
      return null;
   }

   const getMetricColor = (name: string, value: number) => {
      const thresholds: Record<string, { good: number; poor: number }> = {
         CLS: { good: 0.1, poor: 0.25 },
         FID: { good: 100, poor: 300 },
         FCP: { good: 1800, poor: 3000 },
         LCP: { good: 2500, poor: 4000 },
         TTFB: { good: 800, poor: 1800 },
      };

      const threshold = thresholds[name];
      if (!threshold) return '#4ade80';
      if (value <= threshold.good) return '#4ade80';
      if (value <= threshold.poor) return '#fbbf24';
      return '#f87171';
   };

   return (
      <div
         style={{
            position: 'fixed',
            top: '10px',
            right: '10px',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '10px',
            borderRadius: '5px',
            fontFamily: 'monospace',
            fontSize: '12px',
            zIndex: 9999,
            maxWidth: '200px',
         }}
      >
         <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>Web Vitals</div>
         {Object.entries(metrics).map(([name, value]) => (
            <div key={name} style={{ color: getMetricColor(name, value) }}>
               {name}: {Math.round(value * (name === 'CLS' ? 1000 : 1))}{name === 'CLS' ? '' : 'ms'}
            </div>
         ))}
         <div style={{ marginTop: '5px', fontSize: '10px', opacity: 0.7 }}>Dev Only</div>
      </div>
   );
}