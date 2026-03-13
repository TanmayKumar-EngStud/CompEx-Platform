/**
 * Core Web Vitals monitoring utility
 * 
 * Tracks and reports key performance metrics for better user experience monitoring
 * and performance optimization insights.
 */

export interface WebVitalsMetric {
   name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB' | 'INP';
   value: number;
   id: string;
   navigationType?: string;
}

export interface PerformanceConfig {
   enableAnalytics: boolean;
   enableConsoleLog: boolean;
   endpoint?: string;
   sampleRate?: number;
}

/**
 * Default configuration for performance monitoring
 */
const defaultConfig: PerformanceConfig = {
   enableAnalytics: process.env.NODE_ENV === 'production',
   enableConsoleLog: process.env.NODE_ENV === 'development',
   sampleRate: 1.0, // 100% sampling by default
};

/**
 * Send metric data to analytics service
 */
function sendToAnalytics(metric: WebVitalsMetric, config: PerformanceConfig) {
   // Sample rate filtering
   if (Math.random() > (config.sampleRate || 1.0)) {
      return;
   }

   if (config.enableConsoleLog) {
      console.log('Web Vitals Metric:', {
         name: metric.name,
         value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
         id: metric.id,
         rating: getMetricRating(metric.name, metric.value),
      });
   }

   if (config.enableAnalytics) {
      // Send to external analytics service
      if (typeof window !== 'undefined' && 'gtag' in window) {
         (window as any).gtag('event', metric.name, {
            value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
            event_label: metric.id,
            non_interaction: true,
         });
      }

      // Send to custom endpoint if configured
      if (config.endpoint) {
         fetch(config.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
               metric: metric.name,
               value: metric.value,
               id: metric.id,
               url: window.location.href,
               timestamp: Date.now(),
            }),
         }).catch(error => console.warn('Failed to send metric to endpoint:', error));
      }
   }
}

/**
 * Get performance rating based on metric thresholds
 * 
 * @param name - Metric name
 * @param value - Metric value
 * @returns Rating: 'good', 'needs-improvement', or 'poor'
 */
function getMetricRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
   const thresholds = {
      CLS: { good: 0.1, poor: 0.25 },
      FID: { good: 100, poor: 300 },
      FCP: { good: 1800, poor: 3000 },
      LCP: { good: 2500, poor: 4000 },
      TTFB: { good: 800, poor: 1800 },
      INP: { good: 200, poor: 500 },
   };

   const threshold = thresholds[name as keyof typeof thresholds];
   if (!threshold) return 'good';

   if (value <= threshold.good) return 'good';
   if (value <= threshold.poor) return 'needs-improvement';
   return 'poor';
}

/**
 * Initialize Web Vitals monitoring
 * 
 * @param config - Configuration options for monitoring
 */
export async function initWebVitals(config: Partial<PerformanceConfig> = {}) {
   const finalConfig = { ...defaultConfig, ...config };

   try {
      // Dynamic import to reduce bundle size
      const webVitals = await import('web-vitals');

      // Set up metric collection with available metrics
      if ('onCLS' in webVitals) {
         webVitals.onCLS((metric: any) => sendToAnalytics(metric, finalConfig));
      }
      if ('onFCP' in webVitals) {
         webVitals.onFCP((metric: any) => sendToAnalytics(metric, finalConfig));
      }
      if ('onLCP' in webVitals) {
         webVitals.onLCP((metric: any) => sendToAnalytics(metric, finalConfig));
      }
      if ('onTTFB' in webVitals) {
         webVitals.onTTFB((metric: any) => sendToAnalytics(metric, finalConfig));
      }

      // Try to get FID/INP (may not be available in all versions)
      try {
         if ('onFID' in webVitals && typeof (webVitals as any).onFID === 'function') {
            (webVitals as any).onFID((metric: any) => sendToAnalytics(metric, finalConfig));
         }
         if ('onINP' in webVitals && typeof (webVitals as any).onINP === 'function') {
            (webVitals as any).onINP((metric: any) => sendToAnalytics(metric, finalConfig));
         }
      } catch {
         // Some metrics not available in this version
         console.info('Some Web Vitals metrics not available in current version');
      }

      if (finalConfig.enableConsoleLog) {
         console.log('Web Vitals monitoring initialized');
      }
   } catch (error) {
      console.warn('Failed to initialize Web Vitals monitoring:', error);
   }
}

/**
 * Custom performance observer for additional metrics
 */
export function setupCustomPerformanceObserver() {
   if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
      return;
   }

   try {
      // Monitor long tasks
      const longTaskObserver = new PerformanceObserver((list) => {
         for (const entry of list.getEntries()) {
            if (entry.duration > 50) { // Tasks longer than 50ms
               console.warn('Long Task detected:', {
                  duration: entry.duration,
                  startTime: entry.startTime,
               });
            }
         }
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });

      // Monitor layout shifts
      const layoutShiftObserver = new PerformanceObserver((list) => {
         let cumulativeScore = 0;
         for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
               cumulativeScore += (entry as any).value;
            }
         }
         if (cumulativeScore > 0.1) {
            console.warn('Cumulative Layout Shift above threshold:', cumulativeScore);
         }
      });
      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });

   } catch (error) {
      console.warn('Failed to setup custom performance observer:', error);
   }
}

/**
 * Performance budget checker
 */
export interface PerformanceBudget {
   maxBundleSize: number; // KB
   maxLCP: number; // ms
   maxFID: number; // ms
   maxCLS: number; // score
}

export const defaultBudget: PerformanceBudget = {
   maxBundleSize: 500, // 500 KB
   maxLCP: 2500, // 2.5 seconds
   maxFID: 100, // 100 ms
   maxCLS: 0.1, // 0.1 score
};

/**
 * Check if current metrics are within performance budget
 */
export function checkPerformanceBudget(
   metrics: Record<string, number>,
   budget: PerformanceBudget = defaultBudget
): { passed: boolean; violations: string[] } {
   const violations: string[] = [];

   if (metrics.LCP > budget.maxLCP) {
      violations.push(`LCP (${metrics.LCP}ms) exceeds budget (${budget.maxLCP}ms)`);
   }
   if (metrics.FID > budget.maxFID) {
      violations.push(`FID (${metrics.FID}ms) exceeds budget (${budget.maxFID}ms)`);
   }
   if (metrics.CLS > budget.maxCLS) {
      violations.push(`CLS (${metrics.CLS}) exceeds budget (${budget.maxCLS})`);
   }

   return {
      passed: violations.length === 0,
      violations,
   };
}