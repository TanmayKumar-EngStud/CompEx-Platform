/**
 * Priority-based caching system for CompEx
 * 
 * Implements intelligent data fetching prioritization based on user context:
 * 1. Current exam/section (highest priority)
 * 2. Related exam sections (medium priority) 
 * 3. Other exam types (lowest priority)
 */

import { getQueryCacheService, CACHE_KEYS, QUERY_CONFIGS } from "./query-cache";
import { getCacheManager, CACHE_CONFIGS } from "./cache-manager";

export enum CachePriority {
  IMMEDIATE = 1,    // Current exam/section - load immediately
  HIGH = 2,         // Related sections - load after immediate
  MEDIUM = 3,       // Related exam types - background loading
  LOW = 4,          // Other data - load when idle
}

interface PriorityTaskConfig {
  priority: CachePriority;
  examName: string;
  sectionName: string;
  dataType: 'problems' | 'tags' | 'questions';
  topics?: string[];
  themes?: string[];
  types?: string[];
  tags?: string[]; // Combined fallback
  metadata?: any;
}

interface PriorityFetchResult {
  success: boolean;
  data?: any;
  error?: Error;
  cached: boolean;
  priority: CachePriority;
  timing: number;
}

export class PriorityCacheManager {
  private cacheService = getQueryCacheService();
  private cacheManager = getCacheManager();
  private pendingTasks = new Map<string, PriorityTaskConfig>();
  private activeFetches = new Set<string>();
  private completedTasks = new Set<string>();

  // Priority queues for different priority levels
  private priorityQueues = {
    [CachePriority.IMMEDIATE]: [] as PriorityTaskConfig[],
    [CachePriority.HIGH]: [] as PriorityTaskConfig[],
    [CachePriority.MEDIUM]: [] as PriorityTaskConfig[],
    [CachePriority.LOW]: [] as PriorityTaskConfig[],
  };

  private isProcessing = false;
  private onDataLoadedCallbacks = new Map<string, (data: any) => void>();

  /**
   * Generate priority plan based on current context
   */
  generatePriorityPlan(
    currentExam: string,
    currentSection: string,
    filters: { topics?: string[], themes?: string[], types?: string[] } = {}
  ): PriorityTaskConfig[] {
    const { topics = [], themes = [], types = [] } = filters;
    const selectedTags = [...topics, ...themes, ...types];
    const tasks: PriorityTaskConfig[] = [];
    const taskId = (exam: string, section: string, type: string) => `${exam}-${section}-${type}`;

    // 1. IMMEDIATE: Current exam/section data
    tasks.push({
      priority: CachePriority.IMMEDIATE,
      examName: currentExam,
      sectionName: currentSection,
      dataType: 'tags',
      metadata: { taskId: taskId(currentExam, currentSection, 'tags') }
    });

    tasks.push({
      priority: CachePriority.IMMEDIATE,
      examName: currentExam,
      sectionName: currentSection,
      dataType: 'problems',
      tags: selectedTags,
      metadata: { taskId: taskId(currentExam, currentSection, 'problems') }
    });

    // 2. HIGH: Related sections within same exam
    const examSections = this.getRelatedSections(currentExam, currentSection);
    examSections.forEach(section => {
      tasks.push({
        priority: CachePriority.HIGH,
        examName: currentExam,
        sectionName: section,
        dataType: 'tags',
        metadata: { taskId: taskId(currentExam, section, 'tags') }
      });

      tasks.push({
        priority: CachePriority.HIGH,
        examName: currentExam,
        sectionName: section,
        dataType: 'problems',
        tags: [], // No tags filter for background loading
        metadata: { taskId: taskId(currentExam, section, 'problems') }
      });
    });

    // 3. MEDIUM: Other exam types
    const otherExams = this.getOtherExams(currentExam);
    otherExams.forEach(exam => {
      ['quants', 'verbal'].forEach(section => {
        tasks.push({
          priority: CachePriority.MEDIUM,
          examName: exam,
          sectionName: section,
          dataType: 'tags',
          metadata: { taskId: taskId(exam, section, 'tags') }
        });

        tasks.push({
          priority: CachePriority.MEDIUM,
          examName: exam,
          sectionName: section,
          dataType: 'problems',
          tags: [],
          metadata: { taskId: taskId(exam, section, 'problems') }
        });
      });
    });

    return tasks;
  }

  /**
   * Execute prioritized caching plan
   */
  async executePriorityPlan(
    currentExam: string,
    currentSection: string,
    filters: { topics?: string[], themes?: string[], types?: string[] } = {},
    onProgress?: (progress: { completed: number; total: number; currentTask: string }) => void
  ): Promise<Map<string, PriorityFetchResult>> {
    const tasks = this.generatePriorityPlan(currentExam, currentSection, filters);
    const results = new Map<string, PriorityFetchResult>();

    // Clear previous state
    this.clearPendingTasks();

    // Organize tasks by priority
    tasks.forEach(task => {
      const taskId = task.metadata?.taskId || this.generateTaskId(task);
      this.pendingTasks.set(taskId, task);
      this.priorityQueues[task.priority].push(task);
    });

    this.isProcessing = true;
    let completed = 0;
    const total = tasks.length;

    try {
      // Process IMMEDIATE priority first (blocking)
      console.log('🚀 Starting immediate priority cache loading...');
      for (const task of this.priorityQueues[CachePriority.IMMEDIATE]) {
        const taskId = task.metadata?.taskId || this.generateTaskId(task);
        const result = await this.executeTask(task);
        results.set(taskId, result);
        completed++;

        onProgress?.({ completed, total, currentTask: `${task.examName} ${task.sectionName} ${task.dataType}` });

        // Notify UI immediately for critical data
        if (this.onDataLoadedCallbacks.has(taskId)) {
          this.onDataLoadedCallbacks.get(taskId)?.(result.data);
        }
      }

      // Process HIGH priority (semi-blocking with small delay)
      console.log('⚡ Starting high priority cache loading...');
      const highPriorityPromises = this.priorityQueues[CachePriority.HIGH].map(
        async (task, index) => {
          // Stagger requests to avoid overwhelming the server
          await this.delay(index * 100);
          const taskId = task.metadata?.taskId || this.generateTaskId(task);
          const result = await this.executeTask(task);
          results.set(taskId, result);
          completed++;

          onProgress?.({ completed, total, currentTask: `${task.examName} ${task.sectionName} ${task.dataType}` });
          return result;
        }
      );

      await Promise.allSettled(highPriorityPromises);

      // Process MEDIUM and LOW priority in background (non-blocking)
      console.log('🔄 Starting background cache loading...');
      const backgroundTasks = [
        ...this.priorityQueues[CachePriority.MEDIUM],
        ...this.priorityQueues[CachePriority.LOW]
      ];

      // Execute background tasks without blocking UI
      this.executeBackgroundTasks(backgroundTasks, results, (taskCompleted) => {
        completed++;
        onProgress?.({ completed, total, currentTask: taskCompleted });
      });

    } finally {
      this.isProcessing = false;
    }

    return results;
  }

  /**
   * Execute a single cache task
   */
  private async executeTask(task: PriorityTaskConfig): Promise<PriorityFetchResult> {
    const startTime = Date.now();
    const taskId = task.metadata?.taskId || this.generateTaskId(task);

    try {
      this.activeFetches.add(taskId);

      // Check cache first
      const cached = this.getCachedData(task);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          priority: task.priority,
          timing: Date.now() - startTime
        };
      }

      // Fetch from API
      const data = await this.fetchData(task);

      // Cache the result
      this.cacheData(task, data);

      return {
        success: true,
        data,
        cached: false,
        priority: task.priority,
        timing: Date.now() - startTime
      };

    } catch (error) {
      console.warn(`Cache task failed for ${taskId}:`, error);
      return {
        success: false,
        error: error as Error,
        cached: false,
        priority: task.priority,
        timing: Date.now() - startTime
      };
    } finally {
      this.activeFetches.delete(taskId);
      this.completedTasks.add(taskId);
    }
  }

  /**
   * Execute background tasks with intelligent scheduling
   */
  private executeBackgroundTasks(
    tasks: PriorityTaskConfig[],
    results: Map<string, PriorityFetchResult>,
    onProgress: (taskName: string) => void
  ) {
    // Use requestIdleCallback for better performance
    const scheduleTask = (taskIndex: number) => {
      if (taskIndex >= tasks.length) return;

      const scheduleNext = () => {
        if (window.requestIdleCallback) {
          window.requestIdleCallback(() => scheduleTask(taskIndex + 1), { timeout: 5000 });
        } else {
          // Fallback for browsers without requestIdleCallback
          setTimeout(() => scheduleTask(taskIndex + 1), 100);
        }
      };

      const task = tasks[taskIndex];
      const taskId = task.metadata?.taskId || this.generateTaskId(task);

      this.executeTask(task)
        .then(result => {
          results.set(taskId, result);
          onProgress(`${task.examName} ${task.sectionName} ${task.dataType}`);
        })
        .catch(error => {
          console.warn(`Background task failed for ${taskId}:`, error);
        })
        .finally(() => {
          scheduleNext();
        });
    };

    // Start the first background task
    scheduleTask(0);
  }

  /**
   * Get cached data for a task
   */
  private getCachedData(task: PriorityTaskConfig): any | null {
    switch (task.dataType) {
      case 'tags':
        return this.cacheService.getCachedTags(task.examName, task.sectionName);
      case 'problems':
        return this.cacheService.getCachedProblems(task.examName, task.sectionName, task.tags || []);
      default:
        return null;
    }
  }

  /**
   * Fetch data from API
   */
  private async fetchData(task: PriorityTaskConfig): Promise<any> {
    switch (task.dataType) {
      case 'tags':
        const tagsResponse = await fetch(
          `/api/problems/tags?examName=${task.examName}&sectionName=${task.sectionName}`
        );
        if (!tagsResponse.ok) throw new Error(`Failed to fetch tags: ${tagsResponse.status}`);
        const tagsData = await tagsResponse.json();
        return tagsData.tags;

      case 'problems':
        const problemsResponse = await fetch('/api/problems/getProblems', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userid: 1, // TODO: Get from auth context
            examName: task.examName,
            sectionName: task.sectionName,
            topics: task.topics || [],
            themes: task.themes || [],
            types: task.types || [],
            tags: task.tags?.length ? task.tags : null
          })
        });
        if (!problemsResponse.ok) throw new Error(`Failed to fetch problems: ${problemsResponse.status}`);
        return await problemsResponse.json();

      default:
        throw new Error(`Unknown data type: ${task.dataType}`);
    }
  }

  /**
   * Cache fetched data
   */
  private cacheData(task: PriorityTaskConfig, data: any): void {
    switch (task.dataType) {
      case 'tags':
        this.cacheService.cacheTags(task.examName, task.sectionName, data);
        break;
      case 'problems':
        this.cacheService.cacheProblems(task.examName, task.sectionName, task.tags || [], data);
        break;
    }
  }

  /**
   * Get related sections for an exam
   */
  private getRelatedSections(currentExam: string, currentSection: string): string[] {
    const examSections: Record<string, string[]> = {
      'GRE': ['quants', 'verbal'],
      'GMAT': ['quants', 'verbal'],
      'CAT': ['quants', 'verbal', 'lrdi']
    };

    return (examSections[currentExam] || []).filter(section => section !== currentSection);
  }

  /**
   * Get other exam types
   */
  private getOtherExams(currentExam: string): string[] {
    const allExams = ['GRE', 'GMAT', 'CAT'];
    return allExams.filter(exam => exam !== currentExam);
  }

  /**
   * Register callback for when specific data is loaded
   */
  onDataLoaded(taskId: string, callback: (data: any) => void): void {
    this.onDataLoadedCallbacks.set(taskId, callback);
  }

  /**
   * Remove data loaded callback
   */
  removeDataLoadedCallback(taskId: string): void {
    this.onDataLoadedCallbacks.delete(taskId);
  }

  /**
   * Check if a task is completed
   */
  isTaskCompleted(taskId: string): boolean {
    return this.completedTasks.has(taskId);
  }

  /**
   * Get cache statistics with priority information
   */
  getCacheStatsWithPriority() {
    return {
      ...this.cacheService.getCacheStats(),
      priorityCache: {
        pendingTasks: this.pendingTasks.size,
        activeFetches: this.activeFetches.size,
        completedTasks: this.completedTasks.size,
        isProcessing: this.isProcessing,
        queueSizes: {
          immediate: this.priorityQueues[CachePriority.IMMEDIATE].length,
          high: this.priorityQueues[CachePriority.HIGH].length,
          medium: this.priorityQueues[CachePriority.MEDIUM].length,
          low: this.priorityQueues[CachePriority.LOW].length,
        }
      }
    };
  }

  /**
   * Clear all pending tasks and reset state
   */
  private clearPendingTasks(): void {
    this.pendingTasks.clear();
    this.activeFetches.clear();
    this.completedTasks.clear();
    Object.values(this.priorityQueues).forEach(queue => queue.length = 0);
  }

  /**
   * Generate unique task ID
   */
  private generateTaskId(task: PriorityTaskConfig): string {
    const tagsStr = task.tags?.length ? JSON.stringify(task.tags.sort()) : 'no-tags';
    return `${task.examName}-${task.sectionName}-${task.dataType}-${tagsStr}`;
  }

  /**
   * Utility delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Singleton priority cache manager
 */
let priorityCacheManager: PriorityCacheManager | null = null;

export function getPriorityCacheManager(): PriorityCacheManager {
  if (!priorityCacheManager) {
    priorityCacheManager = new PriorityCacheManager();
  }
  return priorityCacheManager;
}

/**
 * React hook for priority caching
 */
export function usePriorityCache() {
  const manager = getPriorityCacheManager();

  return {
    executePriorityPlan: manager.executePriorityPlan.bind(manager),
    generatePriorityPlan: manager.generatePriorityPlan.bind(manager),
    onDataLoaded: manager.onDataLoaded.bind(manager),
    removeDataLoadedCallback: manager.removeDataLoadedCallback.bind(manager),
    isTaskCompleted: manager.isTaskCompleted.bind(manager),
    getCacheStats: manager.getCacheStatsWithPriority.bind(manager),
  };
}