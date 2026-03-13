"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const queryClient = new QueryClient({
   defaultOptions: {
      queries: {
         staleTime: 5 * 60 * 1000, // 5 minutes - prevent unnecessary refetches
         gcTime: 10 * 60 * 1000, // 10 minutes - keep data in cache (formerly cacheTime)
         retry: 2,
         refetchOnWindowFocus: false,
         refetchOnReconnect: true,
      },
   },
});

const ReactQueryProvider: React.FC<{ children: React.ReactNode }> = ({
   children,
}) => {
   return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
   );
};

export default ReactQueryProvider;