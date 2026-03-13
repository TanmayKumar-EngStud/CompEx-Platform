#!/usr/bin/env tsx

/**
 * Database Optimization Script
 * 
 * Applies performance indexes and optimizations to the CompEx database
 * Run with: npx tsx scripts/optimize-database.ts
 */

import { PrismaClient } from '@prisma/client';
import { readFileSync } from 'fs';
import { join } from 'path';

const prisma = new PrismaClient();

interface OptimizationResult {
   success: boolean;
   message: string;
   duration?: number;
   error?: string;
}

/**
 * Apply database indexes from migration file
 */
async function applyPerformanceIndexes(): Promise<OptimizationResult> {
   console.log('🔧 Applying performance indexes...');

   try {
      const migrationPath = join(process.cwd(), 'prisma', 'migrations', '20241217_performance_indexes', 'migration.sql');

      const { existsSync } = require('fs');
      if (!existsSync(migrationPath)) {
         console.warn('⚠️  Migration file for performance indexes not found. Skipping applyPerformanceIndexes.');
         return {
            success: true,
            message: 'Performance indexes migration file not found, skipping.',
         };
      }

      const migrationSQL = readFileSync(migrationPath, 'utf-8');

      const startTime = Date.now();

      // Split by semicolon and execute each statement
      const statements = migrationSQL
         .split(';')
         .map(stmt => stmt.trim())
         .filter(stmt => stmt && !stmt.startsWith('--'));

      console.log(`📊 Executing ${statements.length} optimization statements...`);

      for (const statement of statements) {
         if (statement.toUpperCase().includes('CREATE INDEX')) {
            const indexName = statement.match(/CREATE INDEX (?:IF NOT EXISTS )?(\w+)/)?.[1];
            console.log(`  ➡️  Creating index: ${indexName || 'unnamed'}`);
         }

         await prisma.$executeRawUnsafe(statement);
      }

      const duration = Date.now() - startTime;

      return {
         success: true,
         message: `Successfully applied ${statements.length} optimization statements`,
         duration,
      };
   } catch (error) {
      return {
         success: false,
         message: 'Failed to apply performance indexes',
         error: error instanceof Error ? error.message : String(error),
      };
   }
}

/**
 * Analyze current database performance
 */
async function analyzeDatabase(): Promise<OptimizationResult> {
   console.log('📈 Analyzing database performance...');

   try {
      // Get table sizes
      const tableSizes = await prisma.$queryRaw<any[]>`
         SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
         FROM pg_tables 
         WHERE schemaname = 'public'
         ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
      `;

      console.log('\n📊 Table Sizes:');
      tableSizes.forEach(table => {
         console.log(`  ${table.tablename}: ${table.size}`);
      });

      // Get index usage stats
      const indexStats = await prisma.$queryRaw<any[]>`
         SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as scan_count,
            idx_tup_read as tuple_reads
         FROM pg_stat_user_indexes 
         WHERE schemaname = 'public'
         ORDER BY idx_scan DESC
         LIMIT 10;
      `;

      console.log('\n🔍 Top Index Usage:');
      indexStats.forEach(index => {
         console.log(`  ${index.tablename}.${index.indexname}: ${index.scan_count} scans, ${index.tuple_reads} tuple reads`);
      });

      // Get slow query insights
      const queryStats = await prisma.$queryRaw<any[]>`
         SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
         FROM pg_stat_statements 
         WHERE query NOT LIKE '%pg_stat_statements%'
         ORDER BY mean_time DESC
         LIMIT 5;
      `;

      if (queryStats.length > 0) {
         console.log('\n🐌 Slowest Queries (if pg_stat_statements enabled):');
         queryStats.forEach(query => {
            console.log(`  Mean time: ${Math.round(query.mean_time)}ms, Calls: ${query.calls}`);
            console.log(`    ${query.query.substring(0, 100)}...`);
         });
      }

      return {
         success: true,
         message: 'Database analysis completed',
      };
   } catch (error) {
      return {
         success: false,
         message: 'Failed to analyze database',
         error: error instanceof Error ? error.message : String(error),
      };
   }
}

/**
 * Update table statistics for better query planning
 */
async function updateStatistics(): Promise<OptimizationResult> {
   console.log('📊 Updating table statistics...');

   try {
      const tables = ['problems', 'userattempts', 'problemtags', 'tags', 'ProblemsSet', 'sections', 'users'];

      for (const table of tables) {
         console.log(`  ➡️  Analyzing table: ${table}`);
         await prisma.$executeRawUnsafe(`ANALYZE ${table};`);
      }

      return {
         success: true,
         message: `Updated statistics for ${tables.length} tables`,
      };
   } catch (error) {
      return {
         success: false,
         message: 'Failed to update statistics',
         error: error instanceof Error ? error.message : String(error),
      };
   }
}

/**
 * Check for missing indexes on foreign keys
 */
async function checkMissingIndexes(): Promise<OptimizationResult> {
   console.log('🔍 Checking for missing indexes...');

   try {
      const missingIndexes = await prisma.$queryRaw<any[]>`
         SELECT 
            conrelid::regclass AS table_name,
            conname AS constraint_name,
            pg_get_constraintdef(c.oid) AS constraint_definition
         FROM pg_constraint c
         LEFT JOIN pg_index i ON i.indrelid = c.conrelid 
            AND (i.indkey::smallint[])[0] = ANY(c.conkey)
         WHERE c.contype = 'f' 
            AND i.indrelid IS NULL
            AND conrelid::regclass::text LIKE '%'
         ORDER BY conrelid::regclass;
      `;

      if (missingIndexes.length > 0) {
         console.log('\n⚠️  Missing indexes on foreign keys:');
         missingIndexes.forEach(missing => {
            console.log(`  ${missing.table_name}: ${missing.constraint_name}`);
         });
      } else {
         console.log('✅ All foreign keys have appropriate indexes');
      }

      return {
         success: true,
         message: `Found ${missingIndexes.length} missing foreign key indexes`,
      };
   } catch (error) {
      return {
         success: false,
         message: 'Failed to check missing indexes',
         error: error instanceof Error ? error.message : String(error),
      };
   }
}

/**
 * Main optimization function
 */
async function main() {
   console.log('🚀 Starting CompEx Database Optimization\n');

   const operations = [
      { name: 'Apply Performance Indexes', fn: applyPerformanceIndexes },
      { name: 'Update Table Statistics', fn: updateStatistics },
      { name: 'Check Missing Indexes', fn: checkMissingIndexes },
      { name: 'Analyze Database', fn: analyzeDatabase },
   ];

   const results: Array<{ operation: string; result: OptimizationResult }> = [];

   for (const operation of operations) {
      console.log(`\n${'='.repeat(50)}`);
      console.log(`🔧 ${operation.name}`);
      console.log(`${'='.repeat(50)}`);

      try {
         const result = await operation.fn();
         results.push({ operation: operation.name, result });

         if (result.success) {
            console.log(`✅ ${result.message}`);
            if (result.duration) {
               console.log(`⏱️  Completed in ${result.duration}ms`);
            }
         } else {
            console.error(`❌ ${result.message}`);
            if (result.error) {
               console.error(`   Error: ${result.error}`);
            }
         }
      } catch (error) {
         console.error(`❌ Unexpected error in ${operation.name}:`, error);
         results.push({
            operation: operation.name,
            result: {
               success: false,
               message: 'Unexpected error',
               error: error instanceof Error ? error.message : String(error)
            }
         });
      }
   }

   // Summary
   console.log(`\n${'='.repeat(50)}`);
   console.log('📋 OPTIMIZATION SUMMARY');
   console.log(`${'='.repeat(50)}`);

   const successful = results.filter(r => r.result.success).length;
   const failed = results.filter(r => !r.result.success).length;

   console.log(`✅ Successful operations: ${successful}`);
   console.log(`❌ Failed operations: ${failed}`);

   if (failed > 0) {
      console.log('\n❌ Failed Operations:');
      results
         .filter(r => !r.result.success)
         .forEach(({ operation, result }) => {
            console.log(`  • ${operation}: ${result.message}`);
         });
   }

   console.log('\n🎉 Database optimization completed!');

   // Performance recommendations
   console.log(`\n${'='.repeat(50)}`);
   console.log('💡 PERFORMANCE RECOMMENDATIONS');
   console.log(`${'='.repeat(50)}`);
   console.log('1. Monitor slow queries using Web Vitals tracking');
   console.log('2. Regularly run ANALYZE on frequently updated tables');
   console.log('3. Consider partitioning large tables (userattempts, problems)');
   console.log('4. Enable pg_stat_statements for query performance monitoring');
   console.log('5. Set up connection pooling for production workloads');

   await prisma.$disconnect();
   process.exit(failed > 0 ? 1 : 0);
}

// Run the optimization
main().catch(error => {
   console.error('💥 Fatal error:', error);
   process.exit(1);
});