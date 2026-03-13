/**
 * Advanced Caching Strategy for CompEx Application
 * 
 * Implements multi-tier caching for optimal performance:
 * - Memory cache for frequently accessed data
 * - Browser cache for static resources
 * - Query cache for database results
 * - Service worker cache for offline capabilities
 */

export interface CacheConfig {
   defaultTTL: number; // Time to live in milliseconds
   maxSize: number; // Maximum number of items in cache
   enablePersistence: boolean; // Store in localStorage/sessionStorage
   compressionEnabled: boolean; // Compress large cached items
}

export interface CacheItem<T = any> {
   data: T;
   timestamp: number;
   ttl: number;
   accessCount: number;
   lastAccessed: number;
   size: number; // Estimated size in bytes
}

export interface CacheMetrics {
   hits: number;
   misses: number;
   hitRate: number;
   totalSize: number;
   itemCount: number;
   evictions: number;
}

/**
 * Advanced LRU Cache with TTL and metrics
 */
export class AdvancedCache<T = any> {
   private cache = new Map<string, CacheItem<T>>();
   private accessOrder = new Map<string, number>(); // For LRU ordering
   private metrics: CacheMetrics = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      totalSize: 0,
      itemCount: 0,
      evictions: 0,
   };
   private accessCounter = 0;

   constructor(private config: CacheConfig) {
      this.setupCleanupInterval();
      this.loadFromPersistence();
   }

   /**
    * Get item from cache
    */
   get(key: string): T | null {
      const item = this.cache.get(key);
      
      if (!item) {
         this.metrics.misses++;
         this.updateHitRate();
         return null;
      }

      // Check if item has expired
      if (this.isExpired(item)) {
         this.delete(key);
         this.metrics.misses++;
         this.updateHitRate();
         return null;
      }

      // Update access information
      item.accessCount++;
      item.lastAccessed = Date.now();
      this.accessOrder.set(key, this.accessCounter++);

      this.metrics.hits++;
      this.updateHitRate();
      
      return item.data;
   }

   /**
    * Set item in cache
    */
   set(key: string, data: T, customTTL?: number): void {
      const ttl = customTTL || this.config.defaultTTL;
      const size = this.estimateSize(data);
      
      // Check if we need to evict items
      this.evictIfNecessary(size);

      const item: CacheItem<T> = {
         data,
         timestamp: Date.now(),
         ttl,
         accessCount: 1,
         lastAccessed: Date.now(),
         size,
      };

      // Remove existing item if it exists
      if (this.cache.has(key)) {
         const existingItem = this.cache.get(key)!;
         this.metrics.totalSize -= existingItem.size;
      } else {
         this.metrics.itemCount++;
      }

      this.cache.set(key, item);
      this.accessOrder.set(key, this.accessCounter++);
      this.metrics.totalSize += size;

      this.saveToPersistence();
   }

   /**
    * Delete item from cache
    */
   delete(key: string): boolean {
      const item = this.cache.get(key);
      if (item) {
         this.cache.delete(key);
         this.accessOrder.delete(key);
         this.metrics.totalSize -= item.size;
         this.metrics.itemCount--;
         this.saveToPersistence();
         return true;
      }
      return false;
   }

   /**
    * Clear entire cache
    */
   clear(): void {
      this.cache.clear();
      this.accessOrder.clear();
      this.metrics = {
         hits: 0,
         misses: 0,
         hitRate: 0,
         totalSize: 0,
         itemCount: 0,
         evictions: 0,
      };
      this.accessCounter = 0;
      this.saveToPersistence();
   }

   /**
    * Get cache metrics
    */
   getMetrics(): CacheMetrics {
      return { ...this.metrics };
   }

   /**
    * Get all cache keys
    */
   keys(): string[] {
      return Array.from(this.cache.keys());
   }

   /**
    * Check if key exists and is not expired
    */
   has(key: string): boolean {
      const item = this.cache.get(key);
      return item ? !this.isExpired(item) : false;
   }

   /**
    * Get cache size
    */
   size(): number {
      return this.cache.size;
   }

   /**
    * Check if item is expired
    */
   private isExpired(item: CacheItem<T>): boolean {
      return Date.now() - item.timestamp > item.ttl;
   }

   /**
    * Estimate size of data in bytes
    */
   private estimateSize(data: T): number {
      try {
         return new Blob([JSON.stringify(data)]).size;
      } catch {
         // Fallback estimation
         return JSON.stringify(data).length * 2; // Rough estimate: 2 bytes per character
      }
   }

   /**
    * Evict items if cache is full
    */
   private evictIfNecessary(newItemSize: number): void {
      // Check size limit
      while (this.metrics.totalSize + newItemSize > this.config.maxSize * 1024) {
         this.evictLeastRecentlyUsed();
      }

      // Check item count limit
      while (this.cache.size >= this.config.maxSize) {
         this.evictLeastRecentlyUsed();
      }
   }

   /**
    * Evict least recently used item
    */
   private evictLeastRecentlyUsed(): void {
      let oldestKey: string | null = null;
      let oldestAccess = Infinity;

      for (const [key, accessTime] of Array.from(this.accessOrder.entries())) {
         if (accessTime < oldestAccess) {
            oldestAccess = accessTime;
            oldestKey = key;
         }
      }

      if (oldestKey) {
         this.delete(oldestKey);
         this.metrics.evictions++;
      }
   }

   /**
    * Update hit rate metric
    */
   private updateHitRate(): void {
      const total = this.metrics.hits + this.metrics.misses;
      this.metrics.hitRate = total > 0 ? this.metrics.hits / total : 0;
   }

   /**
    * Setup cleanup interval for expired items
    */
   private setupCleanupInterval(): void {
      if (typeof window !== 'undefined') {
         setInterval(() => {
            this.cleanupExpiredItems();
         }, 60000); // Check every minute
      }
   }

   /**
    * Clean up expired items
    */
   private cleanupExpiredItems(): void {
      const keysToDelete: string[] = [];
      
      for (const [key, item] of Array.from(this.cache.entries())) {
         if (this.isExpired(item)) {
            keysToDelete.push(key);
         }
      }

      keysToDelete.forEach(key => this.delete(key));
   }

   /**
    * Save cache to persistence if enabled
    */
   private saveToPersistence(): void {
      if (!this.config.enablePersistence || typeof window === 'undefined') {
         return;
      }

      try {
         const cacheData = {
            cache: Array.from(this.cache.entries()),
            accessOrder: Array.from(this.accessOrder.entries()),
            metrics: this.metrics,
            accessCounter: this.accessCounter,
         };

         const serialized = JSON.stringify(cacheData);
         sessionStorage.setItem('compex-cache', serialized);
      } catch (error) {
         console.warn('Failed to save cache to persistence:', error);
      }
   }

   /**
    * Load cache from persistence if available
    */
   private loadFromPersistence(): void {
      if (!this.config.enablePersistence || typeof window === 'undefined') {
         return;
      }

      try {
         const cached = sessionStorage.getItem('compex-cache');
         if (cached) {
            const cacheData = JSON.parse(cached);
            
            // Restore cache
            this.cache = new Map(cacheData.cache);
            this.accessOrder = new Map(cacheData.accessOrder);
            this.metrics = cacheData.metrics || this.metrics;
            this.accessCounter = cacheData.accessCounter || 0;

            // Clean up expired items
            this.cleanupExpiredItems();
         }
      } catch (error) {
         console.warn('Failed to load cache from persistence:', error);
      }
   }
}

/**
 * Cache manager for different types of data
 */
export class CacheManager {
   private caches = new Map<string, AdvancedCache>();
   private defaultConfig: CacheConfig = {
      defaultTTL: 5 * 60 * 1000, // 5 minutes
      maxSize: 100, // 100 items
      enablePersistence: true,
      compressionEnabled: false,
   };

   /**
    * Get or create a cache instance
    */
   getCache<T = any>(name: string, config?: Partial<CacheConfig>): AdvancedCache<T> {
      if (!this.caches.has(name)) {
         const cacheConfig = { ...this.defaultConfig, ...config };
         this.caches.set(name, new AdvancedCache<T>(cacheConfig));
      }
      return this.caches.get(name)! as AdvancedCache<T>;
   }

   /**
    * Get metrics for all caches
    */
   getAllMetrics(): Record<string, CacheMetrics> {
      const metrics: Record<string, CacheMetrics> = {};
      for (const [name, cache] of Array.from(this.caches.entries())) {
         metrics[name] = cache.getMetrics();
      }
      return metrics;
   }

   /**
    * Clear all caches
    */
   clearAll(): void {
      for (const cache of Array.from(this.caches.values())) {
         cache.clear();
      }
   }

   /**
    * Get cache statistics summary
    */
   getStatsSummary(): {
      totalCaches: number;
      totalItems: number;
      totalSize: number;
      averageHitRate: number;
      totalEvictions: number;
   } {
      const metrics = this.getAllMetrics();
      const cacheNames = Object.keys(metrics);
      
      const totalItems = cacheNames.reduce((sum, name) => sum + metrics[name].itemCount, 0);
      const totalSize = cacheNames.reduce((sum, name) => sum + metrics[name].totalSize, 0);
      const totalEvictions = cacheNames.reduce((sum, name) => sum + metrics[name].evictions, 0);
      const averageHitRate = cacheNames.length > 0 
         ? cacheNames.reduce((sum, name) => sum + metrics[name].hitRate, 0) / cacheNames.length
         : 0;

      return {
         totalCaches: cacheNames.length,
         totalItems,
         totalSize,
         averageHitRate,
         totalEvictions,
      };
   }
}

/**
 * Singleton cache manager instance
 */
let cacheManager: CacheManager | null = null;

export function getCacheManager(): CacheManager {
   if (!cacheManager) {
      cacheManager = new CacheManager();
   }
   return cacheManager;
}

/**
 * Predefined cache configurations for different data types
 */
export const CACHE_CONFIGS = {
   // Problems and questions - large cache, longer TTL
   PROBLEMS: {
      defaultTTL: 15 * 60 * 1000, // 15 minutes
      maxSize: 500, // 500 problems
      enablePersistence: true,
      compressionEnabled: true,
   },
   // Tags - small data, very long TTL
   TAGS: {
      defaultTTL: 60 * 60 * 1000, // 1 hour
      maxSize: 50, // 50 tag sets
      enablePersistence: true,
      compressionEnabled: false,
   },
   // User attempts - medium cache, short TTL
   USER_ATTEMPTS: {
      defaultTTL: 5 * 60 * 1000, // 5 minutes
      maxSize: 200, // 200 attempts
      enablePersistence: false, // Sensitive data
      compressionEnabled: false,
   },
   // API responses - medium cache, medium TTL
   API_RESPONSES: {
      defaultTTL: 10 * 60 * 1000, // 10 minutes
      maxSize: 100, // 100 responses
      enablePersistence: true,
      compressionEnabled: true,
   },
} as const;