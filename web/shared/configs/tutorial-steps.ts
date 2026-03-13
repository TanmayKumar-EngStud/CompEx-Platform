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

    // Interactive step controls
    noNextButton?: boolean;                  // Hide Next/Prev buttons — user must take the required action
    advanceOnNavigate?: string;              // Auto-advance when pathname starts with this prefix
    advanceOnSelector?: string;              // Auto-advance when this CSS selector appears in the DOM
    noOverlay?: boolean;                     // Skip the dark overlay so user can freely interact with the page
    fixedPosition?: "top-left" | "top-right" | "bottom-left" | "bottom-right";  // Pin tooltip to a corner instead of next to target
}

export type TourDefinition = {
    id: string;
    name: string;
    steps: TutorialStep[];
};

export const tours: Record<string, TourDefinition> = {
    "welcome": {
        id: "welcome",
        name: "Welcome Tour",
        steps: [
            {
                target: "[data-tour='nav-explore']",
                title: "Explore Topics",
                description: "Start here! Browse GRE and GMAT topics organized by category. Pick any topic card to begin practicing.",
                placement: "bottom",
                highlightPadding: 16,
            },
            {
                target: "[data-tour='nav-problems']",
                title: "Practice Problems",
                description: "This is your main practice area. Solve questions one by one, track your progress, and build your skills.",
                placement: "bottom",
                highlightPadding: 16,
            },
            {
                target: "[data-tour='nav-mock']",
                title: "Mock Exams",
                description: "Take full-length timed mock exams that simulate the real test. See how you rank against other students.",
                placement: "bottom",
                highlightPadding: 16,
            },
            {
                target: "[data-tour='nav-learn']",
                title: "Learn",
                description: "Read about the GRE and GMAT exams — structure, scoring, and how CompEx helps you prepare.",
                placement: "bottom",
                highlightPadding: 16,
            },
            {
                target: "[data-tour='streak-counter']",
                title: "Daily Streaks",
                description: "Your practice streak shows here. Solve at least one question per day to keep it going!",
                placement: "bottom",
                highlightPadding: 16,
            },
            {
                target: "[data-tour='user-menu']",
                title: "Your Profile & Settings",
                description: "Access your profile, change your theme, target exam, and account settings from here. You can also replay these tutorials anytime from Account Settings.",
                placement: "bottom",
                highlightPadding: 16,
            },
        ],
    },
    "explore": {
        id: "explore",
        name: "Explore Page Tour",
        steps: [
            // Step 1 — Explore index: user must click a topic card.
            // noOverlay: true so the page is fully scrollable and cards can be
            // individually animated in ExplorePageClient. Tooltip is pinned to
            // the bottom-right corner via fixedPosition.
            {
                target: "[data-tour='explore-topics']",
                title: "Pick a Topic Card!",
                description: "Each card is a focused training module. Click any one of the pulsing cards to open its question set and start practicing!",
                placement: "bottom",
                highlightPadding: 20,
                noNextButton: true,
                noOverlay: true,
                fixedPosition: "bottom-right",
                advanceOnNavigate: "/dashboard/explore/",
                route: "/dashboard/explore",
            },
            // Step 2 — Topic detail page: user must click a question row to open the question window
            {
                target: "[data-tour='problems-table']",
                title: "Your Practice Questions",
                description: "All questions for this topic are listed here. Click any row to open it and start solving!",
                placement: "top",
                highlightPadding: 12,
                canInteract: true,
                noNextButton: true,
                advanceOnSelector: "[data-tour='question-window']",
            },
            // Step 3 — Question window open: user solves 2-3 questions then clicks Finish Session
            {
                target: "[data-tour='question-window']",
                title: "Solve 2–3 Questions",
                description: "Answer the question, then use the arrow buttons to move to the next one. Solve at least 2 questions, then click \"Finish Session\" to see your results.",
                placement: "bottom",
                highlightPadding: 0,
                canInteract: true,
                noNextButton: true,
                advanceOnSelector: "[data-tour='result-window']",
                noOverlay: true,
                fixedPosition: "bottom-right",
            },
            // Step 4 — Result window summary: user must click a question row to see the solution
            {
                target: "[data-tour='result-table-first-row']",
                title: "Review a Question",
                description: "Click any question in this table to see the full solution and AI coach explanation!",
                placement: "top",
                highlightPadding: 6,
                canInteract: true,
                noNextButton: true,
                advanceOnSelector: "[data-tour='result-solution-view']",
            },
            // Step 5 — Solution view: tour complete.
            // noOverlay + fixedPosition so the SVG rect is never rendered and
            // the user can freely scroll through the solution content.
            {
                target: "[data-tour='result-solution-view']",
                title: "You Got It! 🎯",
                description: "This is the solution view — see the correct answer and AI explanation. You now know how to use the Explore page. Happy studying!",
                placement: "bottom",
                highlightPadding: 8,
                noOverlay: true,
                fixedPosition: "bottom-right",
            },
        ],
    },
    "problems": {
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
                target: "[data-tour='problems-filters']",
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
    },
    "mock": {
        id: "mock",
        name: "Mock Exam Tour",
        steps: [
            {
                target: "[data-tour='mock-hero']",
                title: "Mock Exams",
                description: "This is where you can find full-length mock exams for your target test.",
                placement: "bottom",
            },
            {
                target: "[data-tour='mock-card-first']",
                title: "Start a Mock",
                description: "Each card represents a complete exam. Check the difficulty and question count before starting.",
                placement: "right",
            },
        ],
    },
    "profile": {
        id: "profile",
        name: "Profile Tour",
        steps: [
            {
                target: "[data-tour='profile-header']",
                title: "User Profile",
                description: "View your rank, percentile, and member status here.",
                placement: "right",
            },
            {
                target: "[data-tour='profile-stats']",
                title: "Community Stats",
                description: "Track your total solved problems and contribution metrics.",
                placement: "right",
            },
            {
                target: "[data-tour='profile-heatmap']",
                title: "Activity Heatmap",
                description: "Visualizes your daily practice consistency. Darker squares mean more questions solved!",
                placement: "left",
            },
        ],
    },
};
