"use client";

import React, { useEffect, useState, useRef } from 'react';

interface BuildInfo {
  buildTime: string;
  buildTimestamp: number;
  version: string;
  environment: string;
  gitCommit: string;
  gitBranch: string;
}

interface SimpleCacheInvalidationProviderProps {
  children: React.ReactNode;
  checkInterval?: number;
  debug?: boolean;
}

/**
 * Simple Cache Invalidation Provider
 * A more robust implementation that avoids webpack bundling issues
 */
export function SimpleCacheInvalidationProvider({
  children,
  checkInterval = 60000, // 1 minute instead of 30 seconds
  debug = false
}: SimpleCacheInvalidationProviderProps) {
  const [initialBuildTime, setInitialBuildTime] = useState<number | null>(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const log = (message: string, ...args: any[]) => {
    if (debug) {
      console.log(`[SimpleCacheInvalidation] ${message}`, ...args);
    }
  };

  const checkForUpdates = async () => {
    if (!mountedRef.current) return;

    // Skip checking in development mode to prevent server flooding during startup
    if (process.env.NODE_ENV === 'development') {
      return;
    }

    setIsChecking(true);

    try {
      const response = await fetch('/api/version', {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });

      if (!response.ok) {
        throw new Error(`Version check failed: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success || !data.data) {
        throw new Error('Invalid version response');
      }

      const currentBuildTime = data.data.buildTimestamp;

      if (initialBuildTime === null) {
        // First check - store initial build time
        setInitialBuildTime(currentBuildTime);
        log('Initial build time stored:', currentBuildTime);
      } else if (currentBuildTime !== initialBuildTime) {
        // Update detected
        log('Update detected!', { old: initialBuildTime, new: currentBuildTime });
        setUpdateAvailable(true);

        // Show simple notification
        if (confirm('A new version is available. Refresh the page?')) {
          window.location.reload();
        } else {
          // User declined, don't check again for this session
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        }
      }
    } catch (error) {
      log('Error checking for updates:', error);
    } finally {
      if (mountedRef.current) {
        setIsChecking(false);
      }
    }
  };

  useEffect(() => {
    // Initial check after a delay to ensure app is loaded
    const initialTimeout = setTimeout(() => {
      if (mountedRef.current) {
        checkForUpdates();
      }
    }, 5000); // 5 second delay

    // Set up interval for periodic checks
    intervalRef.current = setInterval(() => {
      if (mountedRef.current && !updateAvailable) {
        checkForUpdates();
      }
    }, checkInterval);

    log(`Simple cache invalidation started with ${checkInterval}ms interval`);

    return () => {
      clearTimeout(initialTimeout);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      mountedRef.current = false;
      log('Simple cache invalidation stopped');
    };
  }, [checkInterval, updateAvailable]);

  return (
    <>
      {children}

      {/* Debug Info */}
      {debug && process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 left-4 bg-black/80 text-white p-2 rounded text-xs z-[10000] max-w-xs">
          <div className="font-bold">Simple Cache Debug:</div>
          <div>Checking: {isChecking ? 'Yes' : 'No'}</div>
          <div>Update Available: {updateAvailable ? 'Yes' : 'No'}</div>
          <div>Initial Build: {initialBuildTime || 'Not Set'}</div>
          <button
            onClick={checkForUpdates}
            className="bg-blue-600 px-2 py-1 rounded mt-1 text-xs"
            disabled={isChecking}
          >
            {isChecking ? 'Checking...' : 'Check Now'}
          </button>
        </div>
      )}
    </>
  );
}