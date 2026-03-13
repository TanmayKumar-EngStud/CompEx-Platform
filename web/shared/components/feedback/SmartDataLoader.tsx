"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import Loading from "@/shared/components/feedback/loading";

type LoadingState = "idle" | "loading" | "success" | "error";

interface SmartDataLoaderProps<T = any> {
   status: LoadingState;
   data?: T;
   error?: Error | unknown;
   children: (data: T) => React.ReactNode;
   loader?: React.ReactNode;
   errorComponent?: React.ReactNode;
   emptyComponent?: React.ReactNode;
   loadingMessage?: string;
   retryAction?: () => void;
   className?: string;
   // Smart loading options
   suppressLoadingWhenDataExists?: boolean;
   dataKey?: string; // Key to track data changes more efficiently
}

const SmartDataLoader = React.memo(function SmartDataLoader<T = any>({
   status,
   data,
   error,
   children,
   loader,
   errorComponent,
   emptyComponent,
   loadingMessage = "Loading...",
   retryAction,
   className = "",
   suppressLoadingWhenDataExists = true,
   dataKey,
}: SmartDataLoaderProps<T>) {
   const [hasInitialData, setHasInitialData] = React.useState(false);
   const [cachedData, setCachedData] = React.useState<T | undefined>(data);
   const prevDataKeyRef = React.useRef<string | undefined>(dataKey);

   // Track if we have data to prevent unnecessary loading states
   React.useEffect(() => {
      if (data !== undefined && data !== null) {
         setHasInitialData(true);
         setCachedData(data);
      }
   }, [data]);

   // Check if dataKey has changed (indicating different data request)
   const isDataKeyChanged = dataKey !== prevDataKeyRef.current;
   React.useEffect(() => {
      if (isDataKeyChanged) {
         prevDataKeyRef.current = dataKey;
      }
   }, [dataKey, isDataKeyChanged]);

   // Determine if we should show loading
   const shouldShowLoading = React.useMemo(() => {
      if (status !== "loading") return false;
      
      // If we want to suppress loading when data exists and we have data, don't show loading
      if (suppressLoadingWhenDataExists && hasInitialData && !isDataKeyChanged) {
         return false;
      }
      
      return true;
   }, [status, suppressLoadingWhenDataExists, hasInitialData, isDataKeyChanged]);

   // Check if data is empty
   const isEmpty = (data: any): boolean => {
      if (data === null || data === undefined) return true;
      if (Array.isArray(data)) return data.length === 0;
      if (typeof data === 'object') return Object.keys(data).length === 0;
      return false;
   };

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

   return (
      <div className={className}>
         <AnimatePresence mode="wait">
            {/* Loading State - only when actually needed */}
            {shouldShowLoading && (
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
            {status === "error" && !shouldShowLoading && (
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
            {(status === "success" || (status === "loading" && cachedData && suppressLoadingWhenDataExists)) && 
             !shouldShowLoading && data && !isEmpty(data) && (
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
            {status === "success" && !shouldShowLoading && (!data || isEmpty(data)) && (
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
         </AnimatePresence>
      </div>
   );
}) as <T = any>(props: SmartDataLoaderProps<T>) => React.ReactElement;

export default SmartDataLoader;