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

const STORAGE_KEY = "compex-tutorial-state";

const DEFAULT_STATE = {
    isFirstLogin: true,
    globalTourCompleted: false,
    pageTours: { explore: false, problems: false, mock: false, profile: false },
    activeTour: null,
    activeStep: 0,
    isTourRunning: false,
};

export const useTutorialStore = create<TutorialState>((set, get) => {
    // Initialize from localStorage if available
    let initialState = DEFAULT_STATE;
    if (typeof window !== "undefined") {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                // Merge parsed state with default state to ensure structure
                initialState = {
                    ...DEFAULT_STATE,
                    ...parsed,
                    // Always reset active tour state on reload/init
                    activeTour: null,
                    activeStep: 0,
                    isTourRunning: false
                };
            } catch (e) {
                console.error("Failed to parse tutorial state", e);
            }
        }
    }

    const saveState = (state: Partial<TutorialState>) => {
        if (typeof window !== "undefined") {
            const currentState = get();
            const persistentState = {
                isFirstLogin: state.isFirstLogin !== undefined ? state.isFirstLogin : currentState.isFirstLogin,
                globalTourCompleted: state.globalTourCompleted !== undefined ? state.globalTourCompleted : currentState.globalTourCompleted,
                pageTours: state.pageTours !== undefined ? state.pageTours : currentState.pageTours,
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(persistentState));
        }
    };

    return {
        ...initialState,

        setFirstLogin: (val) => {
            set({ isFirstLogin: val });
            saveState({ isFirstLogin: val });
        },

        completeGlobalTour: () => {
            set({ globalTourCompleted: true });
            saveState({ globalTourCompleted: true });
        },

        completePageTour: (page) => {
            const newPageTours = { ...get().pageTours, [page]: true };
            set({ pageTours: newPageTours });
            saveState({ pageTours: newPageTours });
        },

        startTour: (tourName) => {
            set({
                activeTour: tourName,
                activeStep: 0,
                isTourRunning: true
            });
        },

        nextStep: () => {
            set((state) => ({ activeStep: state.activeStep + 1 }));
        },

        prevStep: () => {
            set((state) => ({ activeStep: Math.max(0, state.activeStep - 1) }));
        },

        endTour: () => {
            set({
                activeTour: null,
                activeStep: 0,
                isTourRunning: false
            });
        },

        resetTour: (tourName) => {
            if (tourName === "welcome") {
                set({ globalTourCompleted: false });
                saveState({ globalTourCompleted: false });
            } else if (tourName in DEFAULT_STATE.pageTours) {
                const newPageTours = { ...get().pageTours, [tourName]: false };
                set({ pageTours: newPageTours });
                saveState({ pageTours: newPageTours });
            }
        },

        resetAllTours: () => {
            set(DEFAULT_STATE);
            if (typeof window !== "undefined") {
                localStorage.removeItem(STORAGE_KEY);
            }
        },
    };
});
