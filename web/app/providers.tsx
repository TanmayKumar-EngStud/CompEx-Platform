/*
next-themes actually requires a ThemeProvider to wrap your application.
- responsible for managing the theme state and making it available via the useTheme hook.
- needed to create a client component to host the ThemeProvider
*/

"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ThemeProviderProps } from "next-themes";
import { initializeServiceWorker, setupOfflineDetection } from "@/shared/lib/cache/service-worker";
import { getQueryCacheService } from "@/shared/lib/cache/query-cache";
import { StreakProvider } from "@/shared/contexts/StreakContext";

export default function ThemeProvider({
   children,
   ...props
}: ThemeProviderProps) {
   // Initialize caching systems on mount
   React.useEffect(() => {
      const initializeCachingSystems = async () => {
         try {
            // TEMPORARILY DISABLED: Initialize service worker for offline caching
            // const status = await initializeServiceWorker();
            // if (status.isSupported) {
            //    console.log('✅ Service Worker initialized');
            // } else {
            //    console.warn('⚠️ Service Worker not supported');
            // }

            // TEMPORARILY DISABLED: Setup offline detection
            // setupOfflineDetection();

            // Explicitly unregister any existing service workers to fix development caching issues
            // This ensures that stale SWs don't serve old content in dev mode
            if (process.env.NODE_ENV === 'development') {
               try {
                  const registrations = await navigator.serviceWorker.getRegistrations();
                  if (registrations.length > 0) {
                     console.log(`🧹 Found ${registrations.length} lingering service workers, cleaning up...`);
                     for (const registration of registrations) {
                        await registration.unregister();
                        console.log('✅ Unregistered service worker');
                     }
                     // Force reload only if we actually found and removed a SW, 
                     // to ensure next load is clean (optional, but helpful)
                     // window.location.reload(); 
                  }
               } catch (error) {
                  console.warn('⚠️ Failed to cleanup service workers:', error);
               }
            }

            console.log('⚠️ Service Worker disabled for development');

            // Preload common data (keeping this active ONLY in production to avoid dev server overload)
            if (process.env.NODE_ENV === 'production') {
               const queryCacheService = getQueryCacheService();
               await queryCacheService.preloadCommonData();
            } else {
               console.log('⚠️ Data preloading disabled for development to improve startup time');
            }
         } catch (error) {
            console.warn('⚠️ Failed to initialize caching systems:', error);
         }
      };

      initializeCachingSystems();
   }, []);

   return (
      <NextThemesProvider
         attribute="class"
         defaultTheme="system"
         enableSystem={true}
         disableTransitionOnChange={false}
         storageKey="compex-theme-preference"
         {...props}
      >
         <StreakProvider>
            {children}
         </StreakProvider>
      </NextThemesProvider>
   );
}
