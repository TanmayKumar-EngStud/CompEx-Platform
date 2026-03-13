# Service Worker Cache Fix - Usage Guide

## Problem Solved

The issue where service worker was caching old JavaScript code that contained Prisma client-side code, causing the error:
```
PrismaClient is unable to run in this browser environment, or has been bundled for the browser
```

## Solution Implemented

### 1. **Updated Service Worker** (`/public/sw.js`)
- **Cache version bumped** to `compex-v1.1.0` to force cache refresh
- **Selective JS caching** - excludes problematic files containing server-side code
- **Never-cache APIs** - submission endpoints always fetch fresh
- **Manual cache clearing** - service worker can clear caches on command

### 2. **Cache Refresh Utilities** (`/shared/lib/cache/cache-refresh-utils.ts`)
- **Automatic error detection** - detects Prisma client-side errors
- **Force refresh mechanism** - clears all caches and reloads
- **Smart cache management** - preserves user preferences while clearing problematic cache

### 3. **Error Handler Component** (`/shared/components/error-handling/PrismaErrorHandler.tsx`)
- **Automatic error handling** - wraps components to catch and handle errors
- **User-friendly interface** - shows refresh options when errors occur
- **Development debugging** - shows error details in dev mode

## Quick Integration

### Option 1: Wrap Your Question Window (Recommended)

```tsx
// In your existing question window component
import PrismaErrorHandler from '@/shared/components/error-handling/PrismaErrorHandler';

function QuestionWindow() {
  return (
    <PrismaErrorHandler autoRefresh={true}>
      {/* Your existing question window content */}
      <QuestionAttempt onClose={handleClose} />
    </PrismaErrorHandler>
  );
}
```

### Option 2: Initialize Auto-Refresh Globally

```tsx
// In your app root or layout
import { initializeCacheRefresh } from '@/shared/lib/cache/cache-refresh-utils';

export default function RootLayout({ children }) {
  useEffect(() => {
    initializeCacheRefresh(); // Sets up automatic error detection
  }, []);

  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

### Option 3: Manual Error Handling

```tsx
// In components that submit data
import { usePrismaErrorHandler } from '@/shared/components/error-handling/PrismaErrorHandler';

function SubmitButton() {
  const { handleError } = usePrismaErrorHandler();
  
  const handleSubmit = async () => {
    try {
      await submitUserAttempt(data);
    } catch (error) {
      const wasHandled = await handleError(error);
      if (!wasHandled) {
        // Handle other types of errors
        console.error('Other error:', error);
      }
    }
  };
}
```

## How It Works

### 1. **Cache Version Control**
When you deploy updates:
- Service worker version changes from `compex-v1.0.0` to `compex-v1.1.0`
- Browser automatically clears old cache and downloads fresh files
- Old problematic JavaScript is replaced with fixed version

### 2. **Selective Caching**
Service worker now:
- ✅ Caches CSS, images, fonts (safe static assets)
- ✅ Caches framework JS files (webpack, vendor bundles)
- ❌ Skips caching JS files with server-side patterns
- ❌ Never caches submission APIs (`/api/problems/returnAttempt`)

### 3. **Automatic Error Recovery**
When Prisma error occurs:
1. **Detection** - Error handler detects the specific error pattern
2. **Cache Clear** - All caches (browser + service worker) are cleared
3. **Reload** - Page reloads with fresh code
4. **User Feedback** - User sees friendly "updating..." message

## Testing the Fix

### 1. **Force the Error** (to verify fix works)
```js
// In browser console, simulate the old error:
console.log('Testing error handler...');
window.dispatchEvent(new ErrorEvent('error', {
  error: new Error('PrismaClient is unable to run in this browser environment')
}));
```

### 2. **Verify Cache Clearing**
```js
// Check cache info:
import { getCacheRefreshManager } from '@/shared/lib/cache/cache-refresh-utils';
const manager = getCacheRefreshManager();
manager.getCacheInfo().then(console.log);
```

### 3. **Manual Refresh**
```js
// Force refresh caches:
manager.forceRefresh();
```

## Development Tools

### Debug Button (Development Only)
In development mode, a red "🔄 Force Refresh Cache" button appears in the top-right corner for testing.

### Console Logging
Service worker logs all caching decisions:
- `🚫 Skipping cache for potentially problematic JS` - JS files excluded
- `🚫 Never cache API, fetching fresh` - API calls that bypass cache
- `🗑️ All caches cleared by service worker` - Manual cache clear

## Deployment Checklist

1. ✅ **Service worker updated** - Cache version bumped
2. ✅ **Error handlers in place** - Automatic error detection
3. ✅ **Selective caching** - Problematic files excluded
4. ✅ **API exclusions** - Submission endpoints never cached

## Expected Behavior

### After Normal Reload:
- ✅ Question display works properly
- ✅ Form submission works without Prisma errors
- ✅ Fast loading from appropriate caches
- ✅ Fresh data for submissions

### After Empty Cache + Hard Reload:
- ✅ Everything works (as before)
- ✅ All caches rebuilt with fresh code
- ✅ Service worker updated to new version

## Monitoring

Monitor browser console for:
- `✅ Service Worker activated` - New version deployed
- `🗑️ Deleting old cache: compex-v1.0.0-*` - Old cache cleaned up
- `📦 Cache version: compex-v1.1.0` - New version active

## Troubleshooting

### If Prisma Error Still Occurs:
1. **Check service worker version** - Should be `compex-v1.1.0`
2. **Manual cache clear** - Use browser DevTools > Application > Storage > Clear storage
3. **Verify error handler** - Check console for `🚨 Detected Prisma error`

### If Automatic Refresh Doesn't Work:
1. **Check console errors** - Error handler may have failed
2. **Manual refresh** - Use the debug button or call `manager.forceRefresh()`
3. **Hard reload** - Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

The solution ensures that your application automatically recovers from cache-related issues without requiring users to manually clear their browser cache.