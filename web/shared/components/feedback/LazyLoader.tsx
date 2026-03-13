"use client";

import React, { Suspense, lazy, ComponentType } from "react";
import { motion } from "framer-motion";
import Loading from "@/shared/components/feedback/loading";

// Generic lazy loading wrapper with enhanced loading states
interface LazyLoaderProps<T = {}> {
   loader: () => Promise<{ default: ComponentType<T> }>;
   fallback?: React.ReactNode;
   loadingMessage?: string;
   errorBoundary?: boolean;
   delay?: number;
   className?: string;
   containerClassName?: string;
   props?: T;
}

// Cache for lazy components to prevent re-creation
const lazyComponentCache = new Map<string, ComponentType<any>>();

function LazyLoader<T = {}>({
   loader,
   fallback,
   loadingMessage = "Loading...",
   errorBoundary = true,
   delay = 0,
   className = "",
   containerClassName = "",
   props = {} as T,
}: LazyLoaderProps<T>) {
   // Create a cache key from the loader function
   const cacheKey = loader.toString();
   
   // Get or create the lazy component from cache
   let LazyComponent = lazyComponentCache.get(cacheKey);
   
   if (!LazyComponent) {
      LazyComponent = lazy(() => {
         if (delay > 0) {
            return new Promise<{ default: ComponentType<T> }>(resolve => {
               setTimeout(() => {
                  loader().then(resolve);
               }, delay);
            });
         }
         return loader();
      });
      lazyComponentCache.set(cacheKey, LazyComponent);
   }

   const defaultFallback = (
      <motion.div 
         className={`flex items-center justify-center p-8 ${className}`}
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ duration: 0.3 }}
      >
         <Loading size="md" message={loadingMessage} />
      </motion.div>
   );

   const LoaderWithErrorBoundary = errorBoundary ? 
      withErrorBoundary(LazyComponent) : LazyComponent;

   return (
      <div className={containerClassName}>
         <Suspense fallback={fallback || defaultFallback}>
            <LoaderWithErrorBoundary {...(props as any)} />
         </Suspense>
      </div>
   );
}

// Error boundary HOC for lazy loaded components
function withErrorBoundary<T>(Component: ComponentType<T>) {
   return function ErrorBoundaryWrapper(props: T) {
      return (
         <ErrorBoundary>
            <Component {...(props as any)} />
         </ErrorBoundary>
      );
   };
}

class ErrorBoundary extends React.Component<
   { children: React.ReactNode },
   { hasError: boolean; error?: Error }
> {
   constructor(props: { children: React.ReactNode }) {
      super(props);
      this.state = { hasError: false };
   }

   static getDerivedStateFromError(error: Error) {
      return { hasError: true, error };
   }

   componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
      console.error('Lazy loading error:', error, errorInfo);
   }

   render() {
      if (this.state.hasError) {
         return (
            <motion.div 
               className="flex flex-col items-center justify-center p-8 text-center"
               initial={{ opacity: 0 }}
               animate={{ opacity: 1 }}
               transition={{ duration: 0.3 }}
            >
               <div className="text-destructive mb-2">⚠️ Something went wrong</div>
               <p className="text-muted-foreground text-sm">
                  Failed to load component. Please try refreshing the page.
               </p>
               <button 
                  onClick={() => window.location.reload()} 
                  className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
               >
                  Reload Page
               </button>
            </motion.div>
         );
      }

      return this.props.children;
   }
}

export default LazyLoader;