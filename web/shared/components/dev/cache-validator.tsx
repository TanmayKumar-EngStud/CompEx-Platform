'use client';

import { useTimerCacheValidation } from '@/shared/hooks/use-timer-cache-validation';
import { useEffect, useState } from 'react';

interface CacheValidatorProps {
  /** Check interval in milliseconds (default: 30 seconds) */
  interval?: number;
  /** Enable automatic reload when updates are detected (default: false) */
  autoReload?: boolean;
  /** Only show in development mode (default: true) */
  devOnly?: boolean;
}

export function CacheValidator({ 
  interval = 30000, 
  autoReload = false,
  devOnly = true 
}: CacheValidatorProps) {
  const [showNotification, setShowNotification] = useState(false);
  
  // Only run in development mode if devOnly is true
  if (devOnly && process.env.NODE_ENV !== 'development') {
    return null;
  }

  const {
    currentVersion,
    isUpdateAvailable,
    isChecking,
    manualUpdate,
    dismissUpdate,
    clearCacheAndReload
  } = useTimerCacheValidation({
    checkInterval: interval,
    enableAutoReload: autoReload,
    onUpdateDetected: (newVersion, currentVersion) => {
      console.log('🔄 New version detected:', {
        current: currentVersion?.buildTimestamp,
        new: newVersion.buildTimestamp,
        version: newVersion.version
      });
      setShowNotification(true);
    }
  });

  // Auto-hide notification after 10 seconds if not interacted with
  useEffect(() => {
    if (isUpdateAvailable && showNotification) {
      const timer = setTimeout(() => {
        setShowNotification(false);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [isUpdateAvailable, showNotification]);

  if (!isUpdateAvailable || !showNotification) {
    return null;
  }

  return (
    <div 
      className="fixed top-4 right-4 z-50 bg-blue-600 text-white p-4 rounded-lg shadow-lg max-w-sm"
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg 
            className="w-5 h-5 text-blue-200" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path 
              fillRule="evenodd" 
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
              clipRule="evenodd" 
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium">
            New Version Available
          </h4>
          <p className="text-sm text-blue-100 mt-1">
            Code changes detected. Reload to see the latest updates.
          </p>
          {currentVersion && (
            <p className="text-xs text-blue-200 mt-1">
              v{currentVersion.version} → New version
            </p>
          )}
        </div>
      </div>
      
      <div className="flex gap-2 mt-3">
        <button
          onClick={manualUpdate}
          className="bg-white text-blue-600 px-3 py-1 rounded text-sm font-medium hover:bg-blue-50 transition-colors"
          disabled={isChecking}
        >
          {isChecking ? 'Loading...' : 'Reload Now'}
        </button>
        <button
          onClick={() => {
            dismissUpdate();
            setShowNotification(false);
          }}
          className="text-blue-200 hover:text-white px-3 py-1 rounded text-sm transition-colors"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}

// Development-only manual cache clear component
export function DevCacheClearer() {
  const { clearCacheAndReload } = useTimerCacheValidation();
  
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <button
        onClick={clearCacheAndReload}
        className="bg-red-600 hover:bg-red-700 text-white text-xs px-3 py-2 rounded shadow-lg transition-colors"
        title="Clear all cache and reload (Dev only)"
      >
        🔄 Clear Cache
      </button>
    </div>
  );
}