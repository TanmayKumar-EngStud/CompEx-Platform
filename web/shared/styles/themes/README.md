# Themes

This directory contains theme-specific configurations and customizations for the application.

## Overview

Currently, the application uses a CSS custom properties-based theming system with light and dark mode support. This directory is prepared for future theme expansions and customizations.

## Current Theme System

### Base Themes

The application currently supports:

1. **Light Theme** (default)
2. **Dark Theme** 
3. **System Theme** (follows OS preference)

### Theme Implementation

Themes are implemented using CSS custom properties defined in `/app/globals.css`:

```css
@layer base {
  :root {
    /* Light theme variables */
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... more variables */
  }
  
  .dark {
    /* Dark theme overrides */
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 84% 4.9%;
    /* ... more overrides */
  }
}
```

## Theme Structure

### Color Tokens

Each theme defines the following semantic color tokens:

#### Background Colors
- `--background`: Main application background
- `--card`: Card/panel background
- `--popover`: Popover/dropdown background
- `--muted`: Subtle background for less prominent elements

#### Text Colors
- `--foreground`: Primary text color
- `--card-foreground`: Text on card backgrounds
- `--popover-foreground`: Text on popover backgrounds
- `--muted-foreground`: Subtle text color

#### Brand Colors
- `--primary`: Primary brand color
- `--primary-foreground`: Text on primary background
- `--secondary`: Secondary accent color
- `--secondary-foreground`: Text on secondary background

#### Interactive Colors
- `--accent`: Hover/focus states
- `--accent-foreground`: Text on accent background
- `--destructive`: Error/danger color
- `--destructive-foreground`: Text on destructive background

#### UI Elements
- `--border`: Border color
- `--input`: Input field border
- `--ring`: Focus ring color

#### Data Visualization
- `--chart-1` through `--chart-5`: Colors for charts and graphs

## Theme Management

### Theme Provider Configuration

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

The application provides utility functions for theme management:

```typescript
// Get current theme preference
function getTheme(): 'light' | 'dark' | 'system';

// Check if current resolved theme is dark
function isDarkTheme(): boolean;

// Get theme-appropriate chart colors
function getChartColors(isDark: boolean);
```

## Future Theme Expansions

This directory is structured to support additional themes:

### Planned Theme Variants

1. **High Contrast Theme**
   - Enhanced contrast ratios for accessibility
   - Bold color differences
   - Improved visibility for users with visual impairments

2. **Colorblind-Friendly Theme**
   - Colors chosen for colorblind accessibility
   - Alternative visual indicators beyond color
   - Tested with colorblind simulation tools

3. **Brand Themes**
   - Institution-specific color schemes
   - Custom branding integration
   - Logo and accent color customization

4. **Seasonal Themes**
   - Holiday or seasonal color variations
   - Temporary theme overlays
   - Special event theming

### Theme File Structure

Future themes would be organized as:

```
themes/
├── README.md
├── high-contrast/
│   ├── colors.css
│   ├── components.css
│   └── variables.css
├── colorblind-friendly/
│   ├── colors.css
│   └── variables.css
├── brand/
│   ├── institution-a.css
│   ├── institution-b.css
│   └── custom.css
└── seasonal/
    ├── winter.css
    ├── spring.css
    └── holiday.css
```

## Creating Custom Themes

### Theme Definition Template

```css
/* Custom theme: theme-name.css */
.theme-name {
  /* Background colors */
  --background: [hsl values];
  --foreground: [hsl values];
  
  /* Brand colors */
  --primary: [hsl values];
  --primary-foreground: [hsl values];
  
  /* Interactive colors */
  --accent: [hsl values];
  --accent-foreground: [hsl values];
  
  /* UI elements */
  --border: [hsl values];
  --input: [hsl values];
  
  /* Chart colors */
  --chart-1: [hsl values];
  --chart-2: [hsl values];
  --chart-3: [hsl values];
  --chart-4: [hsl values];
  --chart-5: [hsl values];
}
```

### Theme Integration Steps

1. **Create Theme File**: Define CSS custom properties
2. **Update Theme Provider**: Add theme to available options
3. **Add Theme Toggle**: Include in theme selection UI
4. **Test Accessibility**: Verify contrast ratios and usability
5. **Document Usage**: Add theme-specific documentation

### Theme Testing Checklist

- [ ] All semantic colors defined
- [ ] Proper contrast ratios (WCAG AA compliance)
- [ ] Chart colors are distinguishable
- [ ] Interactive states are clear
- [ ] Components render correctly
- [ ] Dark/light mode compatibility
- [ ] Mobile responsiveness maintained

## Accessibility Considerations

### Color Contrast

All themes must meet WCAG 2.1 AA standards:
- Normal text: 4.5:1 contrast ratio minimum
- Large text: 3:1 contrast ratio minimum
- Interactive elements: 3:1 contrast ratio minimum

### Visual Indicators

Themes should not rely solely on color to convey information:
- Use icons alongside color coding
- Provide text labels for status indicators
- Include patterns or shapes for differentiation

### Testing Tools

Recommended tools for theme accessibility testing:
- WebAIM Contrast Checker
- axe DevTools
- Lighthouse accessibility audit
- Color Oracle (colorblind simulation)

## Implementation Guidelines

### CSS Custom Properties

Use HSL color format for better manipulation:
```css
--primary: 221.2 83.2% 53.3%; /* H S L values */
```

### Semantic Naming

Always use semantic names rather than descriptive colors:
```css
/* Good */
--primary: 221.2 83.2% 53.3%;
--success: 142.1 76.2% 36.3%;

/* Avoid */
--blue: 221.2 83.2% 53.3%;
--green: 142.1 76.2% 36.3%;
```

### Theme Inheritance

New themes should inherit from base theme and override specific properties:
```css
.custom-theme {
  /* Inherit all base theme properties */
  /* Override only what's different */
  --primary: [custom color];
  --accent: [custom color];
}
```

## Performance Considerations

- Use CSS custom properties for runtime theme switching
- Avoid JavaScript-based theme calculations
- Minimize theme-specific CSS to reduce bundle size
- Leverage CSS cascade for theme inheritance
- Consider critical CSS for theme variables

## Future Enhancements

- Theme preview system
- User-customizable themes
- Theme marketplace/sharing
- Automatic theme generation tools
- Advanced color manipulation utilities
- Theme analytics and usage tracking
