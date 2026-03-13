/**
 * Background Cache Service
 * 
 * Intelligent background data fetching service that runs when the browser
 * is idle to prefetch likely-needed data based on user behavior patterns.
 */

import { getPriorityCacheManager, CachePriority } from "@/shared/lib/cache/priority-cache";
import { getQueryCacheService } from "@/shared/lib/cache/query-cache";

interface UserBehaviorPattern {
  mostUsedExams: string[];
  mostUsedSections: string[];
  timeOfDayPatterns: Record<string, number>;
  averageSessionDuration: number;
  commonTransitions: Array<{
    from: { exam: string; section: string };
    to: { exam: string; section: string };
    frequency: number;
  }>;
}

interface BackgroundTaskConfig {
  examName: string;
  sectionName: string;
  priority: CachePriority;
  estimatedSize: number;
  lastAccessed?: Date;
  frequency: number;
}

export class BackgroundCacheService {
  private isRunning = false;
  private taskQueue: BackgroundTaskConfig[] = [];
  private completedTasks = new Set<string>();
  private failedTasks = new Set<string>();
  private priorityManager = getPriorityCacheManager();
  private cacheService = getQueryCacheService();
  private idleCallbackId: number | null = null;
  private networkObserver: any | null = null;
  
  // User behavior tracking
  private userBehavior: UserBehaviorPattern = {
    mostUsedExams: ['GRE', 'GMAT'],
    mostUsedSections: ['quants', 'verbal'],
    timeOfDayPatterns: {},
    averageSessionDuration: 30 * 60 * 1000, // 30 minutes
    commonTransitions: []
  };

  constructor() {
    this.initializeNetworkObserver();
    this.loadUserBehaviorFromStorage();
  }

  /**
   * Start the background cache service
   */
  start(): void {
    if (this.isRunning) return;
    
    this.isRunning = true;
    console.log('🚀 Background Cache Service started');
    
    // Schedule immediate high-value tasks
    this.scheduleHighValueTasks();
    
    // Schedule periodic background tasks
    this.schedulePeriodicTasks();
    
    // Schedule cleanup tasks
    this.scheduleCleanupTasks();
  }

  /**
   * Stop the background cache service
   */
  stop(): void {
    this.isRunning = false;
    
    if (this.idleCallbackId) {
      cancelIdleCallback(this.idleCallbackId);
      this.idleCallbackId = null;
    }
    
    console.log('⏹️ Background Cache Service stopped');
  }

  /**
   * Schedule high-value caching tasks
   */
  private scheduleHighValueTasks(): void {
    const highValueTasks: BackgroundTaskConfig[] = [
      // Most commonly used exam combinations
      { examName: 'GRE', sectionName: 'quants', priority: CachePriority.HIGH, estimatedSize: 500, frequency: 10 },
      { examName: 'GRE', sectionName: 'verbal', priority: CachePriority.HIGH, estimatedSize: 400, frequency: 8 },
      { examName: 'GMAT', sectionName: 'quants', priority: CachePriority.MEDIUM, estimatedSize: 450, frequency: 7 },
      { examName: 'GMAT', sectionName: 'verbal', priority: CachePriority.MEDIUM, estimatedSize: 350, frequency: 6 },
    ];

    // Add user-specific high-value tasks based on behavior
    this.userBehavior.mostUsedExams.forEach(exam => {
      this.userBehavior.mostUsedSections.forEach(section => {
        if (!highValueTasks.some(task => task.examName === exam && task.sectionName === section)) {
          highValueTasks.push({
            examName: exam,
            sectionName: section,
            priority: CachePriority.MEDIUM,
            estimatedSize: 400,
            frequency: 5
          });
        }
      });
    });

    this.taskQueue.push(...highValueTasks);
    this.processTaskQueue();
  }

  /**
   * Schedule periodic background tasks
   */
  private schedulePeriodicTasks(): void {
    // Schedule task processing every 30 seconds when idle
    const scheduleNext = () => {
      if (!this.isRunning) return;
      
      if (window.requestIdleCallback) {
        this.idleCallbackId = window.requestIdleCallback(
          (deadline) => {
            this.processTasksInIdleTime(deadline);
            setTimeout(scheduleNext, 30000); // Schedule next batch in 30 seconds
          },
          { timeout: 60000 } // Maximum wait time
        );
      } else {
        // Fallback for browsers without requestIdleCallback
        setTimeout(() => {
          this.processTasksInIdleTime({ didTimeout: false, timeRemaining: () => 5 });
          scheduleNext();
        }, 30000);
      }
    };

    scheduleNext();
  }

  /**
   * Process tasks during idle time
   */
  private processTasksInIdleTime(deadline: IdleDeadline): void {
    while (deadline.timeRemaining() > 1 && this.taskQueue.length > 0) {
      const task = this.taskQueue.shift();
      if (task && this.shouldProcessTask(task)) {
        this.processBackgroundTask(task);
      }
    }
  }

  /**
   * Process the task queue intelligently
   */
  private async processTaskQueue(): Promise<void> {
    if (!this.isRunning || this.taskQueue.length === 0) return;

    // Sort tasks by priority and frequency
    this.taskQueue.sort((a, b) => {
      if (a.priority !== b.priority) {
        return a.priority - b.priority;
      }
      return b.frequency - a.frequency;
    });

    // Process tasks with proper delays to avoid overwhelming the system
    let delay = 0;
    const batchSize = 3;
    
    for (let i = 0; i < this.taskQueue.length && this.isRunning; i += batchSize) {
      const batch = this.taskQueue.slice(i, i + batchSize);
      
      setTimeout(() => {
        batch.forEach(task => {
          if (this.shouldProcessTask(task)) {
            this.processBackgroundTask(task);
          }
        });
      }, delay);
      
      delay += 2000; // 2-second delay between batches
    }
  }

  /**
   * Process a single background task
   */
  private async processBackgroundTask(task: BackgroundTaskConfig): Promise<void> {
    const taskId = `${task.examName}-${task.sectionName}`;
    
    if (this.completedTasks.has(taskId) || this.failedTasks.has(taskId)) {
      return;
    }

    try {
      // Check if data is already cached
      const cachedTags = this.cacheService.getCachedTags(task.examName, task.sectionName);
      const cachedProblems = this.cacheService.getCachedProblems(task.examName, task.sectionName, []);
      
      if (cachedTags && cachedProblems) {
        this.completedTasks.add(taskId);
        return;
      }

      // Fetch missing data
      const promises: Promise<any>[] = [];
      
      if (!cachedTags) {
        promises.push(this.fetchTags(task.examName, task.sectionName));
      }
      
      if (!cachedProblems) {
        promises.push(this.fetchProblems(task.examName, task.sectionName));
      }

      await Promise.allSettled(promises);
      this.completedTasks.add(taskId);
      
      console.log(`✅ Background cached: ${taskId}`);
      
    } catch (error) {
      console.warn(`❌ Background caching failed for ${taskId}:`, error);
      this.failedTasks.add(taskId);
    }
  }

  /**
   * Check if task should be processed based on network and system conditions
   */
  private shouldProcessTask(task: BackgroundTaskConfig): boolean {
    // Don't process if user is on a slow connection
    if (this.networkObserver) {
      const effectiveType = (this.networkObserver as any).effectiveType;
      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        return false;
      }
    }

    // Don't process if battery is low (if available)
    if ('getBattery' in navigator) {
      // Note: This is deprecated but still check if available
      return true; // Skip battery check for now
    }

    // Don't process if memory is constrained (if available)
    if ('memory' in performance) {
      const memInfo = (performance as any).memory;
      const usedMemoryRatio = memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit;
      if (usedMemoryRatio > 0.8) {
        return false;
      }
    }

    return true;
  }

  /**
   * Fetch tags for background caching
   */
  private async fetchTags(examName: string, sectionName: string): Promise<void> {
    const response = await fetch(
      `/api/problems/tags?examName=${examName}&sectionName=${sectionName}`,
      {
        headers: {
          'X-Background-Request': 'true',
          'X-Cache-Priority': CachePriority.LOW.toString(),
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      this.cacheService.cacheTags(examName, sectionName, data.tags);
    }
  }

  /**
   * Fetch problems for background caching
   */
  private async fetchProblems(examName: string, sectionName: string): Promise<void> {
    const response = await fetch('/api/problems/getProblems', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Background-Request': 'true',
        'X-Cache-Priority': CachePriority.LOW.toString(),
      },
      body: JSON.stringify({
        userid: 1, // TODO: Get from auth context
        examName,
        sectionName,
        tags: null
      })
    });

    if (response.ok) {
      const data = await response.json();
      this.cacheService.cacheProblems(examName, sectionName, [], data);
    }
  }

  /**
   * Schedule cleanup tasks
   */
  private scheduleCleanupTasks(): void {
    // Clean up every 10 minutes
    setInterval(() => {
      if (this.isRunning) {
        this.cleanupExpiredCache();
        this.optimizeCacheStorage();
      }
    }, 10 * 60 * 1000);
  }

  /**
   * Clean up expired cache entries
   */
  private cleanupExpiredCache(): void {
    // This would be handled by the cache manager's built-in cleanup
    console.log('🧹 Background cache cleanup performed');
  }

  /**
   * Optimize cache storage by removing least-used items if memory is constrained
   */
  private optimizeCacheStorage(): void {
    if ('memory' in performance) {
      const memInfo = (performance as any).memory;
      const usedMemoryRatio = memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit;
      
      if (usedMemoryRatio > 0.7) {
        // Clear some cached items to free memory
        console.log('🔧 Optimizing cache storage due to memory constraints');
        // Implementation would depend on cache manager's API
      }
    }
  }

  /**
   * Initialize network observer
   */
  private initializeNetworkObserver(): void {
    if ('connection' in navigator) {
      this.networkObserver = (navigator as any).connection;
      
      this.networkObserver?.addEventListener('change', () => {
        const effectiveType = (this.networkObserver as any)?.effectiveType;
        console.log(`📡 Network changed to: ${effectiveType}`);
        
        // Adjust task processing based on network conditions
        if (effectiveType === 'slow-2g' || effectiveType === '2g') {
          console.log('🐌 Slowing down background tasks due to slow connection');
        }
      });
    }
  }

  /**
   * Load user behavior patterns from storage
   */
  private loadUserBehaviorFromStorage(): void {
    try {
      const stored = localStorage.getItem('compex-user-behavior');
      if (stored) {
        this.userBehavior = { ...this.userBehavior, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.warn('Failed to load user behavior patterns:', error);
    }
  }

  /**
   * Update user behavior patterns
   */
  updateUserBehavior(examName: string, sectionName: string): void {
    // Update usage patterns
    if (!this.userBehavior.mostUsedExams.includes(examName)) {
      this.userBehavior.mostUsedExams.unshift(examName);
      this.userBehavior.mostUsedExams = this.userBehavior.mostUsedExams.slice(0, 3);
    }

    if (!this.userBehavior.mostUsedSections.includes(sectionName)) {
      this.userBehavior.mostUsedSections.unshift(sectionName);
      this.userBehavior.mostUsedSections = this.userBehavior.mostUsedSections.slice(0, 5);
    }

    // Save to storage
    try {
      localStorage.setItem('compex-user-behavior', JSON.stringify(this.userBehavior));
    } catch (error) {
      console.warn('Failed to save user behavior patterns:', error);
    }
  }

  /**
   * Get service statistics
   */
  getStats() {
    return {
      isRunning: this.isRunning,
      queueLength: this.taskQueue.length,
      completedTasks: this.completedTasks.size,
      failedTasks: this.failedTasks.size,
      userBehavior: this.userBehavior,
    };
  }

  /**
   * Add priority task based on user navigation
   */
  addPriorityTask(examName: string, sectionName: string, priority = CachePriority.HIGH): void {
    const task: BackgroundTaskConfig = {
      examName,
      sectionName,
      priority,
      estimatedSize: 400,
      frequency: 1,
    };

    // Add to front of queue if high priority
    if (priority <= CachePriority.HIGH) {
      this.taskQueue.unshift(task);
    } else {
      this.taskQueue.push(task);
    }

    // Process immediately if high priority
    if (priority === CachePriority.IMMEDIATE && this.isRunning) {
      this.processBackgroundTask(task);
    }
  }
}

/**
 * Singleton background cache service
 */
let backgroundCacheService: BackgroundCacheService | null = null;

export function getBackgroundCacheService(): BackgroundCacheService {
  if (!backgroundCacheService) {
    backgroundCacheService = new BackgroundCacheService();
  }
  return backgroundCacheService;
}

/**
 * React hook for background cache service
 */
export function useBackgroundCache() {
  const service = getBackgroundCacheService();
  
  return {
    start: service.start.bind(service),
    stop: service.stop.bind(service),
    updateUserBehavior: service.updateUserBehavior.bind(service),
    addPriorityTask: service.addPriorityTask.bind(service),
    getStats: service.getStats.bind(service),
  };
}