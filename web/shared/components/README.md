# Shared Components

This directory contains reusable UI components that are used across multiple features.

## Structure

* **ui/**: Design system components
* **forms/**: Form-related components
* **layouts/**: Layout components
* **feedback/**: Loading and error states
* **data-display/**: Data visualization components

## UI Components

Basic UI elements following design system principles:

- `button.tsx`: Button variants (primary, secondary, outline)
- `input.tsx`: Text input fields
- `select.tsx`: Dropdown select
- `checkbox.tsx`: Checkbox input
- `radio.tsx`: Radio button input
- `modal.tsx`: Modal dialog
- `card.tsx`: Content card
- `badge.tsx`: Status badge
- `tooltip.tsx`: Information tooltip

## Form Components

Components for building forms:

- `form-field.tsx`: Form field wrapper with label
- `form-select.tsx`: Enhanced select dropdown
- `form-checkbox.tsx`: Enhanced checkbox
- `validation-message.tsx`: Form validation error message
- `form-group.tsx`: Group of related form fields

## Layout Components

Components for page structure:

- `header.tsx`: Application header with navigation
- `sidebar.tsx`: Navigation sidebar
- `footer.tsx`: Application footer
- `container.tsx`: Content container with responsive width
- `grid.tsx`: Grid layout system

## Feedback Components

Components for loading and error states:

- `loading-spinner.tsx`: Loading indicator
- `error-boundary.tsx`: Error handling component
- `skeleton-loaders.tsx`: Content placeholders
- `alert.tsx`: Alert messages (success, error, warning)
- `progress.tsx`: Progress indicators

## Usage Guidelines

1. **Import Path**: Import components using the `@/shared/components` path
2. **Composition**: Compose complex components from simpler ones
3. **Props**: Use consistent prop naming across components
4. **Styling**: Use Tailwind classes for styling
5. **Accessibility**: Ensure all components are accessible

## Example Usage

```tsx
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { FormField } from '@/shared/components/forms/form-field';
import { Card } from '@/shared/components/ui/card';

function LoginForm() {
  return (
    <Card>
      <form>
        <FormField label="Email">
          <Input type="email" placeholder="Enter your email" />
        </FormField>
        <FormField label="Password">
          <Input type="password" placeholder="Enter your password" />
        </FormField>
        <Button type="submit">Log In</Button>
      </form>
    </Card>
  );
}
```

## Integration with Features

These components are used by feature-specific components to maintain consistency across the application while allowing features to implement their specific business logic.