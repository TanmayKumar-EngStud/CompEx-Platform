"use client";

import { useState, useEffect, useCallback, useRef } from "react";

type AsyncState = "idle" | "loading" | "success" | "error";

interface UseAsyncStateOptions<T> {
   initialData?: T;
   retryAttempts?: number;
   retryDelay?: number;
   onSuccess?: (data: T) => void;
   onError?: (error: Error) => void;
   minLoadingTime?: number;
}

interface UseAsyncStateReturn<T> {
   data: T | undefined;
   error: Error | undefined;
   status: AsyncState;
   isLoading: boolean;
   isSuccess: boolean;
   isError: boolean;
   execute: (asyncFn: () => Promise<T>) => Promise<void>;
   retry: () => Promise<void>;
   reset: () => void;
   setData: (data: T) => void;
}

export function useAsyncState<T = any>(
   options: UseAsyncStateOptions<T> = {}
): UseAsyncStateReturn<T> {
   const {
      initialData,
      retryAttempts = 3,
      retryDelay = 1000,
      onSuccess,
      onError,
      minLoadingTime = 0,
   } = options;

   const [data, setData] = useState<T | undefined>(initialData);
   const [error, setError] = useState<Error | undefined>();
   const [status, setStatus] = useState<AsyncState>("idle");
   const [retryCount, setRetryCount] = useState(0);
   
   const lastAsyncFnRef = useRef<(() => Promise<T>) | null>(null);
   const minLoadingTimeRef = useRef<NodeJS.Timeout | null>(null);

   const reset = useCallback(() => {
      setData(initialData);
      setError(undefined);
      setStatus("idle");
      setRetryCount(0);
      lastAsyncFnRef.current = null;
      if (minLoadingTimeRef.current) {
         clearTimeout(minLoadingTimeRef.current);
         minLoadingTimeRef.current = null;
      }
   }, [initialData]);

   const execute = useCallback(async (asyncFn: () => Promise<T>) => {
      lastAsyncFnRef.current = asyncFn;
      setStatus("loading");
      setError(undefined);
      
      const startTime = Date.now();
      
      try {
         const result = await asyncFn();
         
         // Ensure minimum loading time for better UX
         const elapsedTime = Date.now() - startTime;
         const remainingTime = Math.max(0, minLoadingTime - elapsedTime);
         
         if (remainingTime > 0) {
            await new Promise(resolve => {
               minLoadingTimeRef.current = setTimeout(resolve, remainingTime);
            });
         }
         
         setData(result);
         setStatus("success");
         setRetryCount(0);
         onSuccess?.(result);
      } catch (err) {
         const error = err instanceof Error ? err : new Error(String(err));
         setError(error);
         setStatus("error");
         onError?.(error);
      }
   }, [minLoadingTime, onSuccess, onError]);

   const retry = useCallback(async () => {
      if (!lastAsyncFnRef.current) {
         throw new Error("No function to retry");
      }

      if (retryCount < retryAttempts) {
         setRetryCount(prev => prev + 1);
         
         // Add exponential backoff delay
         const delay = retryDelay * Math.pow(2, retryCount);
         await new Promise(resolve => setTimeout(resolve, delay));
         
         await execute(lastAsyncFnRef.current);
      } else {
         throw new Error(`Max retry attempts (${retryAttempts}) exceeded`);
      }
   }, [execute, retryCount, retryAttempts, retryDelay]);

   // Cleanup on unmount
   useEffect(() => {
      return () => {
         if (minLoadingTimeRef.current) {
            clearTimeout(minLoadingTimeRef.current);
         }
      };
   }, []);

   return {
      data,
      error,
      status,
      isLoading: status === "loading",
      isSuccess: status === "success",
      isError: status === "error",
      execute,
      retry,
      reset,
      setData,
   };
}

// Hook for managing multiple async operations
export function useAsyncOperations<T = any>() {
   const [operations, setOperations] = useState<Map<string, UseAsyncStateReturn<T>>>(new Map());

   const createOperation = useCallback((
      key: string, 
      options?: UseAsyncStateOptions<T>
   ) => {
      // Return a factory function instead of creating the hook inside callback
      return {
         key,
         options,
         create: () => {
            // This should be called at component level, not inside callback
            throw new Error("useAsyncOperations.createOperation should be restructured to avoid calling hooks in callbacks");
         }
      };
   }, []);

   const getOperation = useCallback((key: string) => {
      return operations.get(key);
   }, [operations]);

   const removeOperation = useCallback((key: string) => {
      setOperations(prev => {
         const newMap = new Map(prev);
         newMap.delete(key);
         return newMap;
      });
   }, []);

   const getAllOperations = useCallback(() => {
      return Array.from(operations.values());
   }, [operations]);

   const isAnyLoading = useCallback(() => {
      return Array.from(operations.values()).some(op => op.isLoading);
   }, [operations]);

   return {
      createOperation,
      getOperation,
      removeOperation,
      getAllOperations,
      isAnyLoading,
      operations: Object.fromEntries(operations),
   };
}

export default useAsyncState;