/**
 * Bundle Analysis and Performance Tracking Utilities
 * 
 * Provides tools for analyzing bundle sizes, tracking performance metrics,
 * and generating performance reports for optimization insights.
 */

export interface BundleAnalysis {
   totalSize: number;
   gzippedSize: number;
   chunks: ChunkInfo[];
   largestAssets: AssetInfo[];
   duplicateModules: string[];
   recommendations: string[];
}

export interface ChunkInfo {
   name: string;
   size: number;
   gzippedSize: number;
   modules: string[];
   type: 'vendor' | 'common' | 'page' | 'feature';
}

export interface AssetInfo {
   name: string;
   size: number;
   type: 'js' | 'css' | 'image' | 'font' | 'other';
   gzippedSize?: number;
}

export interface PerformanceBudget {
   totalBundleSize: number; // KB
   individualChunkSize: number; // KB
   vendorChunkSize: number; // KB
   imageAssetSize: number; // KB
   fontAssetSize: number; // KB
}

export interface PerformanceReport {
   timestamp: Date;
   bundleAnalysis: BundleAnalysis;
   budget: PerformanceBudget;
   violations: BudgetViolation[];
   score: number; // 0-100
   trends: PerformanceTrend[];
}

export interface BudgetViolation {
   type: 'bundle' | 'chunk' | 'asset';
   item: string;
   currentSize: number;
   budgetSize: number;
   severity: 'warning' | 'error';
}

export interface PerformanceTrend {
   metric: string;
   current: number;
   previous: number;
   trend: 'improving' | 'degrading' | 'stable';
   changePercent: number;
}

/**
 * Default performance budgets for CompEx application
 */
export const DEFAULT_PERFORMANCE_BUDGET: PerformanceBudget = {
   totalBundleSize: 500, // 500 KB total
   individualChunkSize: 200, // 200 KB per chunk
   vendorChunkSize: 300, // 300 KB for vendor chunks
   imageAssetSize: 100, // 100 KB per image
   fontAssetSize: 50, // 50 KB per font file
};

/**
 * Performance analysis utility class
 */
export class PerformanceAnalyzer {
   private budget: PerformanceBudget;
   private previousReports: PerformanceReport[] = [];

   constructor(budget: PerformanceBudget = DEFAULT_PERFORMANCE_BUDGET) {
      this.budget = budget;
      this.loadPreviousReports();
   }

   /**
    * Analyze bundle performance from webpack stats
    */
   analyzeBundleStats(stats: any): BundleAnalysis {
      const assets = stats.assets || [];
      const chunks = stats.chunks || [];
      const modules = stats.modules || [];

      // Calculate total sizes
      const totalSize = assets.reduce((sum: number, asset: any) => sum + asset.size, 0);
      const gzippedSize = Math.round(totalSize * 0.3); // Approximate gzip compression

      // Analyze chunks
      const chunkInfos: ChunkInfo[] = chunks.map((chunk: any) => ({
         name: chunk.names?.[0] || chunk.id,
         size: chunk.size || 0,
         gzippedSize: Math.round((chunk.size || 0) * 0.3),
         modules: chunk.modules?.map((m: any) => m.name || m.identifier) || [],
         type: this.classifyChunk(chunk.names?.[0] || chunk.id),
      }));

      // Find largest assets
      const largestAssets: AssetInfo[] = assets
         .map((asset: any) => ({
            name: asset.name,
            size: asset.size,
            type: this.classifyAsset(asset.name),
            gzippedSize: Math.round(asset.size * 0.3),
         }))
         .sort((a: AssetInfo, b: AssetInfo) => b.size - a.size)
         .slice(0, 10);

      // Find duplicate modules
      const moduleNames = modules.map((m: any) => m.name || m.identifier);
      const duplicateModules = moduleNames.filter(
         (name: string, index: number) => 
            name && moduleNames.indexOf(name) !== index
      );

      // Generate recommendations
      const recommendations = this.generateRecommendations({
         totalSize,
         chunks: chunkInfos,
         largestAssets,
         duplicateModules,
      });

      return {
         totalSize,
         gzippedSize,
         chunks: chunkInfos,
         largestAssets,
         duplicateModules: Array.from(new Set(duplicateModules)),
         recommendations,
      };
   }

   /**
    * Classify chunk type based on name
    */
   private classifyChunk(chunkName: string): ChunkInfo['type'] {
      if (chunkName.includes('vendor') || chunkName.includes('node_modules')) {
         return 'vendor';
      }
      if (chunkName.includes('common') || chunkName.includes('shared')) {
         return 'common';
      }
      if (chunkName.includes('feature')) {
         return 'feature';
      }
      return 'page';
   }

   /**
    * Classify asset type based on file extension
    */
   private classifyAsset(assetName: string): AssetInfo['type'] {
      const ext = assetName.split('.').pop()?.toLowerCase();
      if (['js', 'mjs', 'jsx', 'ts', 'tsx'].includes(ext || '')) return 'js';
      if (['css', 'scss', 'sass', 'less'].includes(ext || '')) return 'css';
      if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'avif'].includes(ext || '')) return 'image';
      if (['woff', 'woff2', 'ttf', 'otf', 'eot'].includes(ext || '')) return 'font';
      return 'other';
   }

   /**
    * Generate optimization recommendations
    */
   private generateRecommendations(analysis: Partial<BundleAnalysis>): string[] {
      const recommendations: string[] = [];

      // Bundle size recommendations
      if ((analysis.totalSize || 0) > this.budget.totalBundleSize * 1024) {
         recommendations.push(
            `Total bundle size (${Math.round((analysis.totalSize || 0) / 1024)}KB) exceeds budget (${this.budget.totalBundleSize}KB). Consider code splitting.`
         );
      }

      // Large chunk recommendations
      analysis.chunks?.forEach(chunk => {
         if (chunk.size > this.budget.individualChunkSize * 1024) {
            recommendations.push(
               `Chunk "${chunk.name}" (${Math.round(chunk.size / 1024)}KB) is too large. Consider splitting.`
            );
         }
      });

      // Duplicate module recommendations
      if ((analysis.duplicateModules?.length || 0) > 0) {
         recommendations.push(
            `Found ${analysis.duplicateModules?.length} duplicate modules. Review chunk splitting strategy.`
         );
      }

      // Large asset recommendations
      analysis.largestAssets?.slice(0, 3).forEach(asset => {
         if (asset.type === 'image' && asset.size > this.budget.imageAssetSize * 1024) {
            recommendations.push(
               `Image "${asset.name}" (${Math.round(asset.size / 1024)}KB) should be optimized or lazy loaded.`
            );
         }
         if (asset.type === 'font' && asset.size > this.budget.fontAssetSize * 1024) {
            recommendations.push(
               `Font "${asset.name}" (${Math.round(asset.size / 1024)}KB) could be subset or preloaded.`
            );
         }
      });

      return recommendations;
   }

   /**
    * Check performance budget violations
    */
   checkBudgetViolations(analysis: BundleAnalysis): BudgetViolation[] {
      const violations: BudgetViolation[] = [];

      // Total bundle size
      if (analysis.totalSize > this.budget.totalBundleSize * 1024) {
         violations.push({
            type: 'bundle',
            item: 'Total Bundle',
            currentSize: analysis.totalSize,
            budgetSize: this.budget.totalBundleSize * 1024,
            severity: analysis.totalSize > this.budget.totalBundleSize * 1024 * 1.5 ? 'error' : 'warning',
         });
      }

      // Individual chunks
      analysis.chunks.forEach(chunk => {
         const budget = chunk.type === 'vendor' 
            ? this.budget.vendorChunkSize 
            : this.budget.individualChunkSize;
            
         if (chunk.size > budget * 1024) {
            violations.push({
               type: 'chunk',
               item: chunk.name,
               currentSize: chunk.size,
               budgetSize: budget * 1024,
               severity: chunk.size > budget * 1024 * 1.5 ? 'error' : 'warning',
            });
         }
      });

      // Large assets
      analysis.largestAssets.forEach(asset => {
         let budget = 0;
         if (asset.type === 'image') budget = this.budget.imageAssetSize;
         if (asset.type === 'font') budget = this.budget.fontAssetSize;
         
         if (budget > 0 && asset.size > budget * 1024) {
            violations.push({
               type: 'asset',
               item: asset.name,
               currentSize: asset.size,
               budgetSize: budget * 1024,
               severity: asset.size > budget * 1024 * 2 ? 'error' : 'warning',
            });
         }
      });

      return violations;
   }

   /**
    * Calculate performance score (0-100)
    */
   calculatePerformanceScore(analysis: BundleAnalysis, violations: BudgetViolation[]): number {
      let score = 100;

      // Deduct points for violations
      violations.forEach(violation => {
         const deduction = violation.severity === 'error' ? 20 : 10;
         score -= deduction;
      });

      // Deduct points for large bundle
      if (analysis.totalSize > this.budget.totalBundleSize * 1024) {
         const excess = (analysis.totalSize - this.budget.totalBundleSize * 1024) / (this.budget.totalBundleSize * 1024);
         score -= Math.min(30, excess * 50);
      }

      // Deduct points for duplicates
      if (analysis.duplicateModules.length > 0) {
         score -= Math.min(20, analysis.duplicateModules.length * 2);
      }

      return Math.max(0, Math.round(score));
   }

   /**
    * Generate comprehensive performance report
    */
   generateReport(bundleAnalysis: BundleAnalysis): PerformanceReport {
      const violations = this.checkBudgetViolations(bundleAnalysis);
      const score = this.calculatePerformanceScore(bundleAnalysis, violations);
      const trends = this.calculateTrends(bundleAnalysis);

      const report: PerformanceReport = {
         timestamp: new Date(),
         bundleAnalysis,
         budget: this.budget,
         violations,
         score,
         trends,
      };

      this.previousReports.push(report);
      this.savePreviousReports();

      return report;
   }

   /**
    * Calculate performance trends compared to previous reports
    */
   private calculateTrends(currentAnalysis: BundleAnalysis): PerformanceTrend[] {
      if (this.previousReports.length === 0) return [];

      const previousAnalysis = this.previousReports[this.previousReports.length - 1]?.bundleAnalysis;
      if (!previousAnalysis) return [];

      const trends: PerformanceTrend[] = [];

      // Bundle size trend
      const bundleTrend = this.calculateTrend(
         'Bundle Size',
         currentAnalysis.totalSize,
         previousAnalysis.totalSize
      );
      trends.push(bundleTrend);

      // Chunk count trend
      const chunkCountTrend = this.calculateTrend(
         'Chunk Count',
         currentAnalysis.chunks.length,
         previousAnalysis.chunks.length
      );
      trends.push(chunkCountTrend);

      return trends;
   }

   /**
    * Calculate individual trend
    */
   private calculateTrend(metric: string, current: number, previous: number): PerformanceTrend {
      const changePercent = previous === 0 ? 0 : ((current - previous) / previous) * 100;
      let trend: PerformanceTrend['trend'] = 'stable';

      if (Math.abs(changePercent) > 5) {
         trend = changePercent > 0 ? 'degrading' : 'improving';
      }

      return {
         metric,
         current,
         previous,
         trend,
         changePercent: Math.round(changePercent * 100) / 100,
      };
   }

   /**
    * Load previous reports from storage
    */
   private loadPreviousReports() {
      try {
         if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('compex-performance-reports');
            if (stored) {
               this.previousReports = JSON.parse(stored);
            }
         }
      } catch (error) {
         console.warn('Failed to load previous performance reports:', error);
      }
   }

   /**
    * Save reports to storage
    */
   private savePreviousReports() {
      try {
         if (typeof window !== 'undefined') {
            // Keep only last 10 reports
            const reportsToSave = this.previousReports.slice(-10);
            localStorage.setItem('compex-performance-reports', JSON.stringify(reportsToSave));
         }
      } catch (error) {
         console.warn('Failed to save performance reports:', error);
      }
   }
}

/**
 * Create a singleton performance analyzer
 */
let performanceAnalyzer: PerformanceAnalyzer | null = null;

export function getPerformanceAnalyzer(): PerformanceAnalyzer {
   if (!performanceAnalyzer) {
      performanceAnalyzer = new PerformanceAnalyzer();
   }
   return performanceAnalyzer;
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes: number): string {
   if (bytes === 0) return '0 B';
   const k = 1024;
   const sizes = ['B', 'KB', 'MB', 'GB'];
   const i = Math.floor(Math.log(bytes) / Math.log(k));
   return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}