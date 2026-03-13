'use client';

import { useEffect, useRef, useState } from 'react';

interface BuildInfo {
  buildTimestamp: number;
  version: string;
  environment: string;
  buildTime?: string;
  gitCommit?: string;
  gitBranch?: string;
}

interface VersionResponse {
  success: boolean;
  data: BuildInfo;
  timestamp: number;
  error?: string;
}

interface CacheValidationOptions {
  checkInterval?: number; // in milliseconds, default 30000 (30 seconds)
  enableAutoReload?: boolean; // default false
  onUpdateDetected?: (newVersion: BuildInfo, currentVersion: BuildInfo | null) => void;
}

export function useTimerCacheValidation(options: CacheValidationOptions = {}) {
  const {
    checkInterval = 30000,
    enableAutoReload = false,
    onUpdateDetected
  } = options;

  const [currentVersion, setCurrentVersion] = useState<BuildInfo | null>(null);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastCheckRef = useRef<number>(0);

  // Initialize current version
  useEffect(() => {
    const initializeVersion = async () => {
      try {
        const storedVersion = localStorage.getItem('app-build-info');
        if (storedVersion) {
          setCurrentVersion(JSON.parse(storedVersion));
        }
        await checkForUpdates();
      } catch (error) {
        console.warn('Failed to initialize version check:', error);
      }
    };

    initializeVersion();
  }, []);

  const checkForUpdates = async (): Promise<boolean> => {
    // Prevent rapid successive calls
    const now = Date.now();

    // Skip checking in development mode to prevent server flooding during startup
    if (process.env.NODE_ENV === 'development') {
      return false;
    }

    if (now - lastCheckRef.current < 5000) {
      return false;
    }
    lastCheckRef.current = now;

    try {
      setIsChecking(true);

      // Use cache busting to ensure fresh data
      const response = await fetch(`/api/version?t=${now}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const versionResponse: VersionResponse = await response.json();

      // Validate the response structure
      if (!versionResponse.success || !versionResponse.data) {
        throw new Error('Invalid version response structure');
      }

      const newVersion = versionResponse.data;

      // Ensure we have required fields
      if (!newVersion.buildTimestamp || !newVersion.version) {
        throw new Error('Missing required version fields');
      }

      const hasUpdate = currentVersion &&
        newVersion.buildTimestamp > currentVersion.buildTimestamp;

      if (hasUpdate) {
        setIsUpdateAvailable(true);
        onUpdateDetected?.(newVersion, currentVersion);

        if (enableAutoReload) {
          await clearCacheAndReload();
          return true;
        }
      }

      // Update stored version
      if (!currentVersion || newVersion.buildTimestamp !== currentVersion.buildTimestamp) {
        setCurrentVersion(newVersion);
        localStorage.setItem('app-build-info', JSON.stringify(newVersion));
      }

      return hasUpdate || false;
    } catch (error) {
      console.warn('Version check failed:', error);
      return false;
    } finally {
      setIsChecking(false);
    }
  };

  const clearCacheAndReload = async () => {
    try {
      // Clear all storage
      localStorage.clear();
      sessionStorage.clear();

      // Clear React Query cache if available
      if (typeof window !== 'undefined' && (window as any).queryClient) {
        (window as any).queryClient.clear();
      }

      // Clear service worker cache if available
      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (const registration of registrations) {
          await registration.unregister();
        }
      }

      // Clear browser cache if possible
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(name => caches.delete(name))
        );
      }

      // Reload with cache bypass
      window.location.reload();
    } catch (error) {
      console.warn('Failed to clear cache:', error);
      // Fallback to simple reload
      window.location.reload();
    }
  };

  const manualUpdate = async () => {
    setIsUpdateAvailable(false);
    await clearCacheAndReload();
  };

  const dismissUpdate = () => {
    setIsUpdateAvailable(false);
  };

  // Start/stop timer based on visibility
  useEffect(() => {
    const startTimer = () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      intervalRef.current = setInterval(() => {
        checkForUpdates();
      }, checkInterval);
    };

    const stopTimer = () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopTimer();
      } else {
        startTimer();
        // Check immediately when tab becomes visible
        setTimeout(checkForUpdates, 1000);
      }
    };

    // Start timer immediately
    startTimer();

    // Listen for visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      stopTimer();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [checkInterval]);

  return {
    currentVersion,
    isUpdateAvailable,
    isChecking,
    checkForUpdates,
    manualUpdate,
    dismissUpdate,
    clearCacheAndReload
  };
}