# Shared Styles

This directory contains global styling configurations, theme definitions, and shared CSS utilities for the application.

## Overview

The application uses a modern styling approach with:
- **Tailwind CSS** for utility-first styling
- **CSS Custom Properties** for theme variables
- **shadcn/ui** component system
- **next-themes** for dark/light mode support
- **Class Variance Authority (CVA)** for component variants

## Styling Architecture

### Global Styles

The main global styles are defined in `/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    /* ... more CSS custom properties */
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark mode overrides */
  }
}
```

### Theme System

#### Color Palette

The application uses a semantic color system:

**Light Mode:**
- `--background`: Main background color
- `--foreground`: Primary text color
- `--primary`: Brand primary color
- `--secondary`: Secondary accent color
- `--muted`: Subtle background color
- `--border`: Border color
- `--destructive`: Error/danger color

**Dark Mode:**
- Automatically switches using CSS custom properties
- Maintains semantic meaning across themes
- Optimized for accessibility and readability

#### Chart Colors

Special color variables for data visualization:
```css
--chart-1: 217.2 91.2% 59.8%;
--chart-2: 142.1 70.6% 45.3%;
--chart-3: 47.9 95.8% 53.1%;
--chart-4: 346.8 77.2% 49.8%;
--chart-5: 262.1 83.3% 67.8%;
```

### Tailwind Configuration

Located in `/config/tailwind.config.ts`:

```typescript
const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./shared/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ... more color definitions
      },
      fontFamily: {
        primary1: "var(--font-primary-1)",
        primary2: "var(--font-primary-2)",
        // ... more font definitions
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
```

### Component Styling

#### shadcn/ui Integration

The application uses shadcn/ui components with configuration in `/config/components.json`:

```json
{
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  }
}
```

#### Component Variants

Using Class Variance Authority (CVA) for component styling:

```typescript
const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
      },
    },
  }
);
```

## Theme Management

### Theme Provider

The application uses `next-themes` for theme management:

```typescript
<NextThemesProvider
  attribute="class"
  defaultTheme="system"
  enableSystem={true}
  disableTransitionOnChange={false}
  storageKey="compex-theme-preference"
>
  {children}
</NextThemesProvider>
```

### Theme Utilities

Located in `/shared/lib/configs/theme.ts`:

```typescript
// Get current theme
export function getTheme(): 'light' | 'dark' | 'system';

// Check if current theme is dark
export function isDarkTheme(): boolean;

// Get chart colors based on theme
export function getChartColors(isDark: boolean);
```

### Theme Toggle Component

Provides user interface for theme switching:
- Light mode
- Dark mode  
- System preference
- Prevents hydration mismatch
- Smooth transitions

## Directory Structure

```
shared/styles/
├── README.md          # This file
└── themes/           # Theme-specific configurations
    └── README.md     # Theme documentation
```

## Usage Guidelines

### Using Theme Colors

```tsx
// In components, use semantic color classes
<div className="bg-background text-foreground">
  <button className="bg-primary text-primary-foreground hover:bg-primary/90">
    Click me
  </button>
</div>
```

### Custom CSS Properties

```css
/* Access theme variables in custom CSS */
.custom-component {
  background-color: hsl(var(--muted));
  border: 1px solid hsl(var(--border));
  color: hsl(var(--muted-foreground));
}
```

### Responsive Design

```tsx
// Use Tailwind responsive prefixes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>
```

### Component Styling

```tsx
// Use CVA for component variants
const cardVariants = cva(
  "rounded-lg border bg-card text-card-foreground shadow-sm",
  {
    variants: {
      size: {
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      },
    },
  }
);
```

## Best Practices

### Color Usage

1. **Use Semantic Colors**: Always use semantic color names (primary, secondary, muted) instead of specific colors
2. **Theme Consistency**: Ensure colors work in both light and dark modes
3. **Accessibility**: Maintain proper contrast ratios
4. **Chart Colors**: Use designated chart color variables for data visualization

### Performance

1. **Utility Classes**: Prefer Tailwind utility classes over custom CSS
2. **CSS-in-JS**: Avoid runtime CSS-in-JS for better performance
3. **Critical CSS**: Inline critical styles for above-the-fold content
4. **Purging**: Tailwind automatically purges unused styles

### Maintainability

1. **Component Variants**: Use CVA for complex component styling
2. **Design Tokens**: Use CSS custom properties for consistent theming
3. **Documentation**: Document custom styling patterns
4. **Testing**: Test components in both light and dark modes

## Future Enhancements

- Add more theme variants (high contrast, colorblind-friendly)
- Implement CSS-in-JS solution for dynamic theming
- Add animation and transition utilities
- Create design system documentation
- Add RTL (right-to-left) language support
