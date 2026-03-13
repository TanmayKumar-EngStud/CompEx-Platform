/**
 * Priority Cache Provider
 * 
 * Integrates priority caching with the React application, providing
 * context for priority cache management and background services.
 */

"use client";
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { usePriorityCache } from '@/shared/lib/cache/priority-cache';
import { useBackgroundCache } from '@/shared/services/background-cache-service';
import { PriorityCacheProgress } from '@/shared/components/feedback/PriorityCacheProgress';

interface PriorityCacheContextType {
  loadingState: {
    immediate: boolean;
    high: boolean;
    background: boolean;
    progress: {
      completed: number;
      total: number;
      currentTask: string;
    };
  };
  cacheStats: any;
  initializePriorityCache: (examName: string, sectionName: string, filters?: { topics?: string[], themes?: string[], types?: string[] }) => Promise<void>;
  updateUserBehavior: (examName: string, sectionName: string) => void;
  backgroundServiceStats: any;
}

const PriorityCacheContext = createContext<PriorityCacheContextType | undefined>(undefined);

interface PriorityCacheProviderProps {
  children: ReactNode;
  showProgress?: boolean;
  autoStart?: boolean;
}

export const PriorityCacheProvider: React.FC<PriorityCacheProviderProps> = ({
  children,
  showProgress = true,
  autoStart = true
}) => {
  const priorityCache = usePriorityCache();
  const backgroundCache = useBackgroundCache();

  const [loadingState, setLoadingState] = useState({
    immediate: false,
    high: false,
    background: false,
    progress: { completed: 0, total: 0, currentTask: '' }
  });

  const [cacheStats, setCacheStats] = useState<any>(null);
  const [backgroundServiceStats, setBackgroundServiceStats] = useState<any>(null);

  // Initialize background cache service
  useEffect(() => {
    if (autoStart) {
      backgroundCache.start();

      // Update stats periodically
      const statsInterval = setInterval(() => {
        setCacheStats(priorityCache.getCacheStats());
        setBackgroundServiceStats(backgroundCache.getStats());
      }, 5000);

      return () => {
        backgroundCache.stop();
        clearInterval(statsInterval);
      };
    }
  }, [autoStart, backgroundCache, priorityCache]);

  // Initialize priority cache for specific exam/section
  const initializePriorityCache = async (
    examName: string,
    sectionName: string,
    filters: { topics?: string[], themes?: string[], types?: string[] } = {}
  ) => {
    setLoadingState(prev => ({
      ...prev,
      immediate: true,
      background: true
    }));

    try {
      await priorityCache.executePriorityPlan(
        examName,
        sectionName,
        filters,
        (progress) => {
          setLoadingState(prev => ({
            ...prev,
            progress
          }));
        }
      );

      // Update user behavior for background service
      backgroundCache.updateUserBehavior(examName, sectionName);

      console.log('✅ Priority cache initialized for', examName, sectionName);

    } catch (error) {
      console.error('❌ Priority cache initialization failed:', error);
    } finally {
      setLoadingState(prev => ({
        ...prev,
        immediate: false,
        high: false,
        background: false
      }));
    }
  };

  // Update user behavior wrapper
  const updateUserBehavior = (examName: string, sectionName: string) => {
    backgroundCache.updateUserBehavior(examName, sectionName);
  };

  const contextValue: PriorityCacheContextType = {
    loadingState,
    cacheStats,
    initializePriorityCache,
    updateUserBehavior,
    backgroundServiceStats,
  };

  return (
    <PriorityCacheContext.Provider value={contextValue}>
      {showProgress && (
        <PriorityCacheProgress
          loadingState={loadingState}
          className="fixed top-4 right-4 w-80 z-50"
        />
      )}
      {children}
    </PriorityCacheContext.Provider>
  );
};

/**
 * Hook to use priority cache context
 */
export const usePriorityCacheContext = (): PriorityCacheContextType => {
  const context = useContext(PriorityCacheContext);
  if (!context) {
    throw new Error('usePriorityCacheContext must be used within a PriorityCacheProvider');
  }
  return context;
};

/**
 * HOC for components that need priority caching
 */
export function withPriorityCache<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    showProgress?: boolean;
    autoInitialize?: boolean;
  }
) {
  return function PriorityCacheWrappedComponent(props: P) {
    return (
      <PriorityCacheProvider
        showProgress={options?.showProgress ?? false}
        autoStart={true}
      >
        <Component {...props} />
      </PriorityCacheProvider>
    );
  };
}

export default PriorityCacheProvider;