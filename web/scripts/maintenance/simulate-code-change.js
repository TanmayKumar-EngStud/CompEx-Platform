#!/usr/bin/env node

/**
 * Simulate code change by updating build info
 * This script helps test the cache invalidation system
 */

const fs = require('fs');
const path = require('path');

// Paths
const publicBuildInfoPath = path.join(__dirname, '..', 'public', 'build-info.json');
const libBuildInfoPath = path.join(__dirname, '..', 'shared', 'lib', 'build-info.ts');

// Generate new build info
const newBuildInfo = {
  buildTime: new Date().toISOString(),
  buildTimestamp: Date.now(),
  version: process.env.npm_package_version || '1.0.0',
  environment: process.env.NODE_ENV || 'development',
  gitCommit: process.env.VERCEL_GIT_COMMIT_SHA || `local-dev-${Date.now().toString(36)}`,
  gitBranch: process.env.VERCEL_GIT_COMMIT_REF || 'local'
};

// TypeScript content
const tsContent = `// This file is auto-generated. Do not edit manually.
export interface BuildInfo {
  buildTime: string;
  buildTimestamp: number;
  version: string;
  environment: string;
  gitCommit: string;
  gitBranch: string;
}

export const buildInfo: BuildInfo = ${JSON.stringify(newBuildInfo, null, 2)};

export default buildInfo;
`;

try {
  // Write JSON file
  fs.writeFileSync(publicBuildInfoPath, JSON.stringify(newBuildInfo, null, 2));
  console.log('✅ Updated public/build-info.json');

  // Write TypeScript file
  fs.writeFileSync(libBuildInfoPath, tsContent);
  console.log('✅ Updated shared/lib/build-info.ts');

  console.log('🔄 Simulated code change:');
  console.log('   New timestamp:', newBuildInfo.buildTimestamp);
  console.log('   Build time:', newBuildInfo.buildTime);
  console.log('   Git commit:', newBuildInfo.gitCommit);
  console.log('');
  console.log('🕒 Cache validation will detect this change within 30 seconds');
  console.log('💡 You should see a notification in the browser if the page is open');

} catch (error) {
  console.error('❌ Error simulating code change:', error.message);
  process.exit(1);
}