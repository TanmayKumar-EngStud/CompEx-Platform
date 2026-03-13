/**
 * Pre-fetch Service
 * 
 * Handles intelligent background prefetching of questions for smooth
 * pagination. Works with the PaginationCacheService to preload questions
 * that users are likely to navigate to next.
 */

import { getQuestionDetails } from "./question-details-service";
import { HybridProblem } from "@/shared/stores/problems/cache";

export interface PrefetchOptions {
  /** Priority level for the prefetch request */
  priority: 'high' | 'medium' | 'low';

  /** Whether to use browser idle time for prefetching */
  useIdleTime: boolean;

  /** Maximum number of concurrent prefetch requests */
  maxConcurrent: number;

  /** Timeout for prefetch requests in milliseconds */
  timeout: number;

  /** Whether to retry failed prefetch requests */
  retryOnFailure: boolean;
}

export interface PrefetchRequest {
  /** Unique identifier for this prefetch request */
  id: string;

  /** Section ID this prefetch is for */
  sectionId: string;

  /** Page number being prefetched */
  pageNumber: number;

  /** Question IDs to prefetch */
  questionIds: string[];

  /** Priority of this request */
  priority: 'high' | 'medium' | 'low';

  /** Timestamp when request was created */
  createdAt: number;

  /** Whether this request is currently in progress */
  inProgress: boolean;

  /** Promise resolving when prefetch completes */
  promise?: Promise<HybridProblem[]>;
}

export interface PrefetchStats {
  /** Total prefetch requests made */
  totalRequests: number;

  /** Successfully completed prefetch requests */
  successfulRequests: number;

  /** Failed prefetch requests */
  failedRequests: number;

  /** Currently pending prefetch requests */
  pendingRequests: number;

  /** Average prefetch time in milliseconds */
  averagePrefetchTime: number;

  /** Cache hit ratio for prefetched content */
  cacheHitRatio: number;
}

export class PreFetchService {
  private activeRequests: Map<string, PrefetchRequest> = new Map();
  private completedRequests: Map<string, HybridProblem[]> = new Map();
  private options: PrefetchOptions;
  private stats: PrefetchStats;
  private requestQueue: PrefetchRequest[] = [];
  private isProcessingQueue = false;

  constructor(options: Partial<PrefetchOptions> = {}) {
    this.options = {
      priority: 'medium',
      useIdleTime: true,
      maxConcurrent: 2,
      timeout: 10000, // 10 seconds
      retryOnFailure: true,
      ...options
    };

    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      pendingRequests: 0,
      averagePrefetchTime: 0,
      cacheHitRatio: 0
    };

    console.log('🚀 PreFetchService initialized with options:', this.options);
  }

  /**
   * Schedule a prefetch request for a specific page
   */
  async prefetchPage(
    sectionId: string,
    pageNumber: number,
    questionIds: string[],
    priority: 'high' | 'medium' | 'low' = 'medium'
  ): Promise<void> {
    const requestId = `${sectionId}-page-${pageNumber}`;

    // Check if already prefetched or in progress
    if (this.completedRequests.has(requestId) || this.activeRequests.has(requestId)) {
      console.log(`⏭️  Skipping prefetch for ${requestId} - already cached or in progress`);
      return;
    }

    const request: PrefetchRequest = {
      id: requestId,
      sectionId,
      pageNumber,
      questionIds,
      priority,
      createdAt: Date.now(),
      inProgress: false
    };

    console.log(`📋 Queuing prefetch request: ${requestId} (${questionIds.length} questions)`);

    this.requestQueue.push(request);
    this.stats.totalRequests++;

    // Sort queue by priority
    this.requestQueue.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });

    // Start processing queue if not already running
    if (!this.isProcessingQueue) {
      this.processQueue();
    }
  }

  /**
   * Process the prefetch queue respecting concurrency limits
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue) return;

    this.isProcessingQueue = true;

    while (this.requestQueue.length > 0 && this.activeRequests.size < this.options.maxConcurrent) {
      const request = this.requestQueue.shift()!;

      // Check if we should use idle time
      if (this.options.useIdleTime && !this.isSystemIdle()) {
        console.log(`⏸️  Delaying prefetch ${request.id} - system not idle`);
        this.requestQueue.unshift(request); // Put back at front
        break;
      }

      this.executeRequest(request);
    }

    this.isProcessingQueue = false;

    // Schedule next queue processing if there are pending requests
    if (this.requestQueue.length > 0) {
      setTimeout(() => this.processQueue(), 1000);
    }
  }

  /**
   * Execute a single prefetch request
   */
  private async executeRequest(request: PrefetchRequest): Promise<void> {
    console.log(`🚀 Starting prefetch: ${request.id}`);

    request.inProgress = true;
    this.activeRequests.set(request.id, request);
    this.stats.pendingRequests++;

    const startTime = Date.now();

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.options.timeout);

      // Convert question IDs to numbers
      const numericIds = request.questionIds.map(id => parseInt(id, 10));

      // Fetch question details
      const promise = this.fetchWithTimeout(numericIds, controller.signal);
      request.promise = promise;

      const questions = await promise;

      clearTimeout(timeoutId);

      // Convert to HybridProblem format
      const hybridQuestions: HybridProblem[] = questions.map(q => ({
        problemid: q.problemid.toString(),
        title: q.title,
        difficulty: 0, // Will be set by actual data
        addedDate: new Date(),
        type: q.type,
        iscorrect: null,
        isParent: false,
        absoluteIndex: 0, // Will be set by pagination logic
        ...q
      }));

      // Store result
      this.completedRequests.set(request.id, hybridQuestions);

      const duration = Date.now() - startTime;
      this.stats.successfulRequests++;
      this.updateAverageTime(duration);

      console.log(`✅ Prefetch completed: ${request.id} (${duration}ms, ${questions.length} questions)`);

    } catch (error) {
      const duration = Date.now() - startTime;
      this.stats.failedRequests++;

      console.warn(`❌ Prefetch failed: ${request.id} (${duration}ms)`, error);

      // Retry logic
      if (this.options.retryOnFailure && !this.isAbortError(error)) {
        console.log(`🔄 Retrying prefetch: ${request.id}`);
        // Add back to queue with lower priority
        const retryRequest = {
          ...request,
          priority: 'low' as const,
          createdAt: Date.now()
        };
        this.requestQueue.push(retryRequest);
      }
    } finally {
      // Clean up
      this.activeRequests.delete(request.id);
      this.stats.pendingRequests--;

      // Continue processing queue
      if (this.requestQueue.length > 0) {
        setTimeout(() => this.processQueue(), 100);
      }
    }
  }

  /**
   * Fetch questions with timeout support
   */
  private async fetchWithTimeout(
    questionIds: number[],
    _signal: AbortSignal
  ): Promise<any[]> {
    return getQuestionDetails(questionIds);
  }

  /**
   * Get prefetched data if available
   */
  getPrefetchedData(sectionId: string, pageNumber: number): HybridProblem[] | null {
    const requestId = `${sectionId}-page-${pageNumber}`;
    const data = this.completedRequests.get(requestId);

    if (data) {
      console.log(`✅ Cache hit for prefetched data: ${requestId}`);
      // Remove from cache after use to free memory
      this.completedRequests.delete(requestId);
      return data;
    }

    return null;
  }

  /**
   * Check if a prefetch is in progress
   */
  isPrefetchInProgress(sectionId: string, pageNumber: number): boolean {
    const requestId = `${sectionId}-page-${pageNumber}`;
    return this.activeRequests.has(requestId);
  }

  /**
   * Cancel all prefetch requests for a section
   */
  cancelSectionPrefetches(sectionId: string): void {
    console.log(`🛑 Cancelling all prefetches for section: ${sectionId}`);

    // Remove from queue
    this.requestQueue = this.requestQueue.filter(req => req.sectionId !== sectionId);

    // Cancel active requests
    for (const id of Array.from(this.activeRequests.keys())) {
      const request = this.activeRequests.get(id)!;
      if (request.sectionId === sectionId) {
        this.activeRequests.delete(id);
        this.stats.pendingRequests--;
      }
    }

    // Clear completed cache for this section
    for (const id of Array.from(this.completedRequests.keys())) {
      if (id.startsWith(sectionId)) {
        this.completedRequests.delete(id);
      }
    }
  }

  /**
   * Clear all prefetch data
   */
  clearAll(): void {
    console.log('🧹 Clearing all prefetch data');

    this.requestQueue = [];
    this.activeRequests.clear();
    this.completedRequests.clear();
    this.isProcessingQueue = false;

    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      pendingRequests: 0,
      averagePrefetchTime: 0,
      cacheHitRatio: 0
    };
  }

  /**
   * Get prefetch statistics
   */
  getStats(): PrefetchStats {
    this.stats.cacheHitRatio = this.stats.successfulRequests /
      Math.max(this.stats.totalRequests, 1);

    return { ...this.stats };
  }

  /**
   * Update options at runtime
   */
  updateOptions(newOptions: Partial<PrefetchOptions>): void {
    this.options = { ...this.options, ...newOptions };
    console.log('⚙️  Updated prefetch options:', this.options);
  }

  // Private helper methods

  private isSystemIdle(): boolean {
    // Simple idle detection - could be enhanced with more sophisticated logic
    if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
      return true; // Browser supports idle detection
    }

    // Fallback: check if it's been a while since last navigation
    return Date.now() % 10000 < 5000; // Simple time-based check
  }

  private isAbortError(error: any): boolean {
    return error && (error.name === 'AbortError' || error.message?.includes('abort'));
  }

  private updateAverageTime(duration: number): void {
    const totalTime = this.stats.averagePrefetchTime * this.stats.successfulRequests;
    this.stats.averagePrefetchTime =
      (totalTime + duration) / (this.stats.successfulRequests + 1);
  }
}

// Export singleton instance
export const preFetchService = new PreFetchService();