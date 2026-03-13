# Shared Directory

This directory contains reusable components, hooks, utilities, and styles that are used across multiple features.

## Structure

* **components**: Reusable UI components
  * **ui**: Design system components (buttons, inputs, modals)
  * **forms**: Form-related components
  * **layouts**: Layout components (headers, sidebars)
  * **feedback**: Loading and error states
* **hooks**: Custom React hooks
* **lib**: Utilities, configurations, and types
* **styles**: Global styles and themes

## Components

The components are organized by purpose:

### UI Components

Basic UI elements that follow design system principles:
- `button.tsx`: Button variants
- `input.tsx`: Input fields
- `modal.tsx`: Modal dialogs
- `data-table.tsx`: Data tables

### Form Components

Components for building forms:
- `form-field.tsx`: Form field wrapper
- `form-select.tsx`: Select dropdown
- `form-checkbox.tsx`: Checkbox input
- `validation-message.tsx`: Form validation messages

### Layout Components

Components for page structure:
- `header.tsx`: Application header
- `sidebar.tsx`: Navigation sidebar
- `footer.tsx`: Application footer
- `container.tsx`: Content container

### Feedback Components

Components for loading and error states:
- `loading-spinner.tsx`: Loading indicator
- `error-boundary.tsx`: Error handling
- `skeleton-loaders.tsx`: Content placeholders

## Hooks

Custom React hooks for common patterns:
- `use-async.ts`: Async operation handling
- `use-media-query.ts`: Responsive design
- `use-local-storage.ts`: Local storage access
- `use-debounce.ts`: Debounced values

## Integration with Features

- Components are imported by feature components
- Hooks are used in feature logic
- Utilities are used throughout the application
- Styles provide consistent theming

## Usage Example

```tsx
// In a feature component
import { Button } from '@/shared/components/ui/button';
import { useAsync } from '@/shared/hooks/use-async';
import { formatDate } from '@/shared/lib/utils/date-utils';

function MyFeatureComponent() {
  const { loading, data, error } = useAsync(fetchData);
  
  return (
    <div>
      <h2>{formatDate(data.date)}</h2>
      <Button onClick={handleAction}>Submit</Button>
    </div>
  );
}
```