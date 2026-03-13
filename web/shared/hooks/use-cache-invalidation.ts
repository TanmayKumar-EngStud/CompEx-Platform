"use client";

import { useEffect, useRef, useCallback, useState } from 'react';

interface BuildInfo {
  buildTime: string;
  buildTimestamp: number;
  version: string;
  environment: string;
  gitCommit: string;
  gitBranch: string;
}

interface VersionResponse {
  success: boolean;
  data: BuildInfo;
  timestamp: number;
  error?: string;
}

interface CacheInvalidationOptions {
  /** Check interval in milliseconds (default: 30 seconds) */
  checkInterval?: number;
  /** Enable automatic reload on update detection (default: false) */
  autoReload?: boolean;
  /** Show notification when update is available (default: true) */
  showNotification?: boolean;
  /** Enable debug logging (default: false) */
  debug?: boolean;
}

interface CacheInvalidationState {
  /** Current build information */
  currentBuild: BuildInfo | null;
  /** Whether an update is available */
  updateAvailable: boolean;
  /** Whether currently checking for updates */
  isChecking: boolean;
  /** Last check timestamp */
  lastChecked: number | null;
  /** Error message if check failed */
  error: string | null;
}

/**
 * Hook for automatic cache invalidation based on build timestamp changes
 * 
 * Features:
 * - Periodically checks for code updates
 * - Compares build timestamps to detect changes
 * - Provides update notifications
 * - Optional automatic reload
 * - React Query cache invalidation
 * 
 * @param options Configuration options
 * @returns Cache invalidation state and control functions
 */
export function useCacheInvalidation(options: CacheInvalidationOptions = {}) {
  const {
    checkInterval = 30000, // 30 seconds
    autoReload = false,
    showNotification = true,
    debug = false
  } = options;

  const [state, setState] = useState<CacheInvalidationState>({
    currentBuild: null,
    updateAvailable: false,
    isChecking: false,
    lastChecked: null,
    error: null
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const initialBuildRef = useRef<BuildInfo | null>(null);
  const notificationShownRef = useRef(false);

  const log = useCallback((message: string, ...args: any[]) => {
    if (debug) {
      console.log(`[CacheInvalidation] ${message}`, ...args);
    }
  }, [debug]);

  /**
   * Check for version updates
   */
  const checkForUpdates = useCallback(async () => {
    setState(prev => ({ ...prev, isChecking: true, error: null }));

    // Skip checking in development mode to prevent server flooding during startup
    if (process.env.NODE_ENV === 'development') {
      log('Update check skipped in development mode');
      setState(prev => ({ ...prev, isChecking: false }));
      return;
    }

    log('Checking for updates...');

    try {
      const response = await fetch('/api/version', {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch version: ${response.status}`);
      }

      const versionData: VersionResponse = await response.json();

      if (!versionData.success) {
        throw new Error(versionData.error || 'Failed to get version info');
      }

      const newBuild = versionData.data;
      log('Received version data:', newBuild);

      // Initialize on first check
      if (!initialBuildRef.current) {
        initialBuildRef.current = newBuild;
        setState(prev => ({
          ...prev,
          currentBuild: newBuild,
          lastChecked: Date.now(),
          isChecking: false
        }));
        log('Initial build info saved:', newBuild);
        return;
      }

      // Compare timestamps to detect updates
      const hasUpdate = initialBuildRef.current.buildTimestamp !== newBuild.buildTimestamp;

      if (hasUpdate) {
        log('Update detected!', {
          old: initialBuildRef.current.buildTimestamp,
          new: newBuild.buildTimestamp
        });

        setState(prev => ({
          ...prev,
          currentBuild: newBuild,
          updateAvailable: true,
          lastChecked: Date.now(),
          isChecking: false
        }));

        // Show notification if enabled and not already shown
        if (showNotification && !notificationShownRef.current) {
          showUpdateNotification();
          notificationShownRef.current = true;
        }

        // Auto-reload if enabled
        if (autoReload) {
          log('Auto-reloading due to update...');
          setTimeout(() => {
            window.location.reload();
          }, 1000); // Small delay for user to see notification
        }

      } else {
        setState(prev => ({
          ...prev,
          currentBuild: newBuild,
          lastChecked: Date.now(),
          isChecking: false
        }));
        log('No update detected');
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log('Error checking for updates:', errorMessage);

      setState(prev => ({
        ...prev,
        error: errorMessage,
        lastChecked: Date.now(),
        isChecking: false
      }));
    }
  }, [autoReload, showNotification, log]);

  /**
   * Show update notification to user
   */
  const showUpdateNotification = useCallback(() => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('CompEx Update Available', {
        body: 'A new version is available. Refresh to get the latest features.',
        icon: '/favicon.ico'
      });
    } else {
      // Fallback to console notification
      console.log('🔄 CompEx Update Available: A new version is ready. Refresh to get the latest features.');
    }
  }, []);

  /**
   * Manually trigger cache invalidation and reload
   */
  const invalidateAndReload = useCallback(() => {
    log('Manual cache invalidation triggered');

    // Clear all localStorage
    try {
      localStorage.clear();
      log('localStorage cleared');
    } catch (e) {
      log('Failed to clear localStorage:', e);
    }

    // Clear sessionStorage
    try {
      sessionStorage.clear();
      log('sessionStorage cleared');
    } catch (e) {
      log('Failed to clear sessionStorage:', e);
    }

    // Invalidate React Query cache if available
    if (typeof window !== 'undefined' && (window as any).queryClient) {
      (window as any).queryClient.invalidateQueries();
      log('React Query cache invalidated');
    }

    // Force reload with cache bust
    window.location.href = window.location.href + '?cache_bust=' + Date.now();
  }, [log]);

  /**
   * Manually check for updates
   */
  const checkManually = useCallback(() => {
    log('Manual update check triggered');
    checkForUpdates();
  }, [checkForUpdates]);

  /**
   * Reset update state (after user has acknowledged)
   */
  const resetUpdateState = useCallback(() => {
    setState(prev => ({ ...prev, updateAvailable: false }));
    notificationShownRef.current = false;
    log('Update state reset');
  }, [log]);

  // Set up periodic checking
  useEffect(() => {
    // Initial check
    checkForUpdates();

    // Set up interval
    if (checkInterval > 0) {
      intervalRef.current = setInterval(checkForUpdates, checkInterval);
      log(`Update checking enabled with ${checkInterval}ms interval`);
    }

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        log('Update checking stopped');
      }
    };
  }, [checkForUpdates, checkInterval, log]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    ...state,
    checkForUpdates: checkManually,
    invalidateAndReload,
    resetUpdateState
  };
}