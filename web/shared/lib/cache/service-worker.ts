/**
 * Service Worker Registration and Management
 * 
 * Handles service worker lifecycle, updates, and cache management
 * with intelligent registration and error handling.
 */

export interface ServiceWorkerStatus {
   isSupported: boolean;
   isRegistered: boolean;
   isActive: boolean;
   updateAvailable: boolean;
   error: string | null;
}

export interface CacheInfo {
   name: string;
   size: number;
   lastModified: Date;
}

/**
 * Service Worker Manager
 */
export class ServiceWorkerManager {
   private registration: ServiceWorkerRegistration | null = null;
   private status: ServiceWorkerStatus = {
      isSupported: false,
      isRegistered: false,
      isActive: false,
      updateAvailable: false,
      error: null,
   };
   private updateCallbacks: Array<(hasUpdate: boolean) => void> = [];

   /**
    * Initialize service worker
    */
   async initialize(): Promise<ServiceWorkerStatus> {
      try {
         // Check if service workers are supported
         if (!('serviceWorker' in navigator)) {
            this.status.error = 'Service workers not supported';
            return this.status;
         }

         this.status.isSupported = true;

         // Register service worker
         this.registration = await navigator.serviceWorker.register('/sw.js', {
            scope: '/',
         });

         this.status.isRegistered = true;

         // Set up event listeners
         this.setupEventListeners();

         // Check if service worker is active
         this.status.isActive = !!this.registration.active;

         // Check for updates
         await this.checkForUpdates();

         console.log('✅ Service Worker registered successfully');
         return this.status;

      } catch (error) {
         this.status.error = error instanceof Error ? error.message : 'Unknown error';
         console.error('❌ Service Worker registration failed:', error);
         return this.status;
      }
   }

   /**
    * Setup service worker event listeners
    */
   private setupEventListeners(): void {
      if (!this.registration) return;

      // Listen for service worker updates
      this.registration.addEventListener('updatefound', () => {
         const newWorker = this.registration!.installing;
         if (newWorker) {
            console.log('🔄 New service worker found, installing...');
            
            newWorker.addEventListener('statechange', () => {
               if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  console.log('🆕 New service worker installed, update available');
                  this.status.updateAvailable = true;
                  this.notifyUpdateCallbacks(true);
               }
            });
         }
      });

      // Listen for service worker control
      navigator.serviceWorker.addEventListener('controllerchange', () => {
         console.log('🔄 Service worker controller changed');
         this.status.isActive = true;
      });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', (event) => {
         this.handleServiceWorkerMessage(event.data);
      });
   }

   /**
    * Handle messages from service worker
    */
   private handleServiceWorkerMessage(data: any): void {
      switch (data.type) {
         case 'CACHE_UPDATED':
            console.log('📦 Cache updated:', data.cacheName);
            break;
         case 'OFFLINE_READY':
            console.log('📡 Application ready for offline use');
            break;
         case 'UPDATE_AVAILABLE':
            this.status.updateAvailable = true;
            this.notifyUpdateCallbacks(true);
            break;
         default:
            console.log('📨 Service worker message:', data);
      }
   }

   /**
    * Check for service worker updates
    */
   async checkForUpdates(): Promise<boolean> {
      if (!this.registration) {
         return false;
      }

      try {
         await this.registration.update();
         return this.status.updateAvailable;
      } catch (error) {
         console.error('❌ Failed to check for updates:', error);
         return false;
      }
   }

   /**
    * Apply pending service worker update
    */
   async applyUpdate(): Promise<void> {
      if (!this.registration || !this.status.updateAvailable) {
         return;
      }

      const newWorker = this.registration.waiting || this.registration.installing;
      if (newWorker) {
         // Send skip waiting message
         newWorker.postMessage({ type: 'SKIP_WAITING' });
         
         // Wait for controller change
         await new Promise<void>((resolve) => {
            const handleControllerChange = () => {
               navigator.serviceWorker.removeEventListener('controllerchange', handleControllerChange);
               resolve();
            };
            navigator.serviceWorker.addEventListener('controllerchange', handleControllerChange);
         });

         // Reload the page to use new service worker
         window.location.reload();
      }
   }

   /**
    * Unregister service worker
    */
   async unregister(): Promise<boolean> {
      if (!this.registration) {
         return false;
      }

      try {
         const result = await this.registration.unregister();
         if (result) {
            this.status.isRegistered = false;
            this.status.isActive = false;
            console.log('✅ Service worker unregistered');
         }
         return result;
      } catch (error) {
         console.error('❌ Failed to unregister service worker:', error);
         return false;
      }
   }

   /**
    * Get cache information
    */
   async getCacheInfo(): Promise<CacheInfo[]> {
      if (!('caches' in window)) {
         return [];
      }

      try {
         const cacheNames = await caches.keys();
         const cacheInfos: CacheInfo[] = [];

         for (const name of cacheNames) {
            const cache = await caches.open(name);
            const keys = await cache.keys();
            
            // Estimate cache size
            let size = 0;
            for (const request of keys) {
               const response = await cache.match(request);
               if (response) {
                  const blob = await response.blob();
                  size += blob.size;
               }
            }

            cacheInfos.push({
               name,
               size,
               lastModified: new Date(), // Approximate
            });
         }

         return cacheInfos;
      } catch (error) {
         console.error('❌ Failed to get cache info:', error);
         return [];
      }
   }

   /**
    * Clear all caches
    */
   async clearCaches(): Promise<boolean> {
      if (!('caches' in window)) {
         return false;
      }

      try {
         const cacheNames = await caches.keys();
         const deletePromises = cacheNames.map(name => caches.delete(name));
         await Promise.all(deletePromises);
         
         console.log('🗑️ All caches cleared');
         return true;
      } catch (error) {
         console.error('❌ Failed to clear caches:', error);
         return false;
      }
   }

   /**
    * Clear specific cache
    */
   async clearCache(cacheName: string): Promise<boolean> {
      if (!('caches' in window)) {
         return false;
      }

      try {
         const result = await caches.delete(cacheName);
         if (result) {
            console.log(`🗑️ Cache '${cacheName}' cleared`);
         }
         return result;
      } catch (error) {
         console.error(`❌ Failed to clear cache '${cacheName}':`, error);
         return false;
      }
   }

   /**
    * Get current service worker status
    */
   getStatus(): ServiceWorkerStatus {
      return { ...this.status };
   }

   /**
    * Subscribe to update notifications
    */
   onUpdate(callback: (hasUpdate: boolean) => void): () => void {
      this.updateCallbacks.push(callback);
      
      // Return unsubscribe function
      return () => {
         const index = this.updateCallbacks.indexOf(callback);
         if (index > -1) {
            this.updateCallbacks.splice(index, 1);
         }
      };
   }

   /**
    * Notify all update callbacks
    */
   private notifyUpdateCallbacks(hasUpdate: boolean): void {
      this.updateCallbacks.forEach(callback => {
         try {
            callback(hasUpdate);
         } catch (error) {
            console.error('❌ Error in update callback:', error);
         }
      });
   }

   /**
    * Send message to service worker
    */
   async sendMessage(message: any, ports?: MessagePort[]): Promise<void> {
      if (!navigator.serviceWorker.controller) {
         throw new Error('No active service worker');
      }

      if (ports) {
         navigator.serviceWorker.controller.postMessage(message, ports);
      } else {
         navigator.serviceWorker.controller.postMessage(message);
      }
   }

   /**
    * Prefetch resources
    */
   async prefetchResources(urls: string[]): Promise<void> {
      await this.sendMessage({
         type: 'PREFETCH_RESOURCES',
         urls,
      });
   }
}

/**
 * Singleton service worker manager
 */
let serviceWorkerManager: ServiceWorkerManager | null = null;

export function getServiceWorkerManager(): ServiceWorkerManager {
   if (!serviceWorkerManager) {
      serviceWorkerManager = new ServiceWorkerManager();
   }
   return serviceWorkerManager;
}

/**
 * Initialize service worker with default configuration
 */
export async function initializeServiceWorker(): Promise<ServiceWorkerStatus> {
   const manager = getServiceWorkerManager();
   return await manager.initialize();
}

/**
 * Check if the app is offline
 */
export function isOffline(): boolean {
   return !navigator.onLine;
}

/**
 * Setup offline/online event listeners
 */
export function setupOfflineDetection(): void {
   const handleOnline = () => {
      console.log('🌐 Application is online');
      document.body.classList.remove('offline');
      
      // Notify service worker that we're online
      const manager = getServiceWorkerManager();
      manager.sendMessage({ type: 'ONLINE' }).catch(console.warn);
   };

   const handleOffline = () => {
      console.log('📡 Application is offline');
      document.body.classList.add('offline');
      
      // Notify service worker that we're offline
      const manager = getServiceWorkerManager();
      manager.sendMessage({ type: 'OFFLINE' }).catch(console.warn);
   };

   window.addEventListener('online', handleOnline);
   window.addEventListener('offline', handleOffline);

   // Set initial state
   if (isOffline()) {
      handleOffline();
   }
}

/**
 * Format cache size for display
 */
export function formatCacheSize(bytes: number): string {
   if (bytes === 0) return '0 B';
   const k = 1024;
   const sizes = ['B', 'KB', 'MB', 'GB'];
   const i = Math.floor(Math.log(bytes) / Math.log(k));
   return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}