# Plan: Onboarding Tutorial System for New Users

## Context

There is currently **zero onboarding** — after signup (email or Google OAuth), users land directly on `/dashboard/explore` with no guidance. This plan implements:

1. **Post-signup welcome flow** — Show AccountSettingsModal immediately so users can set theme, target exam, etc.
2. **Tooltip-based guided tutorial** — Step-by-step tooltip tour across pages (Explore → Problems → solving a question → viewing results)
3. **Replayable tutorials** — A "Replay Tutorial" section in AccountSettingsModal with per-page tutorial triggers

---

## Architecture Overview

```
Tutorial State (localStorage: compex-tutorial-state)
  ├── globalTourCompleted: boolean
  ├── showSettingsOnFirstLogin: boolean
  └── pageTours: { explore: boolean, problems: boolean, mock: boolean, profile: boolean }

TutorialProvider (React Context, wraps dashboard layout)
  ├── TutorialOverlay (backdrop + spotlight cutout)
  └── TutorialTooltip (positioned tooltip with step content + nav buttons)

AccountSettingsModal (existing component, modified)
  └── New section: "Replay Tutorials" dropdown
```

---

## Step 1: Create Tutorial State Store

### File: `shared/stores/tutorial-store.ts` (NEW)

Create a Zustand store with `localStorage` persistence using the `compex-tutorial-state` key.

```typescript
import { create } from "zustand";

interface TutorialState {
    // Global state
    isFirstLogin: boolean;
    globalTourCompleted: boolean;

    // Per-page tour completion
    pageTours: {
        explore: boolean;
        problems: boolean;
        mock: boolean;
        profile: boolean;
    };

    // Active tour state
    activeTour: string | null;       // "welcome" | "explore" | "problems" | "mock" | "profile" | null
    activeStep: number;              // Current step index in the active tour
    isTourRunning: boolean;

    // Actions
    setFirstLogin: (val: boolean) => void;
    completeGlobalTour: () => void;
    completePageTour: (page: keyof TutorialState["pageTours"]) => void;
    startTour: (tourName: string) => void;
    nextStep: () => void;
    prevStep: () => void;
    endTour: () => void;
    resetTour: (tourName: string) => void;
    resetAllTours: () => void;
}
```

**Persistence logic:**
- On store creation, read from `localStorage.getItem("compex-tutorial-state")`
- On every state change that affects `isFirstLogin`, `globalTourCompleted`, or `pageTours`, write to `localStorage.setItem("compex-tutorial-state", JSON.stringify(...))`
- Use Zustand's `subscribeWithSelector` or a manual `subscribe` callback for persistence — do NOT use `zustand/middleware/persist` (the rest of the codebase doesn't use it; keep consistency)

**Initial state for brand new users:**
```typescript
{
    isFirstLogin: true,
    globalTourCompleted: false,
    pageTours: { explore: false, problems: false, mock: false, profile: false },
    activeTour: null,
    activeStep: 0,
    isTourRunning: false,
}
```

The very first time a user loads the dashboard and `localStorage` has no `compex-tutorial-state` key, initialize with the above defaults (meaning `isFirstLogin: true`).

---

## Step 2: Define Tour Step Configurations

### File: `shared/configs/tutorial-steps.ts` (NEW)

Each tour is an array of step objects. Each step describes what to highlight and what text to show.

```typescript
export interface TutorialStep {
    // Target element (CSS selector or data attribute)
    target: string;                          // e.g., "[data-tour='explore-link']"

    // Tooltip content
    title: string;
    description: string;

    // Positioning
    placement: "top" | "bottom" | "left" | "right";

    // Navigation
    route?: string;                          // If set, navigate to this route before showing this step
    waitForSelector?: string;                // Wait for this element to appear before showing tooltip

    // Optional
    highlightPadding?: number;               // Extra padding around the highlighted element (default: 8)
    canInteract?: boolean;                   // If true, user can click the highlighted element (default: false)
}

export type TourDefinition = {
    id: string;
    name: string;
    steps: TutorialStep[];
};
```

### Tour Definitions:

#### Tour 1: "welcome" (Runs on first login, AFTER AccountSettingsModal is closed)

```typescript
{
    id: "welcome",
    name: "Welcome Tour",
    steps: [
        {
            target: "[data-tour='nav-explore']",
            title: "Explore Topics",
            description: "Start here! Browse GRE and GMAT topics organized by category. Pick any topic card to begin practicing.",
            placement: "bottom",
        },
        {
            target: "[data-tour='nav-problems']",
            title: "Practice Problems",
            description: "This is your main practice area. Solve questions one by one, track your progress, and build your skills.",
            placement: "bottom",
        },
        {
            target: "[data-tour='nav-mock']",
            title: "Mock Exams",
            description: "Take full-length timed mock exams that simulate the real test. See how you rank against other students.",
            placement: "bottom",
        },
        {
            target: "[data-tour='nav-learn']",
            title: "Learn",
            description: "Read about the GRE and GMAT exams — structure, scoring, and how CompEx helps you prepare.",
            placement: "bottom",
        },
        {
            target: "[data-tour='streak-counter']",
            title: "Daily Streaks",
            description: "Your practice streak shows here. Solve at least one question per day to keep it going!",
            placement: "bottom",
        },
        {
            target: "[data-tour='user-menu']",
            title: "Your Profile & Settings",
            description: "Access your profile, change your theme, target exam, and account settings from here. You can also replay these tutorials anytime from Account Settings.",
            placement: "bottom-end",
        },
    ],
}
```

#### Tour 2: "explore" (For /dashboard/explore page)

```typescript
{
    id: "explore",
    name: "Explore Page Tour",
    steps: [
        {
            target: "[data-tour='explore-hero']",
            title: "Your Target Exam",
            description: "This shows your currently selected exam. You can change it in Account Settings.",
            placement: "bottom",
        },
        {
            target: "[data-tour='explore-topics']",
            title: "Focused Topics",
            description: "These cards represent specific topics like Algebra, Geometry, or Sentence Equivalence. Each shows the number of available questions.",
            placement: "bottom",
        },
        {
            target: "[data-tour='explore-card-first']",
            title: "Start Practicing",
            description: "Click any topic card to jump straight into practice mode. Questions will be filtered to that topic automatically.",
            placement: "right",
            canInteract: true,
        },
    ],
}
```

#### Tour 3: "problems" (For /dashboard/problems page)

```typescript
{
    id: "problems",
    name: "Problems Page Tour",
    steps: [
        {
            target: "[data-tour='section-tabs']",
            title: "Exam Sections",
            description: "Switch between Quantitative and Verbal sections here. Use the shuffle button for mixed practice.",
            placement: "bottom",
        },
        {
            target: "[data-tour='problems-table']",
            title: "Question Table",
            description: "All available questions are listed here. Click any row to open and solve that question.",
            placement: "top",
        },
        {
            target: "[data-tour='sidebar-toggle']",
            title: "Filters & Settings",
            description: "Open this panel to filter by topic, enable bookmarks, toggle the timer, and customize your practice experience.",
            placement: "left",
        },
        {
            target: "[data-tour='display-solved-switch']",
            title: "Track Solved Questions",
            description: "Toggle this to show or hide questions you've already answered. Focus on unsolved problems to maximize progress.",
            placement: "bottom",
        },
    ],
}
```

#### Tour 4: "mock" (For /dashboard/mock page)

```typescript
{
    id: "mock",
    name: "Mock Exam Tour",
    steps: [
        {
            target: "[data-tour='mock-grid']",
            title: "Available Mock Exams",
            description: "Each card is a full-length timed mock exam. You'll see the difficulty level, question count, and your past scores.",
            placement: "bottom",
        },
    ],
}
```

#### Tour 5: "profile" (For /u/[username] page)

```typescript
{
    id: "profile",
    name: "Profile Tour",
    steps: [
        {
            target: "[data-tour='profile-stats']",
            title: "Your Stats",
            description: "Track your rank, percentile, and total questions solved. This updates in real-time as you practice.",
            placement: "right",
        },
        {
            target: "[data-tour='profile-analytics']",
            title: "Analytics Dashboard",
            description: "10+ interactive charts showing your progress — accuracy trends, topic quadrant analysis, skill radar, and more. Use these to find your weak spots.",
            placement: "left",
        },
    ],
}
```

---

## Step 3: Create Tutorial UI Components

### File: `shared/components/tutorial/TutorialOverlay.tsx` (NEW)

A fullscreen overlay with a spotlight cutout around the target element.

**Implementation approach:**
- Render a `fixed inset-0 z-[200]` div (must be above everything including AccountSettingsModal at z-[101])
- Use an SVG mask or `clip-path` to create a transparent "hole" over the target element
- The overlay background should be `bg-black/60 backdrop-blur-[1px]`
- Calculate the target element's `getBoundingClientRect()` and position the cutout there with `highlightPadding` (default 8px)
- Add a subtle `ring-2 ring-primary rounded-lg` glow effect via an absolutely positioned div around the cutout
- Clicking the overlay (not the cutout) should do nothing (prevent accidentally closing)
- Use `ResizeObserver` and `scroll` event listeners to reposition the cutout if the page layout shifts
- Use Framer Motion `AnimatePresence` + `motion.div` for smooth transitions between steps

### File: `shared/components/tutorial/TutorialTooltip.tsx` (NEW)

The tooltip that appears next to the highlighted element.

**Structure:**
```
┌─────────────────────────────────────┐
│  [Step 2 of 6]                      │
│                                     │
│  Title Text (bold, text-lg)         │
│  Description text (text-sm,         │
│  text-muted-foreground)             │
│                                     │
│  [← Prev]  [● ● ● ● ● ●]  [Next →]│
│                          [Skip Tour]│
└─────────────────────────────────────┘
```

**Props:**
```typescript
interface TutorialTooltipProps {
    step: TutorialStep;
    currentIndex: number;
    totalSteps: number;
    onNext: () => void;
    onPrev: () => void;
    onSkip: () => void;
    targetRect: DOMRect;       // Position of the highlighted element
}
```

**Positioning logic:**
- Based on `step.placement`, position the tooltip relative to `targetRect`
- Use the same Framer Motion `motion.div` with `initial={{ opacity: 0, y: 8 }}`, `animate={{ opacity: 1, y: 0 }}`
- Ensure the tooltip stays within viewport bounds (flip placement if it would overflow)
- Render via `ReactDOM.createPortal(document.body)` at `z-[201]`

**Styling:**
- `bg-card border border-border rounded-xl shadow-2xl p-5 w-[340px]`
- Step indicator: small dots using `bg-primary` for current, `bg-muted` for others
- Buttons: "Previous" (ButtonS variant), "Next" / "Finish" (ButtonP variant), "Skip Tour" (ghost text link)
- On the final step, "Next" button text changes to "Finish"

### File: `shared/components/tutorial/TutorialProvider.tsx` (NEW)

A context provider component that manages the active tour rendering.

**What it does:**
1. Reads `activeTour`, `activeStep`, `isTourRunning` from `useTutorialStore`
2. If `isTourRunning`, looks up the current step definition from `tutorial-steps.ts`
3. If the step has a `route` and the current pathname doesn't match, use `router.push(route)` and wait
4. If the step has a `waitForSelector`, poll for the element (with a 5-second timeout)
5. Once the target element is found, calculate its `getBoundingClientRect()` and render:
   - `<TutorialOverlay targetRect={rect} padding={step.highlightPadding} />`
   - `<TutorialTooltip step={step} targetRect={rect} ... />`
6. Wire up `onNext` → `store.nextStep()` (if last step, call `store.endTour()` and `store.completePageTour()`)
7. Wire up `onSkip` → `store.endTour()`
8. Wire up `onPrev` → `store.prevStep()`

**Scroll handling:** Before showing each step, call `targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' })` to ensure the target is visible.

**Wrap this provider** around the dashboard layout children (see Step 5).

---

## Step 4: Add `data-tour` Attributes to Existing Components

These attributes are the anchor points for the tutorial tooltips. Add them to existing elements — **no visual changes, just adding data attributes**.

### `shared/components/layouts/navbar.tsx`

In the `navLinks.map()` render (authenticated state), add `data-tour` to each `<Link>`:

```tsx
// Inside the navLinks.map() — add data-tour to the <Link>
<Link
    key={index}
    href={link.href}
    data-tour={`nav-${link.name.toLowerCase()}`}   // ADD THIS
    className={clsx(...)}
>
    {link.name}
</Link>
```

This produces: `data-tour="nav-explore"`, `data-tour="nav-problems"`, `data-tour="nav-mock"`, `data-tour="nav-learn"`.

Also add to the streak counter and user menu in `renderRight()`:

```tsx
// Around ProblemsStreak component:
<div data-tour="streak-counter">
    <ProblemsStreak streak={...} />
</div>

// Around UserSwitcher component:
<div data-tour="user-menu">
    <UserSwitcher />
</div>
```

The full `renderRight()` for authenticated users becomes:
```tsx
return [
    <div key="auth-right" className="flex gap-4 items-center">
        <div data-tour="streak-counter">
            <ProblemsStreak streak={streakLoading ? 0 : streakData.currentstreak} />
        </div>
        <div data-tour="user-menu">
            <UserSwitcher />
        </div>
    </div>,
];
```

### `app/dashboard/explore/explore-page-client.tsx`

Add `data-tour` to the hero section and the first topic card:

```tsx
// Hero section wrapper
<div data-tour="explore-hero">
    {/* existing hero content */}
</div>

// First accordion/topic section
<div data-tour="explore-topics">
    {/* existing Focused Topics accordion */}
</div>

// First topic card rendered in the grid (only the first one)
// Add data-tour="explore-card-first" to the first Card in the topic grid
```

To add `data-tour="explore-card-first"` to only the first card: in the `.map()` that renders topic cards, conditionally add the attribute:

```tsx
<div
    key={tag.name}
    data-tour={index === 0 ? "explore-card-first" : undefined}
    // ... rest of props
>
```

### `app/dashboard/problems/components/problems-table-section.tsx`

```tsx
// Wrapper around the table
<div data-tour="problems-table">
    <LazyQuestionTable ... />
</div>

// The "Display Solved" switch area
<div data-tour="display-solved-switch">
    {/* existing toggle pill with Display Solved switch */}
</div>
```

### `features/exam-management/components/parent-panel.tsx`

```tsx
// Tab bar wrapper
<div data-tour="section-tabs">
    {/* existing tab bar flex container */}
</div>
```

### `app/dashboard/problems/components/problems-sidebar.tsx`

```tsx
// The sidebar toggle button (the ChevronLeft button visible when sidebar is closed)
<button data-tour="sidebar-toggle" ...>
    <ChevronLeft />
</button>
```

### `app/dashboard/mock/page.tsx`

```tsx
// The mock test card grid
<div data-tour="mock-grid">
    {/* existing grid of mock test cards */}
</div>
```

### `app/u/[username]/page.tsx`

```tsx
// Left sidebar stats area
<div data-tour="profile-stats">
    {/* existing UserAvatar + stats content */}
</div>

// Right analytics area
<div data-tour="profile-analytics">
    <ProfileAnalytics ... />
</div>
```

---

## Step 5: Wire Up the First-Login Flow

### Modify: `app/dashboard/layout.tsx`

1. Import and wrap children with `<TutorialProvider>`:

```tsx
import { TutorialProvider } from "@/shared/components/tutorial/TutorialProvider";

// In the return JSX, wrap {children}:
<TutorialProvider>
    {children}
</TutorialProvider>
```

### Create: `shared/components/tutorial/FirstLoginHandler.tsx` (NEW)

A client component that checks if this is a first login and orchestrates the welcome flow.

```typescript
"use client";

import { useEffect, useState } from "react";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

export function FirstLoginHandler() {
    const { isFirstLogin, setFirstLogin, startTour, globalTourCompleted } = useTutorialStore();
    const [showSettings, setShowSettings] = useState(false);

    useEffect(() => {
        // Only trigger on first login
        if (!isFirstLogin) return;

        // Show AccountSettingsModal immediately
        setShowSettings(true);
    }, [isFirstLogin]);

    const handleSettingsClose = () => {
        setShowSettings(false);
        setFirstLogin(false);

        // Start the welcome tour after settings modal closes
        if (!globalTourCompleted) {
            // Small delay to let the modal close animation finish
            setTimeout(() => {
                startTour("welcome");
            }, 500);
        }
    };

    if (!showSettings) return null;

    return (
        <AccountSettingsModal
            isOpen={showSettings}
            onClose={handleSettingsClose}
            isFirstLogin={true}  // Pass this prop to show a welcome message in the modal
        />
    );
}
```

**Add `<FirstLoginHandler />` to the dashboard layout** right after `<TutorialProvider>`.

### Modify: `shared/components/interactive/AccountSettingsModal.tsx`

Add an optional `isFirstLogin` prop. When `true`:
- Show a welcome banner at the top: "Welcome to CompEx! Let's set up your account."
- Pre-expand the Preferences section
- The "Save Changes" button text changes to "Get Started"

**No other changes to the modal logic** — it already has theme toggle and exam type selector.

---

## Step 6: Add "Replay Tutorial" Section to AccountSettingsModal

### Modify: `shared/components/interactive/AccountSettingsModal.tsx`

Add a new section in the right panel, below the existing Preferences grid:

```tsx
{/* Replay Tutorials Section */}
<div className="space-y-3">
    <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
        Replay Tutorials
    </h3>
    <p className="text-xs text-muted-foreground">
        Re-watch the guided tutorial for any page
    </p>
    <Select onValueChange={(value) => handleReplayTutorial(value)}>
        <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a page tutorial..." />
        </SelectTrigger>
        <SelectContent>
            <SelectItem value="welcome">Welcome Tour (Navbar Overview)</SelectItem>
            <SelectItem value="explore">Explore Page</SelectItem>
            <SelectItem value="problems">Problems Page</SelectItem>
            <SelectItem value="mock">Mock Exams Page</SelectItem>
            <SelectItem value="profile">Profile & Analytics</SelectItem>
        </SelectContent>
    </Select>
</div>
```

The `handleReplayTutorial` function:
```typescript
const handleReplayTutorial = (tourId: string) => {
    const { resetTour, startTour } = useTutorialStore.getState();

    // Close the settings modal
    onClose();

    // Navigate to the relevant page first, then start tour
    const routeMap: Record<string, string> = {
        welcome: "/dashboard/explore",
        explore: "/dashboard/explore",
        problems: "/dashboard/problems",
        mock: "/dashboard/mock",
        profile: `/u/${username}`,   // use the current user's username
    };

    const targetRoute = routeMap[tourId];
    if (targetRoute && pathname !== targetRoute) {
        router.push(targetRoute);
    }

    // Small delay for navigation + modal close animation
    setTimeout(() => {
        resetTour(tourId);
        startTour(tourId);
    }, 600);
};
```

**Imports needed:** Add `Select`, `SelectTrigger`, `SelectContent`, `SelectItem`, `SelectValue` from `@/shared/components/ui/select` (already exists in the codebase). Import `useRouter` from `next/navigation` and `useTutorialStore`.

---

## Step 7: Auto-Trigger Page Tours for New Users

### Modify: `app/dashboard/explore/explore-page-client.tsx`

Add a `useEffect` that checks if the explore page tour has been completed:

```typescript
import { useTutorialStore } from "@/shared/stores/tutorial-store";

// Inside the component:
const { pageTours, startTour, isTourRunning } = useTutorialStore();

useEffect(() => {
    if (!pageTours.explore && !isTourRunning) {
        // Delay to let the page render fully
        const timer = setTimeout(() => startTour("explore"), 800);
        return () => clearTimeout(timer);
    }
}, [pageTours.explore, isTourRunning, startTour]);
```

### Modify: `app/dashboard/problems/page.tsx`

Same pattern:
```typescript
const { pageTours, startTour, isTourRunning } = useTutorialStore();

useEffect(() => {
    if (!pageTours.problems && !isTourRunning) {
        const timer = setTimeout(() => startTour("problems"), 800);
        return () => clearTimeout(timer);
    }
}, [pageTours.problems, isTourRunning, startTour]);
```

### Modify: `app/dashboard/mock/page.tsx`

Same pattern with `pageTours.mock`.

### Modify: `app/u/[username]/page.tsx`

This is a server component, so you'll need to add a small client wrapper component:

Create `app/u/[username]/ProfileTourTrigger.tsx`:
```tsx
"use client";
import { useEffect } from "react";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

export function ProfileTourTrigger() {
    const { pageTours, startTour, isTourRunning } = useTutorialStore();

    useEffect(() => {
        if (!pageTours.profile && !isTourRunning) {
            const timer = setTimeout(() => startTour("profile"), 800);
            return () => clearTimeout(timer);
        }
    }, [pageTours.profile, isTourRunning, startTour]);

    return null;
}
```

Then add `<ProfileTourTrigger />` to the profile page JSX.

---

## Files Summary

| Action | File | Description |
|--------|------|-------------|
| **NEW** | `shared/stores/tutorial-store.ts` | Zustand store with localStorage persistence |
| **NEW** | `shared/configs/tutorial-steps.ts` | Tour definitions (5 tours, ~20 steps total) |
| **NEW** | `shared/components/tutorial/TutorialOverlay.tsx` | Fullscreen overlay with spotlight cutout |
| **NEW** | `shared/components/tutorial/TutorialTooltip.tsx` | Positioned tooltip with step content + navigation |
| **NEW** | `shared/components/tutorial/TutorialProvider.tsx` | Context provider managing active tour rendering |
| **NEW** | `shared/components/tutorial/FirstLoginHandler.tsx` | First-login detection + settings modal + welcome tour trigger |
| **NEW** | `app/u/[username]/ProfileTourTrigger.tsx` | Client component to auto-trigger profile page tour |
| **MODIFY** | `shared/components/layouts/navbar.tsx` | Add `data-tour` attributes to nav links, streak, user menu |
| **MODIFY** | `app/dashboard/explore/explore-page-client.tsx` | Add `data-tour` attributes + auto-trigger explore tour |
| **MODIFY** | `app/dashboard/problems/page.tsx` | Auto-trigger problems tour |
| **MODIFY** | `app/dashboard/problems/components/problems-table-section.tsx` | Add `data-tour` attributes |
| **MODIFY** | `features/exam-management/components/parent-panel.tsx` | Add `data-tour` to tab bar |
| **MODIFY** | `app/dashboard/problems/components/problems-sidebar.tsx` | Add `data-tour` to toggle button |
| **MODIFY** | `app/dashboard/mock/page.tsx` | Add `data-tour` + auto-trigger mock tour |
| **MODIFY** | `app/u/[username]/page.tsx` | Add `data-tour` attributes + `<ProfileTourTrigger />` |
| **MODIFY** | `app/dashboard/layout.tsx` | Wrap children with `<TutorialProvider>` + `<FirstLoginHandler>` |
| **MODIFY** | `shared/components/interactive/AccountSettingsModal.tsx` | Add `isFirstLogin` welcome banner + "Replay Tutorials" dropdown |

---

## Key Implementation Notes

1. **Z-index layering**: Tutorial overlay must be `z-[200]`, tooltip `z-[201]`. This is above AccountSettingsModal (`z-[101]`) and the crop modal (`z-[110]`). The overlay must render AFTER the settings modal closes.

2. **No new dependencies**: Use only existing libraries — Framer Motion for animations, Radix primitives for the dropdown, Zustand for state. No need for external tour libraries like `react-joyride`.

3. **localStorage key**: `compex-tutorial-state` — follows the existing `compex-` prefix convention.

4. **Tour does NOT persist step progress**: If the user closes the browser mid-tour, the tour resets to step 0 next time. Only completion state persists. This is intentional — tours are short (2-6 steps each).

5. **Keyboard support**: The TutorialTooltip should handle `Escape` (skip tour), `ArrowRight` / `Enter` (next step), `ArrowLeft` (prev step).

6. **Mobile responsiveness**: On screens < 768px, the tooltip should always appear below the target (override `placement`). The overlay cutout must recalculate on resize.

7. **Route-based steps**: Some welcome tour steps highlight navbar links. If the user is already on `/dashboard/explore`, no navigation is needed. The TutorialProvider should compare `step.route` with `usePathname()` before navigating.

---

## Verification

1. **New user signup** (email or Google) → lands on `/dashboard/explore` → AccountSettingsModal appears immediately with "Welcome to CompEx!" banner → user sets preferences → clicks "Get Started" → welcome navbar tour starts (6 steps highlighting each nav element)
2. **Navigate to Explore** → if explore tour not completed, it auto-triggers (3 steps)
3. **Navigate to Problems** → if problems tour not completed, it auto-triggers (4 steps)
4. **Navigate to Mock** → if mock tour not completed, it auto-triggers (1 step)
5. **Visit Profile** → if profile tour not completed, it auto-triggers (2 steps)
6. **Replay**: Open AccountSettingsModal → "Replay Tutorials" dropdown → select "Explore Page" → modal closes, navigates to `/dashboard/explore`, tour replays
7. **Returning users**: No tours auto-trigger (all marked complete in localStorage)
8. **Clear localStorage** → tours reset for that browser (simulates new user experience)
