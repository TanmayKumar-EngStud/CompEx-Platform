/**
 * CompEx Design Tokens
 * Mirrors the web app's shadcn/ui neutral palette (New York style)
 * CSS variables → React Native StyleSheet values
 */

// ─── Colors (shadcn/ui neutral, dark mode first) ───────────────────────────
export const Colors = {
  // Core backgrounds
  background: '#09090b',       // --background  (zinc-950)
  card: '#18181b',             // --card        (zinc-900)
  cardBorder: '#27272a',       // --border      (zinc-800)

  // Foregrounds
  foreground: '#fafafa',       // --foreground  (zinc-50)
  mutedForeground: '#a1a1aa',  // --muted-foreground (zinc-400)
  cardForeground: '#fafafa',   // --card-foreground

  // Interactive
  primary: '#ffffff',          // --primary     (white in dark mode)
  primaryForeground: '#09090b',// --primary-foreground
  secondary: '#27272a',        // --secondary   (zinc-800)
  secondaryForeground: '#fafafa',

  // State
  muted: '#27272a',            // --muted
  accent: '#27272a',           // --accent
  accentForeground: '#fafafa', // --accent-foreground
  destructive: '#ef4444',      // --destructive (red-500)
  destructiveForeground: '#fafafa',

  // Utilities
  border: '#27272a',           // --border
  input: '#27272a',            // --input
  ring: '#a1a1aa',             // --ring

  // Brand accent (CompEx blue — used for CTAs, active states)
  brand: '#3b82f6',            // blue-500
  brandMuted: '#1d4ed8',       // blue-700
  brandLight: 'rgba(59,130,246,0.15)',

  // Status colors
  success: '#22c55e',          // green-500
  warning: '#f59e0b',          // amber-500
  info: '#06b6d4',             // cyan-500
  error: '#ef4444',            // red-500

  // Exam type colors (from your brand assets)
  gre: '#8b5cf6',              // violet-500
  gmat: '#f59e0b',             // amber-500
  sat: '#06b6d4',              // cyan-500

  // Difficulty
  easy: '#22c55e',
  medium: '#f59e0b',
  hard: '#ef4444',

  // Transparent overlays
  overlay: 'rgba(0,0,0,0.6)',
  overlayLight: 'rgba(0,0,0,0.3)',
} as const;

// ─── Typography ────────────────────────────────────────────────────────────
// Matches Inter (web) — loaded via expo-font
export const Typography = {
  fonts: {
    sans: 'Inter_400Regular',
    sansMedium: 'Inter_500Medium',
    sansSemiBold: 'Inter_600SemiBold',
    sansBold: 'Inter_700Bold',
  },
  sizes: {
    xs: 11,
    sm: 13,
    base: 15,
    lg: 17,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
  },
  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.7,
  },
  letterSpacing: {
    tight: -0.5,
    normal: 0,
    wide: 0.5,
    wider: 1,
  },
} as const;

// ─── Spacing (4pt grid) ────────────────────────────────────────────────────
export const Spacing = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  7: 28,
  8: 32,
  10: 40,
  12: 48,
  16: 64,
  20: 80,
} as const;

// ─── Border Radius ─────────────────────────────────────────────────────────
// New York style = slightly sharper (not fully rounded)
export const Radius = {
  sm: 6,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
} as const;

// ─── Shadows ───────────────────────────────────────────────────────────────
export const Shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 6,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
    elevation: 8,
  },
} as const;

// ─── Animation durations ───────────────────────────────────────────────────
export const Durations = {
  fast: 150,
  normal: 250,
  slow: 400,
} as const;

// ─── Z-index ───────────────────────────────────────────────────────────────
export const ZIndex = {
  base: 0,
  card: 10,
  dropdown: 100,
  modal: 200,
  toast: 300,
} as const;
