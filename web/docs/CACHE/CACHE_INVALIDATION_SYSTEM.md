# Automatic Cache Invalidation System

This document describes the automatic cache invalidation system implemented in CompEx to solve the issue where code changes weren't reflected without hard refresh + cache clear.

## 🎯 Problem Solved

Before this implementation:
- Code changes required manual "Hard Refresh with Clear Cache" to be visible
- Users would see stale content even after deployments
- No way to automatically detect when new versions were available

After implementation:
- ✅ Automatic detection of code changes via build timestamp comparison
- ✅ Smart cache invalidation that only triggers when needed
- ✅ User-friendly notifications when updates are available
- ✅ Configurable update checking intervals
- ✅ Development-friendly with debug mode

## 🏗️ Architecture Overview

The system consists of several components working together:

### 1. Build Timestamp Generation (`scripts/generate-build-info.js`)
- Generates unique timestamps for each build
- Creates both JSON and TypeScript files with build information
- Runs automatically during `pnpm dev` and `pnpm build`

### 2. Version Checking API (`/api/version`)
- Provides current build information via HTTP endpoint
- Includes cache-busting headers to ensure fresh data
- Returns build timestamp, version, and environment info

### 3. Cache Invalidation Hook (`shared/hooks/use-cache-invalidation.ts`)
- Periodically checks for version updates (default: 30 seconds)
- Compares build timestamps to detect changes
- Provides configurable options for auto-reload and notifications

### 4. Update Notifications (`shared/components/feedback/update-notification.tsx`)
- Beautiful UI components to notify users of available updates
- Two variants: full notification and compact notification
- Animated with Framer Motion for smooth UX

### 5. Cache Invalidation Provider (`shared/components/providers/cache-invalidation-provider.tsx`)
- Wraps the entire application
- Manages update state and notifications
- Provides context for manual cache invalidation

### 6. Cache Utilities (`shared/lib/cache-utils.ts`)
- Utility functions for clearing various types of caches
- Integration with React Query, localStorage, sessionStorage
- Service Worker and IndexedDB cache clearing

## 🔧 Configuration

### Basic Setup (Already Configured)

The system is automatically active with these default settings:

```typescript
// In app/layout.tsx
<CacheInvalidationProvider
  checkInterval={30000}          // Check every 30 seconds
  compactNotification={false}    // Show full notification
  debug={process.env.NODE_ENV === 'development'} // Debug mode in dev
>
```

### Customizable Options

```typescript
interface CacheInvalidationOptions {
  checkInterval?: number;        // How often to check (default: 30s)
  autoReload?: boolean;         // Auto-reload without user confirmation
  showNotification?: boolean;   // Show UI notifications
  debug?: boolean;             // Enable debug logging
}
```

### Environment-Specific Behavior

#### Development Mode
- ✅ Build info generated on every `pnpm dev` start
- ✅ Debug logging enabled
- ✅ Shorter cache durations (1 minute for static assets)
- ✅ Debug UI shows current status

#### Production Mode
- ✅ Build info generated during build process
- ✅ Longer cache durations for performance
- ✅ Clean user notifications without debug info
- ✅ Optimized checking intervals

## 🚀 How It Works

### 1. Build Time
```bash
# Development
pnpm dev → generates build-info.json → starts dev server

# Production
pnpm build → updates version → generates build-info.json → builds app
```

### 2. Runtime Detection
```
User loads page → Cache invalidation starts → Periodic checks every 30s
                                           ↓
API call to /api/version → Compare timestamps → Update detected?
                                           ↓                 ↓
                                         No               Yes
                                           ↓                 ↓
                                    Continue checking    Show notification
                                                              ↓
                                                        User clicks refresh
                                                              ↓
                                                     Clear all caches + reload
```

### 3. Cache Types Cleared
When an update is detected and user confirms refresh:

1. **Browser Storage**
   - localStorage
   - sessionStorage

2. **React Query Cache**
   - All query data
   - Query metadata

3. **Service Worker Caches**
   - All registered cache entries

4. **IndexedDB** (if used)
   - Database entries

5. **Browser Cache**
   - Force reload with cache busting parameters

## 📁 File Structure

```
compex/
├── scripts/
│   └── generate-build-info.js           # Build timestamp generator
├── app/
│   ├── layout.tsx                       # Provider integration
│   └── api/version/route.ts             # Version checking endpoint
├── shared/
│   ├── hooks/
│   │   └── use-cache-invalidation.ts    # Main invalidation hook
│   ├── components/
│   │   ├── providers/
│   │   │   └── cache-invalidation-provider.tsx  # App-wide provider
│   │   └── feedback/
│   │       └── update-notification.tsx  # Notification components
│   └── lib/
│       ├── cache-utils.ts               # Cache clearing utilities
│       └── build-info.ts                # Generated build info (auto)
├── public/
│   └── build-info.json                  # Generated build info (auto)
└── docs/
    └── CACHE_INVALIDATION_SYSTEM.md     # This documentation
```

## 🎛️ Manual Usage

### Check for Updates Manually
```typescript
import { useCacheInvalidationContext } from '@/shared/components/providers/cache-invalidation-provider';

function MyComponent() {
  const { checkForUpdates, updateAvailable } = useCacheInvalidationContext();
  
  return (
    <button onClick={checkForUpdates}>
      Check for Updates {updateAvailable && '(Update Available!)'}
    </button>
  );
}
```

### Force Cache Invalidation
```typescript
import { useManualCacheInvalidation } from '@/shared/components/providers/cache-invalidation-provider';

function MyComponent() {
  const invalidateCache = useManualCacheInvalidation();
  
  return (
    <button onClick={invalidateCache}>
      Force Refresh
    </button>
  );
}
```

### Use Cache Utilities Directly
```typescript
import { clearAllCaches, forceReload, softReload } from '@/shared/lib/cache-utils';

// Clear all caches but stay on page
await clearAllCaches();

// Force complete page reload with cache bust
forceReload();

// Try soft reload (invalidate queries + navigate)
softReload();
```

## 🔧 Cache Headers Configuration

The system includes optimized cache headers in `next.config.mjs`:

```javascript
// API routes - never cached
'/api/*' → 'no-store, no-cache, must-revalidate'

// Version endpoint - extra cache busting
'/api/version' → 'no-store, no-cache, must-revalidate, proxy-revalidate'

// Build info - never cached  
'/build-info.json' → 'no-store, no-cache, must-revalidate'

// Static assets - cached but shorter in dev
'*.js,*.css,*.png' → dev: 'max-age=60' | prod: 'max-age=31536000'

// HTML pages - smart caching
'/' → dev: 'no-cache' | prod: 'max-age=0, s-maxage=86400, must-revalidate'
```

## 🐛 Debug Mode

In development, enable debug mode to see detailed logging:

```typescript
// Debug panel shows:
- Current checking status
- Update availability
- Last check timestamp  
- Error messages
- Build version info
- Manual check button
```

## 📊 Performance Impact

### Minimal Overhead
- ✅ Single API call every 30 seconds (configurable)
- ✅ Lightweight JSON response (~200 bytes)
- ✅ No blocking operations
- ✅ Smart caching prevents excessive checks

### Network Usage
- **Development**: ~1KB per minute (debug info)
- **Production**: ~200 bytes per minute

### Memory Usage
- Negligible - simple interval timer and state

## 🔒 Security Considerations

- ✅ Version endpoint only exposes build metadata (no sensitive info)
- ✅ No user data in build information
- ✅ Cache invalidation happens client-side only
- ✅ No server-side state changes

## 🧪 Testing the System

### 1. Test in Development
```bash
# Terminal 1: Start dev server
pnpm dev

# Terminal 2: Make code changes and save
echo "console.log('test change');" >> app/page.tsx

# Result: You should see debug info showing update detection
```

### 2. Test Build Timestamp Generation
```bash
node scripts/generate-build-info.js

# Check generated files:
cat public/build-info.json
cat shared/lib/build-info.ts
```

### 3. Test API Endpoint
```bash
curl http://localhost:3001/api/version
# Should return fresh build info each time
```

## 📋 Troubleshooting

### Issue: Updates Not Detected
```bash
# Check if build info is generated
ls -la public/build-info.json shared/lib/build-info.ts

# Check API endpoint
curl http://localhost:3001/api/version

# Check browser console for debug logs (dev mode)
```

### Issue: Notifications Not Showing
```typescript
// Check provider is properly wrapped
// Verify notification state in React DevTools
// Check browser notification permissions
```

### Issue: Cache Not Clearing
```typescript
// Check browser console for cache clearing logs
// Verify React Query client is available globally
// Check service worker registration
```

## 🚀 Benefits Achieved

1. **Developer Experience**
   - ✅ No more manual hard refresh needed
   - ✅ Automatic detection of code changes
   - ✅ Visual feedback when updates are ready

2. **User Experience**  
   - ✅ Always see latest version without confusion
   - ✅ Smooth update process with notifications
   - ✅ No stale content after deployments

3. **Production Reliability**
   - ✅ Guaranteed cache invalidation on deployments
   - ✅ Minimal performance impact
   - ✅ Graceful handling of network issues

4. **Maintenance**
   - ✅ Zero configuration needed for basic usage
   - ✅ Comprehensive debugging tools
   - ✅ Flexible and customizable system

## 📝 Future Enhancements

Possible improvements for the future:

1. **Service Worker Integration**
   - Background sync for update detection
   - Offline update queuing

2. **Selective Cache Invalidation**
   - Only invalidate affected query keys
   - Route-specific cache clearing

3. **Update Scheduling**
   - Allow users to schedule updates
   - Update during low-activity periods

4. **Analytics Integration**
   - Track update adoption rates
   - Monitor cache invalidation performance

---

**✅ System is now fully operational and will automatically handle cache invalidation for all future code changes!**