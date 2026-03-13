#!/usr/bin/env tsx

/**
 * Bundle Analysis Script
 * 
 * Analyzes the Next.js bundle for performance insights and optimization opportunities.
 * Run with: npx tsx scripts/analyze-bundle.ts
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { PerformanceAnalyzer, formatFileSize } from '../shared/lib/performance/bundle-analyzer';

interface BuildStats {
   bundleSize: number;
   chunkCount: number;
   largestChunks: Array<{ name: string; size: number }>;
   buildTime: number;
}

/**
 * Run Next.js build and capture statistics
 */
async function runBuildAnalysis(): Promise<BuildStats> {
   console.log('🔧 Building Next.js application for analysis...');
   
   const startTime = Date.now();
   
   try {
      // Build the application with bundle analysis
      const buildOutput = execSync('pnpm build', { 
         encoding: 'utf-8',
         cwd: process.cwd(),
         env: { ...process.env, ANALYZE: 'false' } // Don't open browser
      });
      
      const buildTime = Date.now() - startTime;
      
      console.log('✅ Build completed successfully');
      console.log(`⏱️  Build time: ${buildTime}ms`);
      
      // Parse build output for bundle information
      const bundleInfo = parseBuildOutput(buildOutput);
      
      return {
         ...bundleInfo,
         buildTime,
      };
   } catch (error) {
      console.error('❌ Build failed:', error);
      throw error;
   }
}

/**
 * Parse Next.js build output for bundle information
 */
function parseBuildOutput(buildOutput: string): Omit<BuildStats, 'buildTime'> {
   const lines = buildOutput.split('\n');
   let bundleSize = 0;
   let chunkCount = 0;
   const largestChunks: Array<{ name: string; size: number }> = [];
   
   // Look for route information in build output
   let inRouteSection = false;
   
   for (const line of lines) {
      if (line.includes('Route (app)') || line.includes('Size') || line.includes('First Load JS')) {
         inRouteSection = true;
         continue;
      }
      
      if (inRouteSection && line.trim().startsWith('├') || line.trim().startsWith('└')) {
         chunkCount++;
         
         // Extract size information
         const sizeMatch = line.match(/(\d+(?:\.\d+)?)\s*kB/);
         if (sizeMatch) {
            const size = parseFloat(sizeMatch[1]) * 1024; // Convert KB to bytes
            bundleSize += size;
            
            // Extract route name
            const routeMatch = line.match(/[├└]\s*[ƒ○]\s*([^\s]+)/);
            if (routeMatch) {
               largestChunks.push({
                  name: routeMatch[1],
                  size,
               });
            }
         }
      }
      
      if (line.includes('+ First Load JS shared by all')) {
         inRouteSection = false;
      }
   }
   
   // Sort chunks by size
   largestChunks.sort((a, b) => b.size - a.size);
   
   return {
      bundleSize,
      chunkCount,
      largestChunks: largestChunks.slice(0, 10), // Top 10
   };
}

/**
 * Analyze webpack stats if available
 */
function analyzeWebpackStats(): any {
   const statsPath = join(process.cwd(), '.next', 'webpack-stats.json');
   
   if (existsSync(statsPath)) {
      try {
         const stats = JSON.parse(readFileSync(statsPath, 'utf-8'));
         return stats;
      } catch (error) {
         console.warn('⚠️  Failed to parse webpack stats:', error);
      }
   }
   
   return null;
}

/**
 * Generate performance recommendations
 */
function generateRecommendations(stats: BuildStats): string[] {
   const recommendations: string[] = [];
   
   // Bundle size recommendations
   if (stats.bundleSize > 500 * 1024) { // 500KB
      recommendations.push(
         `Bundle size (${formatFileSize(stats.bundleSize)}) exceeds recommended 500KB. Consider code splitting.`
      );
   }
   
   // Chunk count recommendations
   if (stats.chunkCount > 20) {
      recommendations.push(
         `High chunk count (${stats.chunkCount}). Consider consolidating smaller chunks.`
      );
   } else if (stats.chunkCount < 5) {
      recommendations.push(
         `Low chunk count (${stats.chunkCount}). Consider more aggressive code splitting.`
      );
   }
   
   // Large chunk recommendations
   stats.largestChunks.slice(0, 3).forEach(chunk => {
      if (chunk.size > 200 * 1024) { // 200KB
         recommendations.push(
            `Large chunk detected: ${chunk.name} (${formatFileSize(chunk.size)}). Consider splitting.`
         );
      }
   });
   
   // Build time recommendations
   if (stats.buildTime > 60000) { // 1 minute
      recommendations.push(
         `Build time (${Math.round(stats.buildTime / 1000)}s) is slow. Consider build optimizations.`
      );
   }
   
   return recommendations;
}

/**
 * Save analysis results
 */
function saveAnalysisResults(stats: BuildStats, recommendations: string[]) {
   const results = {
      timestamp: new Date().toISOString(),
      bundleSize: stats.bundleSize,
      chunkCount: stats.chunkCount,
      largestChunks: stats.largestChunks,
      buildTime: stats.buildTime,
      recommendations,
      performance: {
         bundleSizeScore: Math.max(0, 100 - Math.max(0, (stats.bundleSize - 500 * 1024) / (500 * 1024) * 100)),
         chunkCountScore: stats.chunkCount <= 20 ? 100 : Math.max(0, 100 - (stats.chunkCount - 20) * 5),
         buildTimeScore: Math.max(0, 100 - Math.max(0, (stats.buildTime - 30000) / 30000 * 100)),
      },
   };
   
   // Save to file
   const outputPath = join(process.cwd(), 'performance-analysis.json');
   writeFileSync(outputPath, JSON.stringify(results, null, 2));
   
   console.log(`📊 Analysis results saved to: ${outputPath}`);
   
   return results;
}

/**
 * Main analysis function
 */
async function main() {
   console.log('🚀 Starting CompEx Bundle Analysis\n');
   
   try {
      // Step 1: Build and analyze
      const buildStats = await runBuildAnalysis();
      
      // Step 2: Analyze webpack stats if available
      const webpackStats = analyzeWebpackStats();
      
      // Step 3: Generate recommendations
      const recommendations = generateRecommendations(buildStats);
      
      // Step 4: Enhanced analysis with webpack stats
      if (webpackStats) {
         console.log('📈 Analyzing webpack statistics...');
         const analyzer = new PerformanceAnalyzer();
         const bundleAnalysis = analyzer.analyzeBundleStats(webpackStats);
         console.log('✅ Webpack analysis completed');
      }
      
      // Step 5: Display results
      console.log(`\n${'='.repeat(50)}`);
      console.log('📊 BUNDLE ANALYSIS RESULTS');
      console.log(`${'='.repeat(50)}`);
      
      console.log(`📦 Total Bundle Size: ${formatFileSize(buildStats.bundleSize)}`);
      console.log(`📚 Chunk Count: ${buildStats.chunkCount}`);
      console.log(`⏱️  Build Time: ${Math.round(buildStats.buildTime / 1000)}s`);
      
      console.log('\n🏆 Largest Chunks:');
      buildStats.largestChunks.slice(0, 5).forEach((chunk, index) => {
         console.log(`  ${index + 1}. ${chunk.name}: ${formatFileSize(chunk.size)}`);
      });
      
      if (recommendations.length > 0) {
         console.log('\n💡 Recommendations:');
         recommendations.forEach((rec, index) => {
            console.log(`  ${index + 1}. ${rec}`);
         });
      } else {
         console.log('\n✅ No optimization recommendations - bundle looks good!');
      }
      
      // Step 6: Save results
      const results = saveAnalysisResults(buildStats, recommendations);
      
      // Step 7: Performance scores
      console.log(`\n${'='.repeat(50)}`);
      console.log('🎯 PERFORMANCE SCORES');
      console.log(`${'='.repeat(50)}`);
      console.log(`Bundle Size Score: ${Math.round(results.performance.bundleSizeScore)}/100`);
      console.log(`Chunk Count Score: ${Math.round(results.performance.chunkCountScore)}/100`);
      console.log(`Build Time Score: ${Math.round(results.performance.buildTimeScore)}/100`);
      
      const overallScore = Math.round(
         (results.performance.bundleSizeScore + 
          results.performance.chunkCountScore + 
          results.performance.buildTimeScore) / 3
      );
      console.log(`\n🎯 Overall Performance Score: ${overallScore}/100`);
      
      // Step 8: Bundle analyzer recommendation
      console.log(`\n${'='.repeat(50)}`);
      console.log('🔍 ADVANCED ANALYSIS');
      console.log(`${'='.repeat(50)}`);
      console.log('For detailed bundle analysis, run:');
      console.log('  ANALYZE=true pnpm build');
      console.log('\nThis will open the webpack bundle analyzer in your browser.');
      
      console.log('\n🎉 Bundle analysis completed!');
      
      // Exit with appropriate code
      const hasWarnings = recommendations.length > 0;
      const hasErrors = overallScore < 70;
      
      if (hasErrors) {
         console.log('\n❌ Performance issues detected - see recommendations above');
         process.exit(1);
      } else if (hasWarnings) {
         console.log('\n⚠️  Minor optimization opportunities available');
         process.exit(0);
      } else {
         console.log('\n✅ Bundle performance is excellent!');
         process.exit(0);
      }
      
   } catch (error) {
      console.error('💥 Bundle analysis failed:', error);
      process.exit(1);
   }
}

// Run the analysis
main().catch(error => {
   console.error('💥 Fatal error:', error);
   process.exit(1);
});