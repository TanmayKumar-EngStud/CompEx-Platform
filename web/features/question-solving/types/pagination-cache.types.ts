/**
 * TypeScript interfaces for the pagination cache system
 * 
 * This file defines the core data structures for the doubly-linked list
 * based pagination cache that replaces the inefficient fetch-all approach.
 */

import { HybridProblem } from "@/shared/stores/problems/cache";

/**
 * Individual node in the doubly-linked list representing a cached page
 */
export interface CacheNode {
  /** Page number (1-based) */
  pageNumber: number;

  /** Section identifier for this cache node */
  sectionId: string;

  /** Actual question data for this page */
  questionData: HybridProblem[];

  /** Pointer to next page node */
  next: CacheNode | null;

  /** Pointer to previous page node */
  previous: CacheNode | null;

  /** Timestamp when this node was created */
  createdAt: number;

  /** Timestamp when this node was last accessed */
  lastAccessed: number;
}

/**
 * Cache management for a specific section (e.g., GRE Quants, GMAT Verbal)
 */
export interface SectionCache {
  /** Unique section identifier */
  sectionId: string;

  /** Currently active cache node (the page user is viewing) */
  currentNode: CacheNode;

  /** Original unfiltered question entries (top-level rows) */
  questionEntries: QuestionIdEntry[];

  /** Filtered question entries based on current tag selection */
  filteredQuestionEntries: QuestionIdEntry[];

  /** Total number of rows for current state (filtered or unfiltered) */
  totalQuestions: number;

  /** Total number of pages for current state */
  totalPages: number;

  /** Whether current active list is shuffled */
  isShuffled: boolean;

  /** Whether filters are currently applied */
  isFiltered: boolean;

  /** Currently applied tag filters */
  activeFilters: string[];

  /** Page position before filters were applied (for restoration) */
  originalPosition: number;

  /** Questions per page setting */
  questionsPerPage: number;
}

/**
 * Global cache container managing all section caches
 */
export interface GlobalCache {
  /** Map of section ID to section cache */
  sections: Map<string, SectionCache>;

  /** Currently active section ID */
  currentSectionId: string;

  /** Maximum number of cache nodes to keep per section */
  maxCacheSize: number;

  /** Global cache creation timestamp */
  createdAt: number;
}

/**
 * Configuration for cache behavior
 */
export interface CacheConfig {
  /** Maximum number of pages to cache per section */
  maxPagesPerSection: number;

  /** Number of questions per page */
  questionsPerPage: number;

  /** Whether to enable prefetching */
  enablePrefetch: boolean;

  /** How many pages to prefetch ahead */
  prefetchDistance: number;

  /** Cache TTL in milliseconds */
  cacheTTL: number;
}

/**
 * Cache operation result for error handling
 */
export interface CacheOperationResult {
  /** Whether the operation was successful */
  success: boolean;

  /** Error message if operation failed */
  error?: string;

  /** Optional data returned by the operation */
  data?: any;
}

/**
 * Prefetch request parameters
 */
export interface PrefetchRequest {
  /** Section ID to prefetch for */
  sectionId: string;

  /** Target page number to prefetch */
  pageNumber: number;

  /** Whether this is filtered data */
  isFiltered: boolean;

  /** Filter tags if applicable */
  filters?: string[];

  /** Question entries to use for prefetch (shuffled or filtered) */
  questionEntries: QuestionIdEntry[];
}

/**
 * Question ID Entry types for structured pagination
 */
export interface QuestionIdItem {
  problemid: number;
}

export interface QuestionIdGroup {
  problemsSetId: number;
  problems: QuestionIdItem[];
}

export type QuestionIdEntry = QuestionIdGroup | QuestionIdItem;

/**
 * Navigation state for tracking user movement
 */
export interface NavigationState {
  /** Current page number */
  currentPage: number;

  /** Previous page number */
  previousPage: number;

  /** Direction of last navigation */
  direction: 'next' | 'previous' | 'jump';

  /** Timestamp of last navigation */
  lastNavigationTime: number;
}

/**
 * Cache statistics for monitoring and debugging
 */
export interface CacheStats {
  /** Total cache hits */
  hits: number;

  /** Total cache misses */
  misses: number;

  /** Cache hit ratio */
  hitRatio: number;

  /** Total number of cached pages across all sections */
  totalCachedPages: number;

  /** Memory usage estimate in bytes */
  estimatedMemoryUsage: number;

  /** Number of prefetch operations completed */
  prefetchCount: number;
}

/**
 * Events emitted by the cache system for monitoring
 */
export type CacheEvent =
  | { type: 'cache_hit'; sectionId: string; pageNumber: number }
  | { type: 'cache_miss'; sectionId: string; pageNumber: number }
  | { type: 'page_cached'; sectionId: string; pageNumber: number }
  | { type: 'page_evicted'; sectionId: string; pageNumber: number }
  | { type: 'prefetch_started'; sectionId: string; pageNumber: number }
  | { type: 'prefetch_completed'; sectionId: string; pageNumber: number }
  | { type: 'section_switched'; fromSectionId: string; toSectionId: string }
  | { type: 'cache_cleared'; sectionId?: string }
  | { type: 'section_cleared'; sectionId: string }
  | { type: 'all_caches_cleared' }
  | { type: 'shuffle_completed'; sectionId: string; strategy?: string; algorithm?: string; questionCount?: number };