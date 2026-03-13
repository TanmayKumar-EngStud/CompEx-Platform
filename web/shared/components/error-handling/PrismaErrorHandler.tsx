/**
 * Prisma Error Handler Component
 * 
 * Automatically detects and handles PrismaClient browser environment errors
 * by refreshing caches and providing user feedback.
 */

"use client";
import React, { useEffect, useState } from 'react';
import { getCacheRefreshManager } from '@/shared/lib/cache/cache-refresh-utils';
import { Alert, AlertDescription } from '@/shared/components/feedback/alert';
import { Button } from '@/shared/components/ui/button';
import { RefreshCw, AlertTriangle } from 'lucide-react';

interface PrismaErrorHandlerProps {
  children: React.ReactNode;
  onError?: (error: Error) => void;
  showErrorUI?: boolean;
  autoRefresh?: boolean;
}

interface ErrorState {
  hasError: boolean;
  error: Error | null;
  isRefreshing: boolean;
  retryCount: number;
}

export const PrismaErrorHandler: React.FC<PrismaErrorHandlerProps> = ({
  children,
  onError,
  showErrorUI = true,
  autoRefresh = true,
}) => {
  const [errorState, setErrorState] = useState<ErrorState>({
    hasError: false,
    error: null,
    isRefreshing: false,
    retryCount: 0,
  });

  const cacheManager = getCacheRefreshManager();

  useEffect(() => {
    // Setup error boundary for unhandled promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (cacheManager.detectPrismaError(event.reason)) {
        console.warn('🚨 Detected Prisma error in promise rejection');
        handlePrismaError(event.reason);
        event.preventDefault(); // Prevent default browser error handling
      }
    };

    // Setup error boundary for regular errors
    const handleError = (event: ErrorEvent) => {
      if (cacheManager.detectPrismaError(event.error)) {
        console.warn('🚨 Detected Prisma error in global error handler');
        handlePrismaError(event.error);
        event.preventDefault();
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, [cacheManager]);

  const handlePrismaError = async (error: Error) => {
    console.log('🔄 Handling Prisma client-side error...');
    
    setErrorState(prev => ({
      hasError: true,
      error,
      isRefreshing: autoRefresh,
      retryCount: prev.retryCount + 1,
    }));

    // Call user's error handler
    onError?.(error);

    if (autoRefresh && errorState.retryCount < 3) {
      try {
        await cacheManager.forceRefresh();
      } catch (refreshError) {
        console.error('❌ Failed to refresh cache:', refreshError);
        setErrorState(prev => ({ ...prev, isRefreshing: false }));
      }
    }
  };

  const handleManualRefresh = async () => {
    setErrorState(prev => ({ ...prev, isRefreshing: true }));
    
    try {
      await cacheManager.forceRefresh();
    } catch (error) {
      console.error('❌ Manual refresh failed:', error);
      setErrorState(prev => ({ ...prev, isRefreshing: false }));
    }
  };

  const clearError = () => {
    setErrorState({
      hasError: false,
      error: null,
      isRefreshing: false,
      retryCount: 0,
    });
  };

  // Error boundary-like behavior
  if (errorState.hasError && showErrorUI) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 space-y-4">
        <Alert className="max-w-md">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription className="space-y-3">
            <div>
              <strong>Application Update Required</strong>
            </div>
            <div className="text-sm text-muted-foreground">
              The application needs to refresh to load the latest version. 
              This usually happens after updates.
            </div>
            <div className="flex space-x-2">
              <Button 
                onClick={handleManualRefresh}
                disabled={errorState.isRefreshing}
                size="sm"
                className="flex items-center space-x-1"
              >
                <RefreshCw className={`h-3 w-3 ${errorState.isRefreshing ? 'animate-spin' : ''}`} />
                <span>{errorState.isRefreshing ? 'Refreshing...' : 'Refresh Now'}</span>
              </Button>
              
              <Button 
                onClick={clearError}
                variant="outline"
                size="sm"
              >
                Continue Anyway
              </Button>
            </div>
            
            {errorState.retryCount > 2 && (
              <div className="text-xs text-amber-600">
                Multiple refresh attempts detected. You may need to manually clear your browser cache.
              </div>
            )}
          </AlertDescription>
        </Alert>

        {/* Debug information in development */}
        {process.env.NODE_ENV === 'development' && errorState.error && (
          <details className="max-w-md text-xs bg-gray-100 p-2 rounded">
            <summary className="cursor-pointer font-medium">Error Details (Dev)</summary>
            <pre className="mt-2 whitespace-pre-wrap">
              {errorState.error.message}
            </pre>
          </details>
        )}
      </div>
    );
  }

  return <>{children}</>;
};

/**
 * Hook for programmatic error handling
 */
export const usePrismaErrorHandler = () => {
  const cacheManager = getCacheRefreshManager();
  
  const handleError = async (error: unknown) => {
    if (cacheManager.detectPrismaError(error)) {
      console.warn('🚨 Prisma error detected, triggering cache refresh...');
      await cacheManager.forceRefresh();
      return true; // Indicates error was handled
    }
    return false; // Indicates error was not handled
  };

  return {
    handleError,
    detectPrismaError: cacheManager.detectPrismaError.bind(cacheManager),
    forceRefresh: cacheManager.forceRefresh.bind(cacheManager),
    clearJavaScriptCaches: cacheManager.clearJavaScriptCaches.bind(cacheManager),
  };
};

/**
 * Higher-order component for automatic Prisma error handling
 */
export function withPrismaErrorHandler<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    showErrorUI?: boolean;
    autoRefresh?: boolean;
    onError?: (error: Error) => void;
  }
) {
  return function PrismaErrorWrappedComponent(props: P) {
    return (
      <PrismaErrorHandler
        showErrorUI={options?.showErrorUI ?? true}
        autoRefresh={options?.autoRefresh ?? true}
        onError={options?.onError}
      >
        <Component {...props} />
      </PrismaErrorHandler>
    );
  };
}

export default PrismaErrorHandler;