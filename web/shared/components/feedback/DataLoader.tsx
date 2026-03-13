"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import Loading from "@/shared/components/feedback/loading";

// Data loading states
type LoadingState = "idle" | "loading" | "success" | "error";

interface DataLoaderProps<T = any> {
   status: LoadingState;
   data?: T;
   error?: Error | unknown;
   previousData?: T | null;
   children: (data: T) => React.ReactNode;
   loader?: React.ReactNode;
   errorComponent?: React.ReactNode;
   emptyComponent?: React.ReactNode;
   loadingMessage?: string;
   retryAction?: () => void;
   className?: string;
   showPreviousData?: boolean;
   minLoadingTime?: number;
}

function DataLoader<T = any>({
   status,
   data,
   error,
   previousData,
   children,
   loader,
   errorComponent,
   emptyComponent,
   loadingMessage = "Loading...",
   retryAction,
   className = "",
   showPreviousData = true,
   minLoadingTime = 0,
}: DataLoaderProps<T>) {
   const [showLoading, setShowLoading] = React.useState(false);
   const [hasData, setHasData] = React.useState(false);
   const prevDataRef = React.useRef<T | undefined>(undefined);
   const isInitialMount = React.useRef(true);

   // Track if we actually have data to prevent unnecessary loading states
   React.useEffect(() => {
      if (data !== undefined && data !== null) {
         setHasData(true);
         prevDataRef.current = data;
      }
   }, [data]);

   // Efficient data comparison function
   const hasDataChanged = React.useCallback((newData: T | undefined, oldData: T | undefined): boolean => {
      if (newData === oldData) return false;
      if (newData === undefined || oldData === undefined) return true;
      
      // For arrays, compare length and first few elements
      if (Array.isArray(newData) && Array.isArray(oldData)) {
         if (newData.length !== oldData.length) return true;
         // Quick check on first 3 elements to detect changes without full comparison
         for (let i = 0; i < Math.min(3, newData.length); i++) {
            if (newData[i] !== oldData[i]) return true;
         }
         return false;
      }
      
      // For objects, do a shallow comparison of keys
      if (typeof newData === 'object' && typeof oldData === 'object' && newData !== null && oldData !== null) {
         const newKeys = Object.keys(newData as object);
         const oldKeys = Object.keys(oldData as object);
         
         if (newKeys.length !== oldKeys.length) return true;
         
         // Check first few key-value pairs
         for (let i = 0; i < Math.min(5, newKeys.length); i++) {
            const key = newKeys[i];
            if (!oldKeys.includes(key) || (newData as any)[key] !== (oldData as any)[key]) {
               return true;
            }
         }
         return false;
      }
      
      return newData !== oldData;
   }, []);

   // Only show loading if we're actually loading AND either:
   // 1. It's the initial load (no data yet), or
   // 2. The data is changing (different from previous)
   React.useEffect(() => {
      const isDataChanging = hasDataChanged(data, prevDataRef.current);
      
      const shouldShowLoading = status === "loading" && 
                               (isInitialMount.current || !hasData || isDataChanging);

      if (shouldShowLoading) {
         setShowLoading(true);
         isInitialMount.current = false;
         
         if (minLoadingTime > 0) {
            const timer = setTimeout(() => {
               if (status !== "loading") {
                  setShowLoading(false);
               }
            }, minLoadingTime);
            return () => clearTimeout(timer);
         }
      } else {
         setShowLoading(false);
         if (status === "success" && isInitialMount.current) {
            isInitialMount.current = false;
         }
      }
   }, [status, data, hasData, minLoadingTime, hasDataChanged]);

   // Error component
   const defaultErrorComponent = (
      <motion.div 
         className="flex flex-col items-center justify-center p-8 text-center"
         initial={{ opacity: 0, scale: 0.9 }}
         animate={{ opacity: 1, scale: 1 }}
         transition={{ duration: 0.3 }}
      >
         <div className="text-destructive mb-4 text-4xl">⚠️</div>
         <h3 className="text-lg font-semibold text-foreground mb-2">
            Something went wrong
         </h3>
         <p className="text-muted-foreground mb-4 max-w-md">
            {error instanceof Error ? error.message : "An unexpected error occurred"}
         </p>
         {retryAction && (
            <button 
               onClick={retryAction}
               className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
               Try Again
            </button>
         )}
      </motion.div>
   );

   // Loading component
   const defaultLoader = (
      <motion.div 
         className="flex items-center justify-center p-8"
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ duration: 0.3 }}
      >
         <Loading size="md" message={loadingMessage} />
      </motion.div>
   );

   // Empty state component
   const defaultEmptyComponent = (
      <motion.div 
         className="flex flex-col items-center justify-center p-8 text-center"
         initial={{ opacity: 0, y: 10 }}
         animate={{ opacity: 1, y: 0 }}
         transition={{ duration: 0.3 }}
      >
         <div className="text-muted-foreground mb-4 text-4xl">📭</div>
         <h3 className="text-lg font-semibold text-foreground mb-2">
            No data available
         </h3>
         <p className="text-muted-foreground">
            There&apos;s nothing to show right now.
         </p>
      </motion.div>
   );

   // Check if data is empty
   const isEmpty = (data: any): boolean => {
      if (data === null || data === undefined) return true;
      if (Array.isArray(data)) return data.length === 0;
      if (typeof data === 'object') return Object.keys(data).length === 0;
      return false;
   };

   return (
      <div className={className}>
         <AnimatePresence mode="wait">
            {/* Loading State */}
            {(showLoading || status === "loading") && (
               <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
               >
                  {loader || defaultLoader}
               </motion.div>
            )}

            {/* Error State */}
            {status === "error" && !showLoading && (
               <motion.div
                  key="error"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
               >
                  {errorComponent || defaultErrorComponent}
               </motion.div>
            )}

            {/* Success State - with data */}
            {status === "success" && !showLoading && data && !isEmpty(data) && (
               <motion.div
                  key="success"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
               >
                  {children(data)}
               </motion.div>
            )}

            {/* Success State - but empty data */}
            {status === "success" && !showLoading && (!data || isEmpty(data)) && (
               <motion.div
                  key="empty"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
               >
                  {emptyComponent || defaultEmptyComponent}
               </motion.div>
            )}

            {/* Show previous data while loading if available */}
            {status === "loading" && showPreviousData && previousData && !isEmpty(previousData) && (
               <motion.div
                  key="previous-data"
                  initial={{ opacity: 1 }}
                  animate={{ opacity: 0.6 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="relative"
               >
                  {children(previousData)}
                  <div className="absolute inset-0 bg-background/20 backdrop-blur-[1px] flex items-center justify-center">
                     <Loading size="sm" message="Updating..." />
                  </div>
               </motion.div>
            )}
         </AnimatePresence>
      </div>
   );
}

export default DataLoader;