import { create } from "zustand";

/**
 * UI state management for modals, loading states, and user preferences
 * 
 * Handles:
 * - Modal visibility states
 * - Loading and error states
 * - User preference toggles
 * - UI interaction states
 */

export interface UIState {
  // Modal states
  isQuestionWindowOpen: boolean;
  isResultWindowOpen: boolean;
  isSettingsPanelOpen: boolean;
  
  // Loading states
  isLoadingProblems: boolean;
  isLoadingQuestion: boolean;
  isSubmittingAnswer: boolean;
  
  // Error states
  problemsError: string | null;
  questionError: string | null;
  submissionError: string | null;
  
  // User preferences
  showTimer: boolean;
  showDifficulty: boolean;
  displaySolvedQuestions: boolean;
  
  // UI interaction states
  selectedProblemId: number | null;
  expandedProblemSets: Set<number>;
}

export interface UIActions {
  // Modal actions
  openQuestionWindow: () => void;
  closeQuestionWindow: () => void;
  openResultWindow: () => void;
  closeResultWindow: () => void;
  toggleSettingsPanel: () => void;
  
  // Loading actions
  setLoadingProblems: (loading: boolean) => void;
  setLoadingQuestion: (loading: boolean) => void;
  setSubmittingAnswer: (submitting: boolean) => void;
  
  // Error actions
  setProblemsError: (error: string | null) => void;
  setQuestionError: (error: string | null) => void;
  setSubmissionError: (error: string | null) => void;
  clearAllErrors: () => void;
  
  // Preference actions
  setShowTimer: (show: boolean) => void;
  setShowDifficulty: (show: boolean) => void;
  setDisplaySolvedQuestions: (display: boolean) => void;
  ensurePreferencesInitialized: () => void;
  
  // UI interaction actions
  setSelectedProblemId: (id: number | null) => void;
  toggleProblemSetExpansion: (id: number) => void;
  resetUIState: () => void;
}

export type UIStore = UIState & UIActions;

/**
 * Zustand store for UI state management
 * 
 * @example
 * ```ts
 * const { isQuestionWindowOpen, openQuestionWindow, showTimer, setShowTimer } = useUIStore();
 * ```
 */
export const useUIStore = create<UIStore>((set, get) => ({
  // State
  // Modal states
  isQuestionWindowOpen: false,
  isResultWindowOpen: false,
  isSettingsPanelOpen: false,
  
  // Loading states
  isLoadingProblems: false,
  isLoadingQuestion: false,
  isSubmittingAnswer: false,
  
  // Error states
  problemsError: null,
  questionError: null,
  submissionError: null,
  
  // User preferences
  showTimer: false,
  showDifficulty: false,
  displaySolvedQuestions: true,
  
  // UI interaction states
  selectedProblemId: null,
  expandedProblemSets: new Set<number>(),

  // Actions
  // Modal actions
  openQuestionWindow: () => set({ isQuestionWindowOpen: true }),
  closeQuestionWindow: () => set({ 
    isQuestionWindowOpen: false, 
    selectedProblemId: null 
  }),
  openResultWindow: () => set({ isResultWindowOpen: true }),
  closeResultWindow: () => set({ isResultWindowOpen: false }),
  toggleSettingsPanel: () => set((state) => ({ 
    isSettingsPanelOpen: !state.isSettingsPanelOpen 
  })),
  
  // Loading actions
  setLoadingProblems: (loading) => set({ isLoadingProblems: loading }),
  setLoadingQuestion: (loading) => set({ isLoadingQuestion: loading }),
  setSubmittingAnswer: (submitting) => set({ isSubmittingAnswer: submitting }),
  
  // Error actions
  setProblemsError: (error) => set({ problemsError: error }),
  setQuestionError: (error) => set({ questionError: error }),
  setSubmissionError: (error) => set({ submissionError: error }),
  clearAllErrors: () => set({ 
    problemsError: null, 
    questionError: null, 
    submissionError: null 
  }),
  
  // Preference actions
  setShowTimer: (show) => set({ showTimer: show }),
  setShowDifficulty: (show) => set({ showDifficulty: show }),
  setDisplaySolvedQuestions: (display) => set({ displaySolvedQuestions: display }),

  /**
   * Ensure user preferences are initialized to their defaults if undefined
   */
  ensurePreferencesInitialized: () => {
    const state = get();
    const updates: Partial<UIState> = {};
    
    if (state.showTimer === undefined) updates.showTimer = false;
    if (state.showDifficulty === undefined) updates.showDifficulty = false;
    if (state.displaySolvedQuestions === undefined) updates.displaySolvedQuestions = true;
    
    if (Object.keys(updates).length > 0) {
      set(updates);
    }
  },
  
  // UI interaction actions
  setSelectedProblemId: (id) => set({ selectedProblemId: id }),
  
  /**
   * Toggle expansion state of a problem set
   */
  toggleProblemSetExpansion: (id) => {
    const currentExpanded = get().expandedProblemSets;
    const newExpanded = new Set(currentExpanded);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    set({ expandedProblemSets: newExpanded });
  },
  
  /**
   * Reset all UI state to defaults but preserve user preferences
   */
  resetUIState: () => {
    const currentState = get();
    set({
      isQuestionWindowOpen: false,
      isResultWindowOpen: false,
      isSettingsPanelOpen: false,
      isLoadingProblems: false,
      isLoadingQuestion: false,
      isSubmittingAnswer: false,
      problemsError: null,
      questionError: null,
      submissionError: null,
      selectedProblemId: null,
      expandedProblemSets: new Set<number>(),
      // Preserve user preferences during reset
      showTimer: currentState.showTimer,
      showDifficulty: currentState.showDifficulty,
      displaySolvedQuestions: currentState.displaySolvedQuestions,
    });
  },
}));