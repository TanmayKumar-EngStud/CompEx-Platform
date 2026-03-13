/**
 * Database Performance Monitoring Utility
 * 
 * Provides tools for monitoring database query performance,
 * analyzing slow queries, and optimizing database operations.
 */

import { PrismaClient } from '@prisma/client';

export interface QueryPerformanceMetric {
   query: string;
   duration: number;
   timestamp: Date;
   parameters?: any;
   rowsAffected?: number;
   operation: 'SELECT' | 'INSERT' | 'UPDATE' | 'DELETE';
}

export interface DatabaseStats {
   totalQueries: number;
   averageQueryTime: number;
   slowQueries: QueryPerformanceMetric[];
   queryDistribution: Record<string, number>;
   indexUsage: IndexUsageStats[];
}

export interface IndexUsageStats {
   tableName: string;
   indexName: string;
   scanCount: number;
   tupleReads: number;
   efficiency: number;
}

/**
 * Database performance monitoring class
 */
export class DatabasePerformanceMonitor {
   private metrics: QueryPerformanceMetric[] = [];
   private slowQueryThreshold: number = 1000; // 1 second
   private enabled: boolean = process.env.NODE_ENV === 'development';

   constructor(private prisma: PrismaClient, slowQueryThreshold?: number) {
      if (slowQueryThreshold) {
         this.slowQueryThreshold = slowQueryThreshold;
      }
      this.setupQueryLogging();
   }

   /**
    * Enable or disable performance monitoring
    */
   setEnabled(enabled: boolean) {
      this.enabled = enabled;
   }

   /**
    * Set the threshold for slow query detection (in milliseconds)
    */
   setSlowQueryThreshold(threshold: number) {
      this.slowQueryThreshold = threshold;
   }

   /**
    * Setup query logging middleware
    */
   private setupQueryLogging() {
      if (!this.enabled) return;

      // Note: Advanced query monitoring would be implemented here
      // For now, we'll use a simplified approach focusing on the analytics endpoints
      console.log('Database performance monitoring initialized (simplified mode)');
      
      // TODO: Implement Prisma middleware for comprehensive query monitoring
      // This would require setting up Prisma middleware in the actual database connection
   }

   /**
    * Record a query performance metric
    */
   recordQuery(
      operation: QueryPerformanceMetric['operation'],
      query: any,
      duration: number,
      parameters?: any[],
      hasError: boolean = false
   ) {
      if (!this.enabled) return;

      const metric: QueryPerformanceMetric = {
         query: query?.toString() || 'Unknown query',
         duration,
         timestamp: new Date(),
         parameters,
         operation,
      };

      this.metrics.push(metric);

      // Keep only last 1000 metrics to prevent memory leaks
      if (this.metrics.length > 1000) {
         this.metrics = this.metrics.slice(-1000);
      }

      // Log slow queries immediately
      if (duration > this.slowQueryThreshold) {
         console.warn(`🐌 Slow Query Detected (${duration}ms):`, {
            query: metric.query.substring(0, 200) + (metric.query.length > 200 ? '...' : ''),
            duration,
            operation,
            hasError,
         });
      }
   }

   /**
    * Get operation type from SQL query
    */
   getOperationType(query: string): QueryPerformanceMetric['operation'] {
      const normalizedQuery = query.trim().toUpperCase();
      if (normalizedQuery.startsWith('SELECT')) return 'SELECT';
      if (normalizedQuery.startsWith('INSERT')) return 'INSERT';
      if (normalizedQuery.startsWith('UPDATE')) return 'UPDATE';
      if (normalizedQuery.startsWith('DELETE')) return 'DELETE';
      return 'SELECT'; // Default fallback
   }

   /**
    * Get comprehensive database performance statistics
    */
   getPerformanceStats(): DatabaseStats {
      if (this.metrics.length === 0) {
         return {
            totalQueries: 0,
            averageQueryTime: 0,
            slowQueries: [],
            queryDistribution: {},
            indexUsage: [],
         };
      }

      const totalQueries = this.metrics.length;
      const totalTime = this.metrics.reduce((sum, metric) => sum + metric.duration, 0);
      const averageQueryTime = totalTime / totalQueries;

      const slowQueries = this.metrics
         .filter(metric => metric.duration > this.slowQueryThreshold)
         .sort((a, b) => b.duration - a.duration)
         .slice(0, 10); // Top 10 slowest queries

      const queryDistribution = this.metrics.reduce((dist, metric) => {
         dist[metric.operation] = (dist[metric.operation] || 0) + 1;
         return dist;
      }, {} as Record<string, number>);

      return {
         totalQueries,
         averageQueryTime,
         slowQueries,
         queryDistribution,
         indexUsage: [], // This would require actual database statistics query
      };
   }

   /**
    * Get index usage statistics from PostgreSQL
    */
   async getIndexUsageStats(): Promise<IndexUsageStats[]> {
      if (!this.enabled) return [];

      try {
         const indexStats = await this.prisma.$queryRaw<any[]>`
            SELECT 
               schemaname,
               tablename,
               indexname,
               idx_scan as scan_count,
               idx_tup_read as tuple_reads,
               CASE 
                  WHEN idx_scan = 0 THEN 0
                  ELSE round((idx_tup_read::numeric / idx_scan), 2)
               END as efficiency
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC, idx_tup_read DESC;
         `;

         return indexStats.map(stat => ({
            tableName: stat.tablename,
            indexName: stat.indexname,
            scanCount: parseInt(stat.scan_count) || 0,
            tupleReads: parseInt(stat.tuple_reads) || 0,
            efficiency: parseFloat(stat.efficiency) || 0,
         }));
      } catch (error) {
         console.warn('Failed to get index usage stats:', error);
         return [];
      }
   }

   /**
    * Get table size statistics
    */
   async getTableSizes(): Promise<Array<{ tableName: string; size: string; rowCount: number }>> {
      if (!this.enabled) return [];

      try {
         const tableSizes = await this.prisma.$queryRaw<any[]>`
            SELECT 
               tablename,
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
               (xpath('/row/count/text()', xml_count))[1]::text::int as row_count
            FROM (
               SELECT 
                  schemaname, tablename,
                  query_to_xml(format('select count(*) from %I.%I', schemaname, tablename), false, true, '') as xml_count
               FROM pg_tables 
               WHERE schemaname = 'public'
            ) t
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
         `;

         return tableSizes.map(table => ({
            tableName: table.tablename,
            size: table.size,
            rowCount: table.row_count || 0,
         }));
      } catch (error) {
         console.warn('Failed to get table sizes:', error);
         return [];
      }
   }

   /**
    * Analyze query patterns and suggest optimizations
    */
   analyzeQueryPatterns(): Array<{ issue: string; suggestion: string; queries: string[] }> {
      const issues: Array<{ issue: string; suggestion: string; queries: string[] }> = [];

      // Analyze for missing indexes
      const slowSelectQueries = this.metrics
         .filter(m => m.operation === 'SELECT' && m.duration > this.slowQueryThreshold)
         .map(m => m.query);

      if (slowSelectQueries.length > 0) {
         issues.push({
            issue: 'Slow SELECT queries detected',
            suggestion: 'Consider adding indexes for frequently filtered columns',
            queries: slowSelectQueries.slice(0, 3),
         });
      }

      // Analyze for N+1 query patterns
      const queryFrequency = this.metrics.reduce((freq, metric) => {
         const normalizedQuery = metric.query.replace(/\d+/g, '?').replace(/'[^']*'/g, '?');
         freq[normalizedQuery] = (freq[normalizedQuery] || 0) + 1;
         return freq;
      }, {} as Record<string, number>);

      const frequentQueries = Object.entries(queryFrequency)
         .filter(([_, count]) => count > 10)
         .sort(([_, a], [__, b]) => b - a);

      if (frequentQueries.length > 0) {
         issues.push({
            issue: 'Repetitive queries detected (possible N+1 pattern)',
            suggestion: 'Consider using database joins or query batching',
            queries: frequentQueries.slice(0, 3).map(([query]) => query),
         });
      }

      return issues;
   }

   /**
    * Clear collected metrics
    */
   clearMetrics() {
      this.metrics = [];
   }

   /**
    * Export metrics for external analysis
    */
   exportMetrics(): QueryPerformanceMetric[] {
      return [...this.metrics];
   }
}

/**
 * Create a singleton instance of the performance monitor
 */
let performanceMonitor: DatabasePerformanceMonitor | null = null;

export function createDatabasePerformanceMonitor(prisma: PrismaClient): DatabasePerformanceMonitor {
   if (!performanceMonitor) {
      performanceMonitor = new DatabasePerformanceMonitor(prisma);
   }
   return performanceMonitor;
}

/**
 * Get the existing performance monitor instance
 */
export function getDatabasePerformanceMonitor(): DatabasePerformanceMonitor | null {
   return performanceMonitor;
}