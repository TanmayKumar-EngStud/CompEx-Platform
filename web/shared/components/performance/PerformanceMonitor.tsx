"use client";

import { useState, useEffect } from 'react';
import { formatCacheSize, getServiceWorkerManager } from '@/shared/lib/cache/service-worker';
import { getCacheManager } from '@/shared/lib/cache/cache-manager';
import { getQueryCacheService } from '@/shared/lib/cache/query-cache';

/**
 * Performance monitoring dashboard component
 * 
 * Displays real-time performance metrics and alerts for development.
 * Only shows in development mode by default.
 */
export function PerformanceMonitor() {
   const [isOpen, setIsOpen] = useState(false);
   const [metrics, setMetrics] = useState<any>(null);
   const [alerts, setAlerts] = useState<string[]>([]);

   // Only show in development mode
   const isDev = process.env.NODE_ENV === 'development';

   useEffect(() => {
      if (!isDev) return;

      const updateMetrics = () => {
         const cacheManager = getCacheManager();
         const queryCacheService = getQueryCacheService();
         
         const cacheStats = queryCacheService.getCacheStats();
         const summary = cacheManager.getStatsSummary();

         setMetrics({
            cacheStats,
            summary,
            performance: {
               memory: (performance as any).memory ? {
                  used: (performance as any).memory.usedJSHeapSize,
                  total: (performance as any).memory.totalJSHeapSize,
                  limit: (performance as any).memory.jsHeapSizeLimit,
               } : null,
            },
         });

         // Check for performance alerts
         const newAlerts: string[] = [];
         
         if (summary.averageHitRate < 0.5) {
            newAlerts.push(`Low cache hit rate: ${(summary.averageHitRate * 100).toFixed(1)}%`);
         }
         
         if (summary.totalSize > 50 * 1024 * 1024) { // 50MB
            newAlerts.push(`High cache usage: ${formatCacheSize(summary.totalSize)}`);
         }

         if ((performance as any).memory) {
            const memoryUsage = (performance as any).memory.usedJSHeapSize / (performance as any).memory.jsHeapSizeLimit;
            if (memoryUsage > 0.8) {
               newAlerts.push(`High memory usage: ${(memoryUsage * 100).toFixed(1)}%`);
            }
         }

         setAlerts(newAlerts);
      };

      // Update metrics every 5 seconds
      const interval = setInterval(updateMetrics, 5000);
      updateMetrics(); // Initial update

      return () => clearInterval(interval);
   }, [isDev]);

   // Don't render in production
   if (!isDev) return null;

   return (
      <div className="fixed bottom-4 right-4 z-50">
         {/* Toggle Button */}
         <button
            onClick={() => setIsOpen(!isOpen)}
            className={`
               px-3 py-2 rounded-full text-xs font-medium transition-all duration-200
               ${alerts.length > 0 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-blue-500 text-white hover:bg-blue-600'
               }
            `}
            title="Performance Monitor"
         >
            📊 {alerts.length > 0 && <span className="ml-1">⚠️</span>}
         </button>

         {/* Performance Panel */}
         {isOpen && (
            <div className="absolute bottom-12 right-0 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 max-h-96 overflow-y-auto">
               <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm">Performance Monitor</h3>
                  <button
                     onClick={() => setIsOpen(false)}
                     className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                     ✕
                  </button>
               </div>

               {/* Alerts */}
               {alerts.length > 0 && (
                  <div className="mb-4">
                     <h4 className="text-xs font-medium text-red-600 dark:text-red-400 mb-2">
                        🚨 Alerts ({alerts.length})
                     </h4>
                     <div className="space-y-1">
                        {alerts.map((alert, index) => (
                           <div
                              key={index}
                              className="text-xs bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-2 rounded"
                           >
                              {alert}
                           </div>
                        ))}
                     </div>
                  </div>
               )}

               {/* Cache Metrics */}
               {metrics && (
                  <div className="space-y-3">
                     <div>
                        <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                           Cache Summary
                        </h4>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                           <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                              <div className="text-gray-500 dark:text-gray-400">Total Caches</div>
                              <div className="font-medium">{metrics.summary.totalCaches}</div>
                           </div>
                           <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                              <div className="text-gray-500 dark:text-gray-400">Total Items</div>
                              <div className="font-medium">{metrics.summary.totalItems}</div>
                           </div>
                           <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                              <div className="text-gray-500 dark:text-gray-400">Cache Size</div>
                              <div className="font-medium">{formatCacheSize(metrics.summary.totalSize)}</div>
                           </div>
                           <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                              <div className="text-gray-500 dark:text-gray-400">Hit Rate</div>
                              <div className="font-medium">
                                 {(metrics.summary.averageHitRate * 100).toFixed(1)}%
                              </div>
                           </div>
                        </div>
                     </div>

                     {/* Memory Usage */}
                     {metrics.performance.memory && (
                        <div>
                           <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Memory Usage
                           </h4>
                           <div className="space-y-2">
                              <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                                 <div className="text-gray-500 dark:text-gray-400 text-xs">JS Heap</div>
                                 <div className="font-medium text-xs">
                                    {formatCacheSize(metrics.performance.memory.used)} / {formatCacheSize(metrics.performance.memory.limit)}
                                 </div>
                                 <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1.5 mt-1">
                                    <div
                                       className="bg-blue-500 h-1.5 rounded-full"
                                       style={{
                                          width: `${(metrics.performance.memory.used / metrics.performance.memory.limit) * 100}%`
                                       }}
                                    />
                                 </div>
                              </div>
                           </div>
                        </div>
                     )}

                     {/* Individual Cache Stats */}
                     <div>
                        <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                           Cache Details
                        </h4>
                        <div className="space-y-2">
                           {Object.entries(metrics.cacheStats).map(([name, stats]: [string, any]) => (
                              <div key={name} className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                                 <div className="flex justify-between items-center">
                                    <span className="text-xs font-medium capitalize">{name}</span>
                                    <span className="text-xs text-gray-500 dark:text-gray-400">
                                       {stats.hitRate ? `${(stats.hitRate * 100).toFixed(1)}%` : 'N/A'}
                                    </span>
                                 </div>
                                 <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    {stats.itemCount || 0} items • {formatCacheSize(stats.totalSize || 0)}
                                 </div>
                              </div>
                           ))}
                        </div>
                     </div>

                     {/* Actions */}
                     <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
                        <div className="flex gap-2">
                           <button
                              onClick={() => {
                                 getCacheManager().clearAll();
                                 console.log('🗑️ All caches cleared');
                              }}
                              className="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-2 py-1 rounded"
                           >
                              Clear Caches
                           </button>
                           <button
                              onClick={() => {
                                 if (typeof window !== 'undefined' && 'gc' in window) {
                                    (window as any).gc();
                                    console.log('🗑️ Garbage collection triggered');
                                 }
                              }}
                              className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded"
                           >
                              Force GC
                           </button>
                        </div>
                     </div>
                  </div>
               )}
            </div>
         )}
      </div>
   );
}

/**
 * Performance budget checker component
 */
export function PerformanceBudgetChecker() {
   const [budgetViolations, setBudgetViolations] = useState<string[]>([]);
   const isDev = process.env.NODE_ENV === 'development';

   useEffect(() => {
      if (!isDev) return;

      const checkBudgets = () => {
         const violations: string[] = [];

         // Check bundle size budget
         if (typeof window !== 'undefined' && 'performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
            if (navigation) {
               const loadTime = navigation.loadEventEnd - navigation.requestStart;
               if (loadTime > 3000) {
                  violations.push(`Page load time (${Math.round(loadTime)}ms) exceeds 3s budget`);
               }
            }

            // Check resource sizes
            const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
            resources.forEach(resource => {
               if (resource.transferSize > 500 * 1024) { // 500KB
                  violations.push(`Large resource: ${resource.name.split('/').pop()} (${formatCacheSize(resource.transferSize)})`);
               }
            });
         }

         setBudgetViolations(violations);
      };

      // Check budgets after page load
      const timeout = setTimeout(checkBudgets, 2000);
      return () => clearTimeout(timeout);
   }, [isDev]);

   if (!isDev || budgetViolations.length === 0) return null;

   return (
      <div className="fixed bottom-20 right-4 z-40 max-w-sm">
         <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 shadow-lg">
            <h4 className="text-sm font-medium text-yellow-800 mb-2">
               ⚠️ Budget Violations
            </h4>
            <div className="space-y-1">
               {budgetViolations.map((violation, index) => (
                  <div key={index} className="text-xs text-yellow-700">
                     • {violation}
                  </div>
               ))}
            </div>
         </div>
      </div>
   );
}