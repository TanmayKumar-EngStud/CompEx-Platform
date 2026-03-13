import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * Version checking API endpoint
 * Returns current build information for cache invalidation
 */

interface BuildInfo {
  buildTime: string;
  buildTimestamp: number;
  version: string;
  environment: string;
  gitCommit: string;
  gitBranch: string;
}

export async function GET(request: NextRequest) {
  try {
    // Try to read from public/build-info.json first
    const publicBuildInfoPath = path.join(process.cwd(), 'public', 'build-info.json');
    
    let buildInfo: BuildInfo;
    
    if (fs.existsSync(publicBuildInfoPath)) {
      const buildInfoContent = fs.readFileSync(publicBuildInfoPath, 'utf-8');
      buildInfo = JSON.parse(buildInfoContent);
    } else {
      // Fallback: generate current build info if file doesn't exist
      buildInfo = {
        buildTime: new Date().toISOString(),
        buildTimestamp: Date.now(),
        version: process.env.npm_package_version || '1.0.0',
        environment: process.env.NODE_ENV || 'development',
        gitCommit: process.env.VERCEL_GIT_COMMIT_SHA || 'local-dev',
        gitBranch: process.env.VERCEL_GIT_COMMIT_REF || 'local'
      };
    }

    // Add cache control headers to prevent caching of this endpoint
    const response = NextResponse.json({
      success: true,
      data: buildInfo,
      timestamp: Date.now()
    });

    // Prevent caching of this endpoint to always get fresh version info
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    response.headers.set('Surrogate-Control', 'no-store');

    return response;

  } catch (error) {
    console.error('Error reading build info:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to read build information',
      data: {
        buildTime: new Date().toISOString(),
        buildTimestamp: Date.now(),
        version: 'unknown',
        environment: process.env.NODE_ENV || 'development',
        gitCommit: 'unknown',
        gitBranch: 'unknown'
      },
      timestamp: Date.now()
    }, { 
      status: 500,
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
  }
}

// Also support POST for flexibility
export async function POST(request: NextRequest) {
  return GET(request);
}