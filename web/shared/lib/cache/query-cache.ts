/**
 * React Query integration with custom caching strategy
 *
 * Provides optimized caching for database queries and API calls
 * with intelligent cache invalidation and prefetching.
 */

import { QueryClient, QueryKey } from "@tanstack/react-query";
import { getCacheManager, CACHE_CONFIGS } from "./cache-manager";

/**
 * Cache key generators for consistent naming
 */
export const CACHE_KEYS = {
   PROBLEMS: (examName: string, sectionName: string, tags: string[]) => [
      "problems",
      examName,
      sectionName,
      JSON.stringify(tags.sort()),
   ],
   PROBLEM_SETS: (examName: string, sectionName: string, tags: string[]) => [
      "problem-sets",
      examName,
      sectionName,
      JSON.stringify(tags.sort()),
   ],
   QUESTIONS: (questionIds: number[]) => [
      "questions",
      JSON.stringify(questionIds.sort()),
   ],
   TAGS: (examName: string, sectionName: string) => [
      "tags",
      examName,
      sectionName,
   ],
   USER_ATTEMPTS: (userId: number, problemId?: number) =>
      problemId
         ? ["user-attempts", userId, problemId]
         : ["user-attempts", userId],
} as const;

/**
 * Enhanced QueryClient with custom caching
 */
export function createOptimizedQueryClient(): QueryClient {
   const cacheManager = getCacheManager();

   const queryClient = new QueryClient({
      defaultOptions: {
         queries: {
            // Global query defaults
            staleTime: 5 * 60 * 1000, // 5 minutes
            gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
            refetchOnWindowFocus: false,
            refetchOnReconnect: "always",
            retry: (failureCount, error: any) => {
               // Don't retry on 4xx errors
               if (error?.status >= 400 && error?.status < 500) {
                  return false;
               }
               // Retry up to 3 times for other errors
               return failureCount < 3;
            },
            retryDelay: (attemptIndex) =>
               Math.min(1000 * 2 ** attemptIndex, 30000),
         },
         mutations: {
            // Optimistic updates and cache invalidation
            onSuccess: (data, variables, context) => {
               // Invalidate related queries after successful mutations
               if (context && (context as any).invalidateQueries) {
                  (context as any).invalidateQueries.forEach(
                     (queryKey: QueryKey) => {
                        queryClient.invalidateQueries({ queryKey });
                     }
                  );
               }
            },
            onError: (error, variables, context) => {
               // Rollback optimistic updates on error
               if (context && (context as any).rollback) {
                  (context as any).rollback();
               }
            },
         },
      },
   });

   return queryClient;
}

/**
 * Custom cache utilities for specific data types
 */
export class QueryCacheService {
   private cacheManager = getCacheManager();
   private problemsCache = this.cacheManager.getCache(
      "problems",
      CACHE_CONFIGS.PROBLEMS
   );
   private tagsCache = this.cacheManager.getCache("tags", CACHE_CONFIGS.TAGS);
   private apiCache = this.cacheManager.getCache(
      "api",
      CACHE_CONFIGS.API_RESPONSES
   );

   /**
    * Cache problems data with intelligent key generation
    */
   cacheProblems(
      examName: string,
      sectionName: string,
      tags: string[],
      data: any
   ): void {
      const key = this.generateProblemsKey(examName, sectionName, tags);
      this.problemsCache.set(key, data);
   }

   /**
    * Get cached problems data
    */
   getCachedProblems(
      examName: string,
      sectionName: string,
      tags: string[]
   ): any | null {
      const key = this.generateProblemsKey(examName, sectionName, tags);
      return this.problemsCache.get(key);
   }

   /**
    * Cache tags data
    */
   cacheTags(examName: string, sectionName: string, data: any): void {
      const key = `${examName}-${sectionName}`;
      this.tagsCache.set(key, data);
   }

   /**
    * Get cached tags
    */
   getCachedTags(examName: string, sectionName: string): any | null {
      const key = `${examName}-${sectionName}`;
      return this.tagsCache.get(key);
   }

   /**
    * Cache API response
    */
   cacheApiResponse(endpoint: string, params: any, data: any): void {
      const key = `${endpoint}-${JSON.stringify(params)}`;
      this.apiCache.set(key, data);
   }

   /**
    * Get cached API response
    */
   getCachedApiResponse(endpoint: string, params: any): any | null {
      const key = `${endpoint}-${JSON.stringify(params)}`;
      return this.apiCache.get(key);
   }

   /**
    * Invalidate related caches
    */
   invalidateProblemsCache(examName?: string, sectionName?: string): void {
      const keys = this.problemsCache.keys();

      keys.forEach((key) => {
         if (!examName || key.includes(examName)) {
            if (!sectionName || key.includes(sectionName)) {
               this.problemsCache.delete(key);
            }
         }
      });
   }

   /**
    * Invalidate tags cache
    */
   invalidateTagsCache(examName?: string): void {
      const keys = this.tagsCache.keys();

      keys.forEach((key) => {
         if (!examName || key.includes(examName)) {
            this.tagsCache.delete(key);
         }
      });
   }

   /**
    * Get cache statistics
    */
   getCacheStats() {
      return {
         problems: this.problemsCache.getMetrics(),
         tags: this.tagsCache.getMetrics(),
         api: this.apiCache.getMetrics(),
         summary: this.cacheManager.getStatsSummary(),
      };
   }

   /**
    * Preload frequently accessed data
    */
   async preloadCommonData(): Promise<void> {
      try {
         // Preload common exam types and sections
         const commonCombinations = [
            { examName: "GRE", sectionName: "quants" },
            { examName: "GRE", sectionName: "verbal" },
            { examName: "GMAT", sectionName: "quants" },
            { examName: "GMAT", sectionName: "verbal" },
         ];

         // Preload tags for common combinations
         const tagPromises = commonCombinations.map(
            async ({ examName, sectionName }) => {
               if (!this.getCachedTags(examName, sectionName)) {
                  try {
                     const response = await fetch(
                        `/api/problems/tags?examName=${examName}&sectionName=${sectionName}`
                     );
                     if (response.ok) {
                        const data = await response.json();
                        this.cacheTags(examName, sectionName, data.tags);
                     }
                  } catch (error) {
                     console.warn(
                        `Failed to preload tags for ${examName}/${sectionName}:`,
                        error
                     );
                  }
               }
            }
         );

         // Also preload common problem sets (first page of popular exams)
         const problemPromises = commonCombinations
            .slice(0, 4)
            .map(async ({ examName, sectionName }) => {
               try {
                  const response = await fetch(
                     `/api/problems?examName=${examName}&sectionName=${sectionName}&page=1&pageSize=10`
                  );
                  if (response.ok) {
                     const data = await response.json();
                     this.cacheProblems(examName, sectionName, [], data);
                  }
               } catch (error) {
                  console.warn(
                     `Failed to preload problems for ${examName}/${sectionName}:`,
                     error
                  );
               }
            });

         await Promise.allSettled([...tagPromises, ...problemPromises]);
         console.log("✅ Common data preloaded successfully");
      } catch (error) {
         console.warn("⚠️ Failed to preload common data:", error);
      }
   }

   /**
    * Generate consistent problems cache key
    */
   private generateProblemsKey(
      examName: string,
      sectionName: string,
      tags: string[]
   ): string {
      const sortedTags = [...tags].sort();
      return `${examName}-${sectionName}-${JSON.stringify(sortedTags)}`;
   }
}

/**
 * Singleton query cache service
 */
let queryCacheService: QueryCacheService | null = null;

export function getQueryCacheService(): QueryCacheService {
   if (!queryCacheService) {
      queryCacheService = new QueryCacheService();
   }
   return queryCacheService;
}

/**
 * Cache-aware fetch wrapper
 */
export async function cachedFetch<T = any>(
   url: string,
   options: RequestInit = {},
   cacheKey?: string,
   cacheTTL?: number
): Promise<T> {
   const cacheService = getQueryCacheService();
   const key = cacheKey || url;

   // Check cache first
   const cached = cacheService.getCachedApiResponse(key, options);
   if (cached) {
      return cached;
   }

   // Fetch from network
   const response = await fetch(url, options);
   if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
   }

   const data = await response.json();

   // Cache the response
   if (response.status === 200) {
      cacheService.cacheApiResponse(key, options, data);
   }

   return data;
}

/**
 * Optimized query configurations for different data types
 */
export const QUERY_CONFIGS = {
   PROBLEMS: {
      staleTime: 10 * 60 * 1000, // 10 minutes
      gcTime: 15 * 60 * 1000, // 15 minutes
      refetchOnWindowFocus: false,
   },
   TAGS: {
      staleTime: 30 * 60 * 1000, // 30 minutes
      gcTime: 60 * 60 * 1000, // 1 hour
      refetchOnWindowFocus: false,
   },
   QUESTIONS: {
      staleTime: 15 * 60 * 1000, // 15 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: false,
   },
   USER_ATTEMPTS: {
      staleTime: 2 * 60 * 1000, // 2 minutes
      gcTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: true,
   },
} as const;
