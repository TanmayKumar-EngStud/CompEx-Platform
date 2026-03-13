"use client";

import React, { createContext, useContext, useState } from 'react';
import dynamic from 'next/dynamic';
import { useCacheInvalidation } from '@/shared/hooks/use-cache-invalidation';

// Dynamically import notification components
const UpdateNotification = dynamic(
  () => import('@/shared/components/feedback/update-notification').then(mod => ({ default: mod.UpdateNotification })),
  { ssr: false }
);

const CompactUpdateNotification = dynamic(
  () => import('@/shared/components/feedback/update-notification').then(mod => ({ default: mod.CompactUpdateNotification })),
  { ssr: false }
);

interface CacheInvalidationContextType {
  updateAvailable: boolean;
  isChecking: boolean;
  lastChecked: number | null;
  error: string | null;
  checkForUpdates: () => void;
  invalidateAndReload: () => void;
  resetUpdateState: () => void;
}

const CacheInvalidationContext = createContext<CacheInvalidationContextType | null>(null);

export function useCacheInvalidationContext() {
  const context = useContext(CacheInvalidationContext);
  if (!context) {
    throw new Error('useCacheInvalidationContext must be used within CacheInvalidationProvider');
  }
  return context;
}

interface CacheInvalidationProviderProps {
  children: React.ReactNode;
  /** Check interval in milliseconds (default: 30 seconds) */
  checkInterval?: number;
  /** Show compact notification instead of full one */
  compactNotification?: boolean;
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Cache Invalidation Provider
 * 
 * Provides automatic cache invalidation functionality across the application
 * Shows update notifications when new versions are detected
 */
export function CacheInvalidationProvider({
  children,
  checkInterval = 30000, // 30 seconds
  compactNotification = false,
  debug = false
}: CacheInvalidationProviderProps) {
  const [notificationDismissed, setNotificationDismissed] = useState(false);

  const cacheInvalidation = useCacheInvalidation({
    checkInterval,
    autoReload: false, // Let user control reload
    showNotification: false, // We'll handle notifications with our UI
    debug
  });

  const {
    updateAvailable,
    isChecking,
    lastChecked,
    error,
    currentBuild,
    checkForUpdates,
    invalidateAndReload,
    resetUpdateState
  } = cacheInvalidation;

  const handleRefresh = () => {
    // Reset notification state
    setNotificationDismissed(false);
    resetUpdateState();
    
    // Invalidate cache and reload
    invalidateAndReload();
  };

  const handleDismiss = () => {
    setNotificationDismissed(true);
    resetUpdateState();
  };

  const showNotification = updateAvailable && !notificationDismissed;

  // Context value
  const contextValue: CacheInvalidationContextType = {
    updateAvailable,
    isChecking,
    lastChecked,
    error,
    checkForUpdates,
    invalidateAndReload,
    resetUpdateState
  };

  return (
    <CacheInvalidationContext.Provider value={contextValue}>
      {children}
      
      {/* Update Notifications */}
      {compactNotification ? (
        <CompactUpdateNotification
          visible={showNotification}
          onRefresh={handleRefresh}
          onDismiss={handleDismiss}
        />
      ) : (
        <UpdateNotification
          visible={showNotification}
          onRefresh={handleRefresh}
          onDismiss={handleDismiss}
          buildInfo={currentBuild ? {
            version: currentBuild.version,
            buildTime: currentBuild.buildTime
          } : null}
        />
      )}
      
      {/* Debug Info (Development Only) */}
      {debug && process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 left-4 bg-black/80 text-white p-2 rounded text-xs z-[10000]">
          <div>Cache Invalidation Debug:</div>
          <div>Checking: {isChecking ? 'Yes' : 'No'}</div>
          <div>Update Available: {updateAvailable ? 'Yes' : 'No'}</div>
          <div>Last Checked: {lastChecked ? new Date(lastChecked).toLocaleTimeString() : 'Never'}</div>
          {error && <div className="text-red-400">Error: {error}</div>}
          {currentBuild && (
            <div>
              <div>Version: {currentBuild.version}</div>
              <div>Build: {new Date(currentBuild.buildTime).toLocaleTimeString()}</div>
            </div>
          )}
          <button
            onClick={checkForUpdates}
            className="bg-blue-600 px-2 py-1 rounded mt-1 text-xs"
          >
            Check Now
          </button>
        </div>
      )}
    </CacheInvalidationContext.Provider>
  );
}

/**
 * Hook to manually trigger cache invalidation from any component
 */
export function useManualCacheInvalidation() {
  const { invalidateAndReload } = useCacheInvalidationContext();
  return invalidateAndReload;
}

/**
 * Hook to get cache invalidation status
 */
export function useCacheInvalidationStatus() {
  const { updateAvailable, isChecking, lastChecked, error } = useCacheInvalidationContext();
  return { updateAvailable, isChecking, lastChecked, error };
}