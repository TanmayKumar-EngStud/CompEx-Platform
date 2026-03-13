# Shared Hooks

This directory contains reusable React hooks that provide common functionality across the application.

## Available Hooks

* **use-async.ts**: Manages async operations with loading, error, and data states
* **use-debounce.ts**: Debounces values to reduce unnecessary renders
* **use-local-storage.ts**: Persists and retrieves data from localStorage
* **use-media-query.ts**: Responds to media query changes for responsive design
* **use-outside-click.ts**: Detects clicks outside a referenced element
* **use-previous.ts**: Keeps track of previous values
* **use-toggle.ts**: Toggles boolean state
* **use-window-size.ts**: Tracks window dimensions

## Usage Examples

### use-async.ts

```tsx
import { useAsync } from '@/shared/hooks/use-async';

function UserProfile({ userId }) {
  const { 
    data: user, 
    loading, 
    error, 
    execute: fetchUser 
  } = useAsync(() => fetchUserData(userId), [userId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return <ProfileDisplay user={user} onRefresh={fetchUser} />;
}
```

### use-debounce.ts

```tsx
import { useDebounce } from '@/shared/hooks/use-debounce';

function SearchBar() {
  const [input, setInput] = useState('');
  const debouncedInput = useDebounce(input, 500);
  
  useEffect(() => {
    // Only called 500ms after input stops changing
    searchAPI(debouncedInput);
  }, [debouncedInput]);
  
  return <input value={input} onChange={e => setInput(e.target.value)} />;
}
```

## Integration with Features

These hooks are used throughout feature components to:
- Manage common UI patterns
- Handle data fetching and state
- Improve performance
- Enhance user experience

## Creating New Hooks

When creating new shared hooks:

1. Focus on a single responsibility
2. Make them reusable across features
3. Include proper TypeScript typing
4. Add JSDoc comments for documentation
5. Consider edge cases and error handling