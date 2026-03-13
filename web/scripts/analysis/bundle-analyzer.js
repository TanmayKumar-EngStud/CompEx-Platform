#!/usr/bin/env node

/**
 * Simple bundle analyzer to identify heavy dependencies
 */

const fs = require('fs');
const path = require('path');

function analyzeNodeModules() {
  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  
  if (!fs.existsSync(nodeModulesPath)) {
    console.log('No node_modules found');
    return;
  }

  const packages = [];
  
  // Get direct dependencies from package.json
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8')
  );
  
  const dependencies = {
    ...packageJson.dependencies,
    ...packageJson.devDependencies
  };

  Object.keys(dependencies).forEach(dep => {
    const depPath = path.join(nodeModulesPath, dep);
    
    if (fs.existsSync(depPath)) {
      try {
        const stats = fs.statSync(depPath);
        const size = getDirSize(depPath);
        
        packages.push({
          name: dep,
          size: size,
          sizeFormatted: formatBytes(size)
        });
      } catch (err) {
        // Skip if can't read
      }
    }
  });

  // Sort by size
  packages.sort((a, b) => b.size - a.size);

  console.log('\n📦 Bundle Size Analysis\n');
  console.log('Top 15 Largest Dependencies:');
  console.log('════════════════════════════════════════════════════════════');
  
  packages.slice(0, 15).forEach((pkg, i) => {
    console.log(`${(i + 1).toString().padStart(2)}. ${pkg.name.padEnd(30)} ${pkg.sizeFormatted.padStart(10)}`);
  });

  console.log('\n💡 Optimization Suggestions:');
  console.log('────────────────────────────────────────────────────────────');
  
  // Check for specific heavy libraries
  const heavyLibs = packages.filter(p => p.size > 1000000); // > 1MB
  
  heavyLibs.forEach(lib => {
    if (lib.name.includes('react-katex') || lib.name.includes('katex')) {
      console.log(`• Consider lazy loading ${lib.name} (${lib.sizeFormatted}) - only load when math content is present`);
    }
    if (lib.name.includes('framer-motion')) {
      console.log(`• Consider replacing ${lib.name} (${lib.sizeFormatted}) with CSS animations for simple cases`);
    }
    if (lib.name.includes('recharts')) {
      console.log(`• Consider lazy loading ${lib.name} (${lib.sizeFormatted}) - only load on charts page`);
    }
    if (lib.name.includes('@radix-ui')) {
      console.log(`• ${lib.name} (${lib.sizeFormatted}) - consider importing only used components`);
    }
  });

  console.log('\n🚀 Quick Wins:');
  console.log('────────────────────────────────────────────────────────────');
  console.log('• Use dynamic imports for heavy components');
  console.log('• Enable tree shaking in next.config.js');
  console.log('• Split vendor bundles by library type');
  console.log('• Use bundle analyzer: npm run analyze');
  
  const totalSize = packages.reduce((sum, pkg) => sum + pkg.size, 0);
  console.log(`\nTotal analyzed size: ${formatBytes(totalSize)}`);
}

function getDirSize(dirPath) {
  let size = 0;
  
  try {
    const files = fs.readdirSync(dirPath);
    
    files.forEach(file => {
      const filePath = path.join(dirPath, file);
      const stats = fs.statSync(filePath);
      
      if (stats.isDirectory()) {
        size += getDirSize(filePath);
      } else {
        size += stats.size;
      }
    });
  } catch (err) {
    // Skip if can't read
  }
  
  return size;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Run the analysis
analyzeNodeModules();