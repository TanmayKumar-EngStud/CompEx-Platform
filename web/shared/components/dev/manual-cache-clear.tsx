"use client";

import React from 'react';
import { Button } from '@/shared/components/ui/button';
import { RefreshCw } from 'lucide-react';

/**
 * Manual Cache Clear Component
 * Simple utility for development to clear all caches manually
 * Use this as a temporary solution until automatic cache invalidation is reimplemented
 */
export function ManualCacheClear() {
  const [isClearing, setIsClearing] = React.useState(false);

  const clearAllCaches = async () => {
    setIsClearing(true);
    
    try {
      // Clear localStorage
      localStorage.clear();
      console.log('✅ localStorage cleared');

      // Clear sessionStorage  
      sessionStorage.clear();
      console.log('✅ sessionStorage cleared');

      // Clear React Query cache if available
      if (typeof window !== 'undefined' && (window as any).queryClient) {
        await (window as any).queryClient.clear();
        console.log('✅ React Query cache cleared');
      }

      // Clear Service Worker caches
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)));
        console.log(`✅ Cleared ${cacheNames.length} service worker caches`);
      }

      console.log('🔄 Reloading page...');
      
      // Force reload with cache bust
      const cacheBustParam = `cache_bust=${Date.now()}`;
      const separator = window.location.search ? '&' : '?';
      window.location.href = `${window.location.pathname}${window.location.search}${separator}${cacheBustParam}`;
      
    } catch (error) {
      console.error('❌ Error clearing caches:', error);
      // Fallback to simple reload
      window.location.reload();
    }
  };

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999]">
      <Button
        onClick={clearAllCaches}
        disabled={isClearing}
        variant="outline"
        size="sm"
        className="flex items-center gap-2 bg-background/90 backdrop-blur border-border hover:bg-muted shadow-lg"
      >
        <RefreshCw 
          size={14} 
          className={isClearing ? "animate-spin" : ""} 
        />
        {isClearing ? 'Clearing...' : 'Clear Cache'}
      </Button>
    </div>
  );
}