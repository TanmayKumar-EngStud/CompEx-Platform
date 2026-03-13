/**
 * CompEx Service Worker for Advanced Caching
 *
 * Implements intelligent caching strategies for:
 * - Static assets (long-term caching)
 * - API responses (short-term caching with fallbacks)
 * - Offline functionality
 * - Background sync for failed requests
 */

const CACHE_VERSION = "compex-v1.1.0"; // Updated to force cache refresh
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Cache duration in milliseconds
const CACHE_DURATIONS = {
   STATIC: 30 * 24 * 60 * 60 * 1000, // 30 days
   API: 15 * 60 * 1000, // 15 minutes
   DYNAMIC: 24 * 60 * 60 * 1000, // 24 hours
};

// Static assets to cache immediately
const STATIC_ASSETS = [
   "/",
   "/dashboard/problems",
   "/manifest.json",
   // Add critical CSS and JS files
];

// API endpoints to cache
const CACHEABLE_APIS = [
   "/api/problems/tags",
   "/api/problems/getProblems",
   "/api/problems/getProblemsSets",
   "/api/problems/getQuestions",
];

// API endpoints to NEVER cache (always fetch fresh)
const NEVER_CACHE_APIS = [
   "/api/problems/returnAttempt",
   "/api/submit-answers",
   "/api/problems/[id]/attempts",
];

/**
 * Install event - cache static assets
 */
self.addEventListener("install", (event) => {
   // console.log('🔧 Service Worker installing...');

   event.waitUntil(
      caches
         .open(STATIC_CACHE)
         .then((cache) => {
            // console.log('📦 Caching static assets');
            return cache.addAll(STATIC_ASSETS);
         })
         .then(() => {
            // console.log('✅ Static assets cached');
            return self.skipWaiting();
         })
         .catch((error) => {
            console.error("❌ Failed to cache static assets:", error);
         })
   );
});

/**
 * Activate event - cleanup old caches
 */
self.addEventListener("activate", (event) => {
   // console.log("🚀 Service Worker activating...");

   event.waitUntil(
      caches
         .keys()
         .then((cacheNames) => {
            return Promise.all(
               cacheNames.map((cacheName) => {
                  // Delete old cache versions
                  if (
                     cacheName.includes("compex-") &&
                     !cacheName.includes(CACHE_VERSION)
                  ) {
                     // console.log("🗑️ Deleting old cache:", cacheName);
                     return caches.delete(cacheName);
                  }
               })
            );
         })
         .then(() => {
            // console.log("✅ Service Worker activated");
            return self.clients.claim();
         })
   );
});

/**
 * Fetch event - implement caching strategies
 */
self.addEventListener("fetch", (event) => {
   const { request } = event;
   const url = new URL(request.url);
   // Skip non-GET requests
   if (request.method !== "GET") {
      return;
   }
   // Skip chrome-extension requests
   if (url.protocol === "chrome-extension:") {
      return;
   }
   // Different strategies for different types of requests
   if (url.pathname.startsWith("/api/")) {
      event.respondWith(handleApiRequest(request));
   } else if (isStaticAsset(request)) {
      event.respondWith(handleStaticAsset(request));
   } else {
      event.respondWith(handleDynamicRequest(request));
   }
});

/**
 * Handle API requests with network-first strategy
 */
async function handleApiRequest(request) {
   const url = new URL(request.url);
   const isCacheableApi = CACHEABLE_APIS.some((api) =>
      url.pathname.startsWith(api)
   );
   const isNeverCacheApi = NEVER_CACHE_APIS.some((api) =>
      url.pathname.includes(api.replace("[id]", ""))
   );

   // NEVER cache certain APIs - always fetch fresh
   if (isNeverCacheApi) {
      console.log("🚫 Never cache API, fetching fresh:", url.pathname);
      try {
         return await fetch(request);
      } catch (error) {
         console.error("Critical API request failed:", error);
         return new Response(
            JSON.stringify({ error: "Network error, please try again" }),
            {
               status: 503,
               headers: { "Content-Type": "application/json" },
            }
         );
      }
   }

   if (!isCacheableApi) {
      // For non-cacheable APIs, just fetch from network
      try {
         return await fetch(request);
      } catch (error) {
         console.error("API request failed:", error);
         return new Response(
            JSON.stringify({ error: "Network error, please try again" }),
            {
               status: 503,
               headers: { "Content-Type": "application/json" },
            }
         );
      }
   }

   try {
      // Try network first
      const networkResponse = await fetch(request);

      if (networkResponse.ok) {
         // Cache successful responses
         const cache = await caches.open(API_CACHE);
         const responseClone = networkResponse.clone();

         // Add timestamp to track cache age
         const headers = new Headers(responseClone.headers);
         headers.set("sw-cached-at", Date.now().toString());

         const cachedResponse = new Response(responseClone.body, {
            status: responseClone.status,
            statusText: responseClone.statusText,
            headers: headers,
         });

         cache.put(request, cachedResponse);
         console.log("📦 Cached API response:", url.pathname);
      }

      return networkResponse;
   } catch (error) {
      // Network failed, try cache
      console.log("🌐 Network failed, checking cache for:", url.pathname);

      const cache = await caches.open(API_CACHE);
      const cachedResponse = await cache.match(request);

      if (cachedResponse) {
         const cachedAt = cachedResponse.headers.get("sw-cached-at");
         const age = cachedAt ? Date.now() - parseInt(cachedAt) : Infinity;

         // Check if cache is still valid
         if (age < CACHE_DURATIONS.API) {
            console.log("✅ Serving from cache:", url.pathname);
            return cachedResponse;
         } else {
            console.log("⏰ Cache expired for:", url.pathname);
         }
      }

      // Return offline fallback
      return new Response(
         JSON.stringify({
            error: "Offline mode - data unavailable",
            cached: false,
         }),
         {
            status: 503,
            headers: { "Content-Type": "application/json" },
         }
      );
   }
}

/**
 * Handle static assets with cache-first strategy
 */
async function handleStaticAsset(request) {
   const cache = await caches.open(STATIC_CACHE);
   const cachedResponse = await cache.match(request);

   if (cachedResponse) {
      // console.log("📦 Serving static asset from cache:", request.url);
      return cachedResponse;
   }

   try {
      const networkResponse = await fetch(request);

      if (networkResponse.ok) {
         // console.log("🌐 Caching new static asset:", request.url);
         cache.put(request, networkResponse.clone());
      }

      return networkResponse;
   } catch (error) {
      console.error("Failed to fetch static asset:", request.url, error);

      // Return a fallback for failed static assets
      return new Response("Asset unavailable offline", { status: 503 });
   }
}

/**
 * Handle dynamic requests (pages) with network-first strategy
 */
async function handleDynamicRequest(request) {
   try {
      const networkResponse = await fetch(request);

      if (networkResponse.ok) {
         // Cache successful page responses
         const cache = await caches.open(DYNAMIC_CACHE);
         cache.put(request, networkResponse.clone());
         // console.log("📦 Cached dynamic content:", request.url);
      }

      return networkResponse;
   } catch (error) {
      // Try cache fallback
      const cache = await caches.open(DYNAMIC_CACHE);
      const cachedResponse = await cache.match(request);

      if (cachedResponse) {
         // console.log("✅ Serving dynamic content from cache:", request.url);
         return cachedResponse;
      }

      // Return offline page fallback
      return new Response(
         `
         <!DOCTYPE html>
         <html>
         <head>
            <title>CompEx - Offline</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
               body { 
                  font-family: system-ui, sans-serif; 
                  text-align: center; 
                  padding: 2rem;
                  background: #f5f5f5;
               }
               .offline-container {
                  max-width: 400px;
                  margin: 2rem auto;
                  background: white;
                  padding: 2rem;
                  border-radius: 8px;
                  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
               }
               .offline-icon { font-size: 3rem; margin-bottom: 1rem; }
               .offline-title { font-size: 1.5rem; margin-bottom: 1rem; }
               .offline-message { color: #666; line-height: 1.5; }
               .retry-button {
                  background: #007bff;
                  color: white;
                  border: none;
                  padding: 0.75rem 1.5rem;
                  border-radius: 4px;
                  margin-top: 1rem;
                  cursor: pointer;
               }
            </style>
         </head>
         <body>
            <div class="offline-container">
               <div class="offline-icon">📡</div>
               <h1 class="offline-title">You're offline</h1>
               <p class="offline-message">
                  CompEx is currently unavailable. Please check your internet connection and try again.
               </p>
               <button class="retry-button" onclick="window.location.reload()">
                  Try Again
               </button>
            </div>
         </body>
         </html>
      `,
         {
            headers: { "Content-Type": "text/html" },
         }
      );
   }
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(request) {
   const url = new URL(request.url);
   const staticExtensions = [
      ".css",
      ".png",
      ".jpg",
      ".jpeg",
      ".gif",
      ".svg",
      ".ico",
      ".woff",
      ".woff2",
   ];

   // Include CSS and images, but be selective with JS
   const isStaticExtension = staticExtensions.some((ext) =>
      url.pathname.endsWith(ext)
   );
   const isNextStatic = url.pathname.startsWith("/_next/static/");

   // For JavaScript files, only cache certain types and exclude chunks that might contain server code
   if (url.pathname.endsWith(".js")) {
      // Don't cache JS chunks that might contain server-side code
      const problematicPatterns = [
         "question-attempt-service",
         "prisma",
         "server",
         "api",
      ];

      const isProblematic = problematicPatterns.some((pattern) =>
         url.pathname.toLowerCase().includes(pattern)
      );

      if (isProblematic) {
         console.log(
            "🚫 Skipping cache for potentially problematic JS:",
            url.pathname
         );
         return false;
      }

      // Only cache framework and vendor JS files
      return (
         url.pathname.includes("_next/static/") ||
         url.pathname.includes("webpack") ||
         url.pathname.includes("vendor") ||
         url.pathname.includes("framework") ||
         url.pathname.includes("main")
      );
   }

   return isStaticExtension || isNextStatic;
}

/**
 * Background sync for failed requests
 */
self.addEventListener("sync", (event) => {
   // console.log("🔄 Background sync event:", event.tag);

   if (event.tag === "background-sync") {
      event.waitUntil(doBackgroundSync());
   }
});

/**
 * Perform background sync operations
 */
async function doBackgroundSync() {
   try {
      // Implement background sync logic here
      // For example, retry failed user attempts
      console.log("🔄 Performing background sync...");

      // This could include:
      // - Retrying failed user attempt submissions
      // - Syncing cached user progress
      // - Updating cache with latest data

      console.log("✅ Background sync completed");
   } catch (error) {
      console.error("❌ Background sync failed:", error);
   }
}

/**
 * Handle messages from the main thread
 */
self.addEventListener("message", (event) => {
   // console.log("📨 Service worker received message:", event.data);

   switch (event.data.type) {
      case "SKIP_WAITING":
         self.skipWaiting();
         break;

      case "CLEAR_ALL_CACHES":
         event.waitUntil(clearAllCaches());
         break;

      case "CLEAR_JS_CACHE":
         event.waitUntil(clearJavaScriptCache());
         break;

      case "GET_CACHE_INFO":
         event.waitUntil(sendCacheInfo(event.ports[0]));
         break;

      case "FORCE_UPDATE":
         // Clear caches and refresh
         event.waitUntil(
            clearAllCaches().then(() => {
               self.clients.matchAll().then((clients) => {
                  clients.forEach((client) => {
                     client.postMessage({ type: "CACHE_CLEARED" });
                  });
               });
            })
         );
         break;
   }
});

/**
 * Clear all caches
 */
async function clearAllCaches() {
   try {
      const cacheNames = await caches.keys();
      await Promise.all(cacheNames.map((name) => caches.delete(name)));
      // console.log("🗑️ All caches cleared by service worker");
      return true;
   } catch (error) {
      console.error("❌ Failed to clear caches:", error);
      return false;
   }
}

/**
 * Clear only JavaScript-related caches
 */
async function clearJavaScriptCache() {
   try {
      const cache = await caches.open(STATIC_CACHE);
      const requests = await cache.keys();

      const jsRequests = requests.filter((request) =>
         request.url.endsWith(".js")
      );

      await Promise.all(jsRequests.map((request) => cache.delete(request)));
      // console.log("🗑️ JavaScript cache cleared");
      return true;
   } catch (error) {
      console.error("❌ Failed to clear JS cache:", error);
      return false;
   }
}

/**
 * Send cache information to main thread
 */
async function sendCacheInfo(port) {
   try {
      const cacheNames = await caches.keys();
      const info = {
         cacheNames,
         version: CACHE_VERSION,
         timestamp: Date.now(),
      };

      if (port) {
         port.postMessage({ type: "CACHE_INFO", data: info });
      }
   } catch (error) {
      console.error("❌ Failed to get cache info:", error);
   }
}

/**
 * Handle push notifications (for future use)
 */
self.addEventListener("push", (event) => {
   if (!event.data) return;

   const data = event.data.json();

   const options = {
      body: data.body,
      icon: "/icon-192x192.png",
      badge: "/icon-72x72.png",
      vibrate: [100, 50, 100],
      data: data.data,
      actions: data.actions || [],
   };

   event.waitUntil(self.registration.showNotification(data.title, options));
});

/**
 * Handle notification clicks
 */
self.addEventListener("notificationclick", (event) => {
   event.notification.close();

   if (event.action === "open") {
      event.waitUntil(clients.openWindow(event.notification.data.url || "/"));
   }
});

/**
 * Log service worker status
 */
// console.log("🚀 CompEx Service Worker loaded successfully");
// console.log("📦 Cache version:", CACHE_VERSION);
// console.log("🕒 Cache durations:", CACHE_DURATIONS);
