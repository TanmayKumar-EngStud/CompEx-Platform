/**
 * Tag Filter Service
 * 
 * Handles tag-based filtering logic for the pagination cache system.
 * Provides utilities for filtering questions by tags and managing
 * filter state for different sections.
 */

export interface TagFilterRequest {
  sectionId: string;
  includeTags: string[];
  excludeTags?: string[];
  userId?: number;
}

export interface TagFilterResult {
  questionIds: string[];
  totalQuestions: number;
  appliedFilters: {
    includeTags: string[];
    excludeTags: string[];
  };
  sectionId: string;
}

export interface FilterCacheEntry {
  filterKey: string;
  questionIds: string[];
  totalQuestions: number;
  createdAt: number;
  expiresAt: number;
}

export interface TagFilterStats {
  totalFilterRequests: number;
  cacheHits: number;
  cacheMisses: number;
  cacheHitRatio: number;
  averageFilterTime: number;
  activeCacheEntries: number;
}

export class TagFilterService {
  private filterCache: Map<string, FilterCacheEntry> = new Map();
  private stats: TagFilterStats;
  private cacheTTL: number;

  constructor(cacheTTL: number = 10 * 60 * 1000) { // 10 minutes default
    this.cacheTTL = cacheTTL;
    this.stats = {
      totalFilterRequests: 0,
      cacheHits: 0,
      cacheMisses: 0,
      cacheHitRatio: 0,
      averageFilterTime: 0,
      activeCacheEntries: 0
    };

    console.log('🏷️  TagFilterService initialized with cache TTL:', cacheTTL);
    
    // Set up periodic cache cleanup
    setInterval(() => this.cleanExpiredCache(), 5 * 60 * 1000); // Every 5 minutes
  }

  /**
   * Apply tag filters and get filtered question IDs
   */
  async applyTagFilter(request: TagFilterRequest): Promise<TagFilterResult> {
    const startTime = Date.now();
    this.stats.totalFilterRequests++;

    try {
      // Generate cache key
      const filterKey = this.generateFilterKey(request);
      
      // Check cache first
      const cachedResult = this.getCachedResult(filterKey);
      if (cachedResult) {
        this.stats.cacheHits++;
        console.log(`✅ Tag filter cache hit: ${filterKey}`);
        
        return {
          questionIds: cachedResult.questionIds,
          totalQuestions: cachedResult.totalQuestions,
          appliedFilters: {
            includeTags: request.includeTags,
            excludeTags: request.excludeTags || []
          },
          sectionId: request.sectionId
        };
      }

      // Cache miss - fetch from API
      this.stats.cacheMisses++;
      console.log(`🔍 Tag filter cache miss: ${filterKey} - fetching from API`);
      
      const result = await this.fetchFilteredQuestionIds(request);
      
      // Cache the result
      this.cacheResult(filterKey, result);
      
      const duration = Date.now() - startTime;
      this.updateAverageTime(duration);
      
      console.log(`✅ Tag filter completed: ${result.totalQuestions} questions (${duration}ms)`);
      
      return result;
      
    } catch (error) {
      console.error('❌ Tag filter failed:', error);
      throw error;
    }
  }

  /**
   * Get available tags for a section
   */
  async getAvailableTags(sectionId: string): Promise<string[]> {
    try {
      const response = await fetch(`/api/problems/tags?sectionId=${encodeURIComponent(sectionId)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return result.tags || [];
      
    } catch (error) {
      console.error('❌ Failed to fetch available tags:', error);
      return [];
    }
  }

  /**
   * Get tag statistics for a section (how many questions each tag has)
   */
  async getTagStatistics(sectionId: string): Promise<Map<string, number>> {
    try {
      const response = await fetch(`/api/problems/tag-stats?sectionId=${encodeURIComponent(sectionId)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Convert object to Map
      const statsMap = new Map<string, number>();
      for (const [tag, count] of Object.entries(result.tagStats || {})) {
        statsMap.set(tag, count as number);
      }
      
      return statsMap;
      
    } catch (error) {
      console.error('❌ Failed to fetch tag statistics:', error);
      return new Map();
    }
  }

  /**
   * Validate tag filters before applying
   */
  validateTagFilters(includeTags: string[], excludeTags: string[] = []): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    
    // Check for empty include tags
    if (!includeTags || includeTags.length === 0) {
      errors.push('At least one include tag must be specified');
    }
    
    // Check for conflicts between include and exclude tags
    const conflicts = includeTags.filter(tag => excludeTags.includes(tag));
    if (conflicts.length > 0) {
      errors.push(`Tags cannot be both included and excluded: ${conflicts.join(', ')}`);
    }
    
    // Check for valid tag format
    const invalidTags = [...includeTags, ...excludeTags].filter(tag => 
      !tag || typeof tag !== 'string' || tag.trim().length === 0
    );
    if (invalidTags.length > 0) {
      errors.push('All tags must be non-empty strings');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Clear filter cache for a specific section
   */
  clearSectionCache(sectionId: string): void {
    console.log(`🧹 Clearing tag filter cache for section: ${sectionId}`);
    
    for (const [key, entry] of Array.from(this.filterCache.entries())) {
      if (key.startsWith(sectionId)) {
        this.filterCache.delete(key);
      }
    }
    
    this.updateCacheStats();
  }

  /**
   * Clear all filter cache
   */
  clearAllCache(): void {
    console.log('🧹 Clearing all tag filter cache');
    this.filterCache.clear();
    this.updateCacheStats();
  }

  /**
   * Get filter statistics
   */
  getStats(): TagFilterStats {
    this.stats.cacheHitRatio = this.stats.cacheHits / 
      Math.max(this.stats.totalFilterRequests, 1);
    this.stats.activeCacheEntries = this.filterCache.size;
    
    return { ...this.stats };
  }

  /**
   * Get currently cached filters for debugging
   */
  getCachedFilters(): string[] {
    return Array.from(this.filterCache.keys());
  }

  // Private methods

  private async fetchFilteredQuestionIds(request: TagFilterRequest): Promise<TagFilterResult> {
    const response = await fetch('/api/problems/filtered-ids', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sectionId: request.sectionId,
        tags: request.includeTags,
        userId: request.userId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    return {
      questionIds: result.questionIds || [],
      totalQuestions: result.totalQuestions || 0,
      appliedFilters: {
        includeTags: request.includeTags,
        excludeTags: request.excludeTags || []
      },
      sectionId: request.sectionId
    };
  }

  private generateFilterKey(request: TagFilterRequest): string {
    const includeTags = [...request.includeTags].sort().join(',');
    const excludeTags = [...(request.excludeTags || [])].sort().join(',');
    const userId = request.userId || 'anonymous';
    
    return `${request.sectionId}|${includeTags}|${excludeTags}|${userId}`;
  }

  private getCachedResult(filterKey: string): FilterCacheEntry | null {
    const entry = this.filterCache.get(filterKey);
    
    if (!entry) return null;
    
    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.filterCache.delete(filterKey);
      return null;
    }
    
    return entry;
  }

  private cacheResult(filterKey: string, result: TagFilterResult): void {
    const entry: FilterCacheEntry = {
      filterKey,
      questionIds: result.questionIds,
      totalQuestions: result.totalQuestions,
      createdAt: Date.now(),
      expiresAt: Date.now() + this.cacheTTL
    };
    
    this.filterCache.set(filterKey, entry);
    this.updateCacheStats();
    
    console.log(`💾 Cached filter result: ${filterKey} (${result.totalQuestions} questions)`);
  }

  private cleanExpiredCache(): void {
    const now = Date.now();
    let removedCount = 0;
    
    for (const [key, entry] of Array.from(this.filterCache.entries())) {
      if (now > entry.expiresAt) {
        this.filterCache.delete(key);
        removedCount++;
      }
    }
    
    if (removedCount > 0) {
      console.log(`🧹 Cleaned ${removedCount} expired tag filter cache entries`);
      this.updateCacheStats();
    }
  }

  private updateCacheStats(): void {
    this.stats.activeCacheEntries = this.filterCache.size;
  }

  private updateAverageTime(duration: number): void {
    const totalRequests = this.stats.totalFilterRequests;
    const totalTime = this.stats.averageFilterTime * (totalRequests - 1);
    this.stats.averageFilterTime = (totalTime + duration) / totalRequests;
  }
}

// Export singleton instance
export const tagFilterService = new TagFilterService();