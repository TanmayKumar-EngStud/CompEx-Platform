import { create } from "zustand";

/**
 * User attempt tracking and flagged questions management
 * 
 * Handles:
 * - User answer submissions and tracking
 * - Question flagging/bookmarking
 * - Attempt history management
 */

interface Attempt {
  problemId: number;
  option: string[]; // option text values
  timetaken: string | null;
  partialcorrectnessscore: number | null;
}

export interface AttemptsState {
  userId: number;
  Attempt: Attempt[] | null;
  flaggedQuestions: Set<number>;
  bookmarksEnabled: boolean;
  questionTagsEnabled: boolean;
}

export interface AttemptsActions {
  resetAttempt: () => void;
  addAttempt: (attempt: {
    problemId: number;
    option: string[];
    timetaken: string | null;
    partialcorrectnessscore: number | null;
  }) => void;
  toggleFlag: (questionId: number) => void;
  isFlagged: (questionId: number) => boolean;
  clearFlags: () => void;
  setBookmarksEnabled: (enabled: boolean) => void;
  setQuestionTagsEnabled: (enabled: boolean) => void;
  setUserId: (userId: number) => void;
  getAttemptForProblem: (problemId: number) => Attempt | null;
  removeAttempt: (problemId: number) => void;
}

export type AttemptsStore = AttemptsState & AttemptsActions;

/**
 * Zustand store for user attempts and flagged questions
 * 
 * @example
 * ```ts
 * const { addAttempt, toggleFlag, isFlagged } = useAttemptsStore();
 * ```
 */
export const useAttemptsStore = create<AttemptsStore>((set, get) => ({
  // State
  userId: 0,
  Attempt: null,
  flaggedQuestions: new Set<number>(),
  bookmarksEnabled: true,
  questionTagsEnabled: true,

  // Actions
  resetAttempt: () => set({ Attempt: null }),

  /**
   * Add or update user attempt for a problem
   */
  addAttempt: ({ problemId, option, timetaken, partialcorrectnessscore }) => {
    const currentAttempts = get().Attempt;

    if (currentAttempts !== null) {
      const existingIndex = currentAttempts.findIndex(
        (attempt) => attempt.problemId === problemId
      );

      if (existingIndex !== -1) {
        // Update existing attempt
        const updatedAttempts = currentAttempts.map((attempt) =>
          attempt.problemId === problemId
            ? { ...attempt, problemId, option, timetaken, partialcorrectnessscore }
            : attempt
        );
        set({ Attempt: updatedAttempts });
      } else {
        // Add new attempt
        set({
          Attempt: [
            ...currentAttempts,
            { timetaken, partialcorrectnessscore, problemId, option },
          ],
        });
      }
    } else {
      // Initialize Attempt with the first attempt
      set({
        Attempt: [
          { timetaken, partialcorrectnessscore, problemId, option },
        ],
      });
    }
  },

  /**
   * Toggle flag status for a question
   */
  toggleFlag: (questionId) => {
    const currentFlags = get().flaggedQuestions;
    const newFlags = new Set(currentFlags);
    if (newFlags.has(questionId)) {
      newFlags.delete(questionId);
    } else {
      newFlags.add(questionId);
    }
    set({ flaggedQuestions: newFlags });
  },

  /**
   * Check if a question is flagged
   */
  isFlagged: (questionId) => {
    return get().flaggedQuestions.has(questionId);
  },

  /**
   * Clear all flagged questions
   */
  clearFlags: () => {
    set({ flaggedQuestions: new Set<number>() });
  },

  /**
   * Enable or disable bookmarks feature
   */
  setBookmarksEnabled: (enabled) => {
    set({ bookmarksEnabled: enabled });
  },

  /**
   * Enable or disable question tags display
   */
  setQuestionTagsEnabled: (enabled) => {
    set({ questionTagsEnabled: enabled });
  },

  /**
   * Set user ID for attempt tracking
   */
  setUserId: (userId) => {
    set({ userId });
  },

  /**
   * Get specific attempt for a problem
   */
  getAttemptForProblem: (problemId) => {
    const attempts = get().Attempt;
    if (!attempts) return null;
    return attempts.find(attempt => attempt.problemId === problemId) || null;
  },

  /**
   * Remove attempt for a specific problem
   */
  removeAttempt: (problemId) => {
    const currentAttempts = get().Attempt;
    if (!currentAttempts) return;

    const filteredAttempts = currentAttempts.filter(
      attempt => attempt.problemId !== problemId
    );

    set({
      Attempt: filteredAttempts.length > 0 ? filteredAttempts : null
    });
  },
}));