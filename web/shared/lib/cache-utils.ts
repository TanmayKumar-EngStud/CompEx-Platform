/**
 * Cache utilities for automatic invalidation
 * Integrates with React Query and browser caches
 */

/**
 * Clear all application caches
 */
export async function clearAllCaches(): Promise<void> {
  const promises: Promise<any>[] = [];

  // Clear localStorage
  try {
    localStorage.clear();
    console.log('✅ localStorage cleared');
  } catch (error) {
    console.warn('⚠️ Failed to clear localStorage:', error);
  }

  // Clear sessionStorage
  try {
    sessionStorage.clear();
    console.log('✅ sessionStorage cleared');
  } catch (error) {
    console.warn('⚠️ Failed to clear sessionStorage:', error);
  }

  // Clear React Query cache if available
  try {
    if (typeof window !== 'undefined' && (window as any).queryClient) {
      await (window as any).queryClient.clear();
      console.log('✅ React Query cache cleared');
    }
  } catch (error) {
    console.warn('⚠️ Failed to clear React Query cache:', error);
  }

  // Clear Service Worker caches
  if ('caches' in window) {
    try {
      const cacheNames = await caches.keys();
      const deletionPromises = cacheNames.map(cacheName => caches.delete(cacheName));
      promises.push(...deletionPromises);
      console.log(`✅ Clearing ${cacheNames.length} service worker caches`);
    } catch (error) {
      console.warn('⚠️ Failed to clear service worker caches:', error);
    }
  }

  // Clear IndexedDB (if you're using it)
  try {
    if ('indexedDB' in window) {
      // Note: This is a basic implementation. You might need to customize
      // based on your specific IndexedDB usage
      const databases = await indexedDB.databases?.();
      if (databases) {
        for (const db of databases) {
          if (db.name) {
            const deleteReq = indexedDB.deleteDatabase(db.name);
            promises.push(new Promise((resolve, reject) => {
              deleteReq.onsuccess = () => resolve(void 0);
              deleteReq.onerror = () => reject(deleteReq.error);
            }));
          }
        }
        console.log(`✅ Clearing ${databases.length} IndexedDB databases`);
      }
    }
  } catch (error) {
    console.warn('⚠️ Failed to clear IndexedDB:', error);
  }

  // Wait for all cache clearing operations to complete
  await Promise.allSettled(promises);
}

/**
 * Invalidate React Query cache for specific queries
 */
export function invalidateQueries(queryKeys?: string[]): void {
  try {
    if (typeof window !== 'undefined' && (window as any).queryClient) {
      const queryClient = (window as any).queryClient;
      
      if (queryKeys && queryKeys.length > 0) {
        // Invalidate specific queries
        queryKeys.forEach(key => {
          queryClient.invalidateQueries({ queryKey: [key] });
        });
        console.log('✅ Invalidated specific React Query caches:', queryKeys);
      } else {
        // Invalidate all queries
        queryClient.invalidateQueries();
        console.log('✅ Invalidated all React Query caches');
      }
    }
  } catch (error) {
    console.warn('⚠️ Failed to invalidate React Query cache:', error);
  }
}

/**
 * Force reload the page with cache busting
 */
export function forceReload(): void {
  try {
    // Add cache bust parameter to force complete reload
    const cacheBustParam = `cache_bust=${Date.now()}`;
    const separator = window.location.search ? '&' : '?';
    const newUrl = `${window.location.pathname}${window.location.search}${separator}${cacheBustParam}`;
    
    window.location.href = newUrl;
  } catch (error) {
    // Fallback to regular reload
    console.warn('⚠️ Failed to force reload with cache bust, falling back to regular reload:', error);
    window.location.reload();
  }
}

/**
 * Soft reload - try to refresh without losing too much state
 */
export function softReload(): void {
  try {
    // First try to invalidate caches without full page reload
    invalidateQueries();
    
    // Then trigger a navigation to the same page
    if (typeof window !== 'undefined' && window.history) {
      window.history.go(0);
    } else {
      window.location.reload();
    }
  } catch (error) {
    console.warn('⚠️ Soft reload failed, falling back to hard reload:', error);
    forceReload();
  }
}

/**
 * Check if page needs refresh based on build timestamp
 */
export async function checkIfRefreshNeeded(lastKnownBuildTime?: number): Promise<boolean> {
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
    
    const versionData = await response.json();
    
    if (!versionData.success || !versionData.data) {
      throw new Error('Invalid version response');
    }
    
    const currentBuildTime = versionData.data.buildTimestamp;
    
    // If we have a last known build time, compare
    if (lastKnownBuildTime && currentBuildTime !== lastKnownBuildTime) {
      console.log('🔄 Build timestamp changed:', {
        old: lastKnownBuildTime,
        new: currentBuildTime
      });
      return true;
    }
    
    return false;
  } catch (error) {
    console.warn('⚠️ Failed to check if refresh needed:', error);
    return false;
  }
}

/**
 * Get current build information
 */
export async function getBuildInfo(): Promise<any> {
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
    
    const versionData = await response.json();
    
    if (!versionData.success) {
      throw new Error(versionData.error || 'Failed to get build info');
    }
    
    return versionData.data;
  } catch (error) {
    console.warn('⚠️ Failed to get build info:', error);
    return null;
  }
}

/**
 * Set up automatic cache invalidation
 * This function can be called from the main app to set up periodic checks
 */
export function setupAutoCacheInvalidation(options: {
  checkInterval?: number;
  onUpdateDetected?: () => void;
  debug?: boolean;
} = {}): () => void {
  const { 
    checkInterval = 30000, // 30 seconds
    onUpdateDetected,
    debug = false
  } = options;

  let lastKnownBuildTime: number | null = null;
  let intervalId: NodeJS.Timeout | null = null;

  const log = (message: string, ...args: any[]) => {
    if (debug) {
      console.log(`[AutoCacheInvalidation] ${message}`, ...args);
    }
  };

  const checkForUpdates = async () => {
    try {
      log('Checking for updates...');
      
      const buildInfo = await getBuildInfo();
      if (!buildInfo) {
        log('No build info available');
        return;
      }

      const currentBuildTime = buildInfo.buildTimestamp;
      
      if (lastKnownBuildTime === null) {
        // First time, just store the current time
        lastKnownBuildTime = currentBuildTime;
        log('Initial build time set:', currentBuildTime);
        return;
      }

      if (currentBuildTime !== lastKnownBuildTime) {
        log('Update detected!', {
          old: lastKnownBuildTime,
          new: currentBuildTime
        });
        
        // Update detected
        if (onUpdateDetected) {
          onUpdateDetected();
        } else {
          // Default behavior: show notification and reload
          if (confirm('A new version is available. Refresh now?')) {
            await clearAllCaches();
            forceReload();
          }
        }
        
        lastKnownBuildTime = currentBuildTime;
      } else {
        log('No update detected');
      }
    } catch (error) {
      log('Error checking for updates:', error);
    }
  };

  // Start checking
  checkForUpdates(); // Initial check
  intervalId = setInterval(checkForUpdates, checkInterval);

  log(`Auto cache invalidation started with ${checkInterval}ms interval`);

  // Return cleanup function
  return () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
      log('Auto cache invalidation stopped');
    }
  };
}