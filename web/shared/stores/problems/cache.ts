import { create } from "zustand";

/**
 * Problem and ProblemsSet data structures
 */
export interface Problem {
  problemid: string;
  title: string;
  difficulty: number;
  addedDate: string;
  options_type?: string | null;
  problemtags: {
    tags: {
      tagid?: number;
      topic: string | null;
      theme: string | null;
      type: string | null;
      name?: string | null;
    }
  }[];
  iscorrect: boolean | null | undefined;
  absoluteIndex?: number;
}

export interface ProblemsSet {
  problemsSetId: number;
  title: string;
  difficulty?: number;
  addedDate?: string;
  isExpanded: boolean;
  problems: Problem[];
  absoluteIndex?: number;
}

export type HybridProblem = ProblemsSet | Problem;

export interface ProblemsResponse {
  problemData: HybridProblem[];
  totalProblems: number;
  metadata?: any;
}

/**
 * Problems cache state for storing fetched problems data
 * 
 * Handles:
 * - Current problems/problemsets display
 * - Shuffle state and order management
 * - Data transformations and validation
 */

export interface ProblemsState {
  problems_or_problemsset: HybridProblem[];
  isShuffled: boolean;
  shuffledOrder: number[];
}

export interface ProblemsActions {
  setProblems: (problems: HybridProblem[]) => void;
  setIsShuffled: (shuffled: boolean) => void;
  setShuffledOrder: (order: number[]) => void;
  shuffleQuestions: (sourceData?: HybridProblem[]) => void;
  clearProblems: () => void;
  updateProblemsWithAttemptData: (attemptResults: Array<{ problemid: number, iscorrect: boolean }>) => void;
}

export type ProblemsStore = ProblemsState & ProblemsActions;

/**
 * Zustand store for problems data management
 * 
 * @example
 * ```ts
 * const { problems_or_problemsset, shuffleQuestions } = useProblemsStore();
 * ```
 */
export const useProblemsStore = create<ProblemsStore>((set, get) => ({
  // State
  problems_or_problemsset: [],
  isShuffled: false,
  shuffledOrder: [],

  // Actions
  setProblems: (problems) => set({ problems_or_problemsset: problems }),
  setIsShuffled: (shuffled) => set({ isShuffled: shuffled }),
  setShuffledOrder: (order) => set({ shuffledOrder: order }),
  clearProblems: () => set({
    problems_or_problemsset: [],
    isShuffled: false,
    shuffledOrder: []
  }),

  /**
   * Shuffles questions with solved questions placed at the end
   * 
   * @param sourceData - Optional source data to shuffle, uses store data if not provided
   */
  shuffleQuestions: (sourceData?: HybridProblem[]) => {
    const state = get();
    let problems: HybridProblem[] = [];

    if (sourceData && sourceData.length > 0) {
      problems = [...sourceData];
    } else if (state.problems_or_problemsset.length > 0) {
      problems = [...state.problems_or_problemsset];
    } else {
      return;
    }

    /**
     * Helper function to check if a problem/problemset is solved
     */
    const isSolved = (item: HybridProblem): boolean => {
      if ("isExpanded" in item) {
        // For ProblemsSet, check if ALL child problems are solved
        const problemSet = item as ProblemsSet;
        return problemSet.problems.every(problem =>
          problem.iscorrect !== null && problem.iscorrect !== undefined
        );
      } else {
        // For individual Problem
        const problem = item as Problem;
        return problem.iscorrect !== null && problem.iscorrect !== undefined;
      }
    };

    // Separate solved and unsolved items
    const solvedItems: HybridProblem[] = [];
    const unsolvedItems: HybridProblem[] = [];

    problems.forEach(item => {
      if (isSolved(item)) {
        solvedItems.push(item);
      } else {
        unsolvedItems.push(item);
      }
    });

    /**
     * Fisher-Yates shuffle algorithm
     */
    const shuffleArray = <T>(array: T[]): T[] => {
      const shuffled = [...array];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
    };

    const shuffledUnsolved = shuffleArray(unsolvedItems);
    const shuffledSolved = shuffleArray(solvedItems);

    // Combine: unsolved questions first, then solved questions
    const shuffledProblems = [...shuffledUnsolved, ...shuffledSolved];

    // Reassign absolute indices after shuffling to maintain correct navigation
    let absoluteIndex = 0;
    const shuffledWithNewIndices = shuffledProblems.map((item) => {
      if ("isExpanded" in item) {
        // For ProblemsSet, update each child's absoluteIndex
        const problemSet = item as ProblemsSet;
        const updatedProblems = problemSet.problems.map((problem) => ({
          ...problem,
          absoluteIndex: absoluteIndex++,
        }));
        return {
          ...problemSet,
          problems: updatedProblems,
          absoluteIndex: absoluteIndex - updatedProblems.length, // Set to first child's index
        };
      } else {
        // For individual Problem
        const problem = item as Problem;
        return {
          ...problem,
          absoluteIndex: absoluteIndex++,
        };
      }
    });

    // Create shuffled order indices
    const shuffledOrder = shuffledWithNewIndices.map((_, index) => index);

    set({
      problems_or_problemsset: shuffledWithNewIndices,
      isShuffled: true,
      shuffledOrder: shuffledOrder,
    });

    console.log('Questions shuffled successfully. New order:', shuffledOrder.slice(0, 5));
  },

  /**
   * Update problems data with attempt results from the result window
   * 
   * @param attemptResults - Array of attempt results with problemid and iscorrect status
   */
  updateProblemsWithAttemptData: (attemptResults) => {
    const state = get();

    // Create a map for quick lookup of attempt results
    const attemptMap = new Map<number, boolean>();
    attemptResults.forEach(result => {
      attemptMap.set(result.problemid, result.iscorrect);
    });

    // Update problems data with new attempt information
    const updatedProblems = state.problems_or_problemsset.map(item => {
      if ("isExpanded" in item) {
        // ProblemsSet - update individual problems within the set
        const problemSet = item as ProblemsSet;
        const updatedChildProblems = problemSet.problems.map(problem => {
          const problemId = parseInt(problem.problemid, 10);
          if (attemptMap.has(problemId)) {
            return {
              ...problem,
              iscorrect: attemptMap.get(problemId)
            };
          }
          return problem;
        });

        return {
          ...problemSet,
          problems: updatedChildProblems
        };
      } else {
        // Individual Problem
        const problem = item as Problem;
        const problemId = parseInt(problem.problemid, 10);
        if (attemptMap.has(problemId)) {
          return {
            ...problem,
            iscorrect: attemptMap.get(problemId)
          };
        }
      }
      return item;
    });

    // Update the store with the new data
    set({ problems_or_problemsset: updatedProblems });

    console.log(`✅ Updated problems store with attempt data for ${attemptResults.length} questions`);
  },
}));