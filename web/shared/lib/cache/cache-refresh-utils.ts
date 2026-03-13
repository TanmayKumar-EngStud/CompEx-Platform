/**
 * Cache Refresh Utilities
 * 
 * Utilities to force refresh caches when service worker is serving stale code
 * that causes the Prisma client-side error.
 */

import { getServiceWorkerManager } from './service-worker';

export class CacheRefreshManager {
  private serviceWorkerManager = getServiceWorkerManager();

  /**
   * Force clear all caches and reload the page
   * Use this when you detect Prisma client-side errors
   */
  async forceRefresh(): Promise<void> {
    try {
      console.log('🔄 Force refreshing application caches...');
      
      // Clear browser caches
      await this.clearBrowserCaches();
      
      // Clear service worker caches
      await this.clearServiceWorkerCaches();
      
      // Reload the page to get fresh code
      window.location.reload();
      
    } catch (error) {
      console.error('❌ Force refresh failed:', error);
      // Fallback: hard reload
      window.location.reload();
    }
  }

  /**
   * Clear browser caches (localStorage, sessionStorage, etc.)
   */
  private async clearBrowserCaches(): Promise<void> {
    try {
      // Clear localStorage (but preserve user preferences)
      const keysToPreserve = ['theme', 'user-preferences'];
      const localStorageBackup: Record<string, string> = {};
      
      keysToPreserve.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
          localStorageBackup[key] = value;
        }
      });
      
      localStorage.clear();
      
      // Restore preserved keys
      Object.entries(localStorageBackup).forEach(([key, value]) => {
        localStorage.setItem(key, value);
      });
      
      // Clear sessionStorage
      sessionStorage.clear();
      
      console.log('✅ Browser caches cleared');
    } catch (error) {
      console.warn('⚠️ Failed to clear browser caches:', error);
    }
  }

  /**
   * Clear service worker caches
   */
  private async clearServiceWorkerCaches(): Promise<void> {
    try {
      await this.serviceWorkerManager.sendMessage({ type: 'FORCE_UPDATE' });
      await this.serviceWorkerManager.clearCaches();
      console.log('✅ Service worker caches cleared');
    } catch (error) {
      console.warn('⚠️ Failed to clear service worker caches:', error);
    }
  }

  /**
   * Check if we're experiencing the Prisma client-side error
   */
  detectPrismaError(error: any): boolean {
    const errorMessage = error?.message || error?.toString() || '';
    return errorMessage.includes('PrismaClient is unable to run in this browser environment') ||
           errorMessage.includes('bundled for the browser');
  }

  /**
   * Clear only JavaScript caches (lighter refresh)
   */
  async clearJavaScriptCaches(): Promise<void> {
    try {
      console.log('🔄 Clearing JavaScript caches...');
      await this.serviceWorkerManager.sendMessage({ type: 'CLEAR_JS_CACHE' });
      console.log('✅ JavaScript caches cleared');
    } catch (error) {
      console.warn('⚠️ Failed to clear JS caches:', error);
    }
  }

  /**
   * Get cache information for debugging
   */
  async getCacheInfo(): Promise<any> {
    try {
      return new Promise((resolve) => {
        const channel = new MessageChannel();
        channel.port1.onmessage = (event) => {
          if (event.data.type === 'CACHE_INFO') {
            resolve(event.data.data);
          }
        };
        
        this.serviceWorkerManager.sendMessage(
          { type: 'GET_CACHE_INFO' },
          [channel.port2]
        );
        
        // Timeout after 5 seconds
        setTimeout(() => resolve(null), 5000);
      });
    } catch (error) {
      console.error('❌ Failed to get cache info:', error);
      return null;
    }
  }

  /**
   * Setup automatic error detection and cache refresh
   */
  setupAutoRefresh(): void {
    // Listen for global errors
    window.addEventListener('error', (event) => {
      if (this.detectPrismaError(event.error)) {
        console.warn('🚨 Detected Prisma client-side error, triggering cache refresh...');
        this.forceRefresh();
      }
    });

    // Listen for unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      if (this.detectPrismaError(event.reason)) {
        console.warn('🚨 Detected Prisma client-side error in promise, triggering cache refresh...');
        this.forceRefresh();
      }
    });

    console.log('🛡️ Auto cache refresh setup completed');
  }

  /**
   * Manual cache refresh button (for development/debugging)
   */
  createDebugButton(): HTMLButtonElement {
    const button = document.createElement('button');
    button.innerHTML = '🔄 Force Refresh Cache';
    button.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 10000;
      background: #ff4444;
      color: white;
      border: none;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    `;
    
    button.addEventListener('click', () => {
      this.forceRefresh();
    });
    
    // Only show in development
    if (process.env.NODE_ENV === 'development') {
      document.body.appendChild(button);
    }
    
    return button;
  }
}

/**
 * Singleton instance
 */
let cacheRefreshManager: CacheRefreshManager | null = null;

export function getCacheRefreshManager(): CacheRefreshManager {
  if (!cacheRefreshManager) {
    cacheRefreshManager = new CacheRefreshManager();
  }
  return cacheRefreshManager;
}

/**
 * Quick utility to force refresh when Prisma error is detected
 */
export async function handlePrismaError(error: any): Promise<void> {
  const manager = getCacheRefreshManager();
  
  if (manager.detectPrismaError(error)) {
    console.warn('🚨 Prisma client-side error detected, refreshing caches...');
    await manager.forceRefresh();
  } else {
    // Re-throw if it's not a Prisma error
    throw error;
  }
}

/**
 * Setup automatic cache refresh on app initialization
 */
export function initializeCacheRefresh(): void {
  const manager = getCacheRefreshManager();
  manager.setupAutoRefresh();
  
  // Create debug button in development
  if (process.env.NODE_ENV === 'development') {
    manager.createDebugButton();
  }
}

/**
 * React hook for cache refresh functionality
 */
export function useCacheRefresh() {
  const manager = getCacheRefreshManager();
  
  return {
    forceRefresh: manager.forceRefresh.bind(manager),
    clearJavaScriptCaches: manager.clearJavaScriptCaches.bind(manager),
    detectPrismaError: manager.detectPrismaError.bind(manager),
    getCacheInfo: manager.getCacheInfo.bind(manager),
  };
}