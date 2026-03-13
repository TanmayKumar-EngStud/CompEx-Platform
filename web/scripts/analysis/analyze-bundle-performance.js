/**
 * Bundle Performance Analysis Script
 * 
 * Analyzes the current build output and compares against performance targets
 * Part of CHECKPOINT 6: Testing & Performance Validation
 */

const fs = require('fs');
const path = require('path');

// Performance targets from ROADMAP.md
const PERFORMANCE_TARGETS = {
  pageLoadTime: 3000, // 3 seconds
  bundleSizes: {
    'main-app.js': 1 * 1024 * 1024,      // 1MB (currently 1.29MB)
    'page.js': 2 * 1024 * 1024,          // 2MB (currently 2.78MB)  
    'layout.js': 500 * 1024,             // 500KB (currently 517KB)
  },
  memoryReduction: 0.5, // 50% reduction target
};

// Function to get file size
function getFileSize(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch (error) {
    return 0;
  }
}

// Function to find files matching pattern
function findFiles(directory, pattern) {
  const files = [];
  
  function searchDirectory(dir) {
    try {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          searchDirectory(fullPath);
        } else if (pattern.test(item)) {
          files.push({
            name: item,
            path: fullPath,
            size: stat.size,
          });
        }
      }
    } catch (error) {
      // Directory doesn't exist or can't be read
    }
  }
  
  searchDirectory(directory);
  return files;
}

// Function to format bytes
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Function to calculate improvement percentage
function calculateImprovement(current, target) {
  if (target >= current) {
    return `✅ ${formatBytes(current)} (target: ${formatBytes(target)})`;
  } else {
    const excess = current - target;
    const excessPercent = ((excess / target) * 100).toFixed(1);
    return `❌ ${formatBytes(current)} (${excessPercent}% over target: ${formatBytes(target)})`;
  }
}

function analyzeBundlePerformance() {
  console.log('🔍 Bundle Performance Analysis');
  console.log('=====================================\n');

  const buildDir = path.join(process.cwd(), '.next');
  const staticDir = path.join(buildDir, 'static/chunks');
  
  if (!fs.existsSync(staticDir)) {
    console.log('❌ Build directory not found. Please run "pnpm build" first.\n');
    return;
  }

  // Find and analyze specific bundle files
  console.log('📦 Bundle Size Analysis:');
  console.log('------------------------');

  // Analyze main app chunks
  const vendorsFiles = findFiles(staticDir, /vendors-.*\.js$/);
  const mainAppFiles = findFiles(staticDir, /main-app-.*\.js$/);
  const pageFiles = findFiles(staticDir, /app\/dashboard\/problems\/page-.*\.js$/);
  const layoutFiles = findFiles(staticDir, /app\/layout-.*\.js$/);

  let totalMainApp = 0;
  let totalPage = 0;
  let totalLayout = 0;

  // Vendors chunk (shared by all)
  if (vendorsFiles.length > 0) {
    const vendorsSize = vendorsFiles[0].size;
    console.log(`Vendors chunk: ${formatBytes(vendorsSize)}`);
    totalMainApp += vendorsSize;
    totalPage += vendorsSize;
    totalLayout += vendorsSize;
  }

  // Main app specific
  if (mainAppFiles.length > 0) {
    const mainAppSize = mainAppFiles[0].size;
    console.log(`Main app chunk: ${formatBytes(mainAppSize)}`);
    totalMainApp += mainAppSize;
  }

  // Problems page specific
  if (pageFiles.length > 0) {
    const pageSize = pageFiles[0].size;
    console.log(`Problems page chunk: ${formatBytes(pageSize)}`);
    totalPage += pageSize;
  }

  // Layout specific
  if (layoutFiles.length > 0) {
    const layoutSize = layoutFiles[0].size;
    console.log(`Layout chunk: ${formatBytes(layoutSize)}`);
    totalLayout += layoutSize;
  }

  console.log('\n📊 Bundle Size vs Targets:');
  console.log('---------------------------');
  console.log(`Main App Total: ${calculateImprovement(totalMainApp, PERFORMANCE_TARGETS.bundleSizes['main-app.js'])}`);
  console.log(`Problems Page Total: ${calculateImprovement(totalPage, PERFORMANCE_TARGETS.bundleSizes['page.js'])}`);
  console.log(`Layout Total: ${calculateImprovement(totalLayout, PERFORMANCE_TARGETS.bundleSizes['layout.js'])}`);

  // Analyze largest files
  console.log('\n🏋️ Largest Bundle Files:');
  console.log('------------------------');
  
  const allFiles = findFiles(staticDir, /\.js$/);
  const sortedFiles = allFiles.sort((a, b) => b.size - a.size).slice(0, 10);
  
  sortedFiles.forEach((file, index) => {
    console.log(`${index + 1}. ${file.name}: ${formatBytes(file.size)}`);
  });

  // Memory usage analysis
  console.log('\n💾 Memory Usage Estimation:');
  console.log('---------------------------');
  
  // Estimate based on bundle sizes (rough approximation)
  const estimatedMemoryUsage = totalPage * 2; // Rough estimate: 2x bundle size in memory
  const targetMemoryUsage = PERFORMANCE_TARGETS.bundleSizes['page.js'] * (1 - PERFORMANCE_TARGETS.memoryReduction);
  
  console.log(`Estimated Memory Usage: ${formatBytes(estimatedMemoryUsage)}`);
  console.log(`Target Memory Reduction: ${formatBytes(targetMemoryUsage)} (${(PERFORMANCE_TARGETS.memoryReduction * 100)}% reduction)`);
  
  if (estimatedMemoryUsage <= targetMemoryUsage) {
    console.log('✅ Memory usage target achieved');
  } else {
    const excessMemory = estimatedMemoryUsage - targetMemoryUsage;
    console.log(`❌ Memory usage ${formatBytes(excessMemory)} above target`);
  }

  // Recommendations
  console.log('\n💡 Optimization Recommendations:');
  console.log('----------------------------------');
  
  const recommendations = [];
  
  if (totalPage > PERFORMANCE_TARGETS.bundleSizes['page.js']) {
    recommendations.push('• Consider lazy loading heavy components in problems page');
    recommendations.push('• Implement code splitting for question templates');
    recommendations.push('• Move large libraries to dynamic imports');
  }
  
  if (totalMainApp > PERFORMANCE_TARGETS.bundleSizes['main-app.js']) {
    recommendations.push('• Analyze vendor bundle for unnecessary dependencies');
    recommendations.push('• Implement tree shaking for unused code');
  }
  
  if (vendorsFiles.length > 0 && vendorsFiles[0].size > 500 * 1024) {
    recommendations.push('• Split vendor bundle into smaller chunks');
    recommendations.push('• Consider removing heavy dependencies like chart libraries');
  }
  
  if (recommendations.length === 0) {
    console.log('✅ Bundle sizes are within acceptable ranges');
  } else {
    recommendations.forEach(rec => console.log(rec));
  }

  // Performance score
  console.log('\n🎯 Performance Score:');
  console.log('---------------------');
  
  let score = 0;
  const maxScore = 100;
  
  // Bundle size scores (60% of total)
  const bundleScore = Math.max(0, 60 - (
    (Math.max(0, totalMainApp - PERFORMANCE_TARGETS.bundleSizes['main-app.js']) / PERFORMANCE_TARGETS.bundleSizes['main-app.js']) * 20 +
    (Math.max(0, totalPage - PERFORMANCE_TARGETS.bundleSizes['page.js']) / PERFORMANCE_TARGETS.bundleSizes['page.js']) * 30 +
    (Math.max(0, totalLayout - PERFORMANCE_TARGETS.bundleSizes['layout.js']) / PERFORMANCE_TARGETS.bundleSizes['layout.js']) * 10
  ));
  
  // Memory score (40% of total)
  const memoryScore = Math.max(0, 40 - (
    Math.max(0, estimatedMemoryUsage - targetMemoryUsage) / targetMemoryUsage * 40
  ));
  
  score = Math.round(bundleScore + memoryScore);
  
  console.log(`Bundle Performance Score: ${score}/${maxScore}`);
  
  if (score >= 90) {
    console.log('🏆 Excellent performance!');
  } else if (score >= 70) {
    console.log('✅ Good performance');
  } else if (score >= 50) {
    console.log('⚠️ Needs improvement');
  } else {
    console.log('❌ Poor performance - immediate action required');
  }

  console.log('\n' + '='.repeat(50));
  console.log('Analysis complete. See recommendations above for next steps.');
}

// Run the analysis
if (require.main === module) {
  analyzeBundlePerformance();
}

module.exports = { analyzeBundlePerformance };