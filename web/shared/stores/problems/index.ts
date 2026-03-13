/**
 * Focused Zustand stores for problems feature
 *
 * This module exports focused, single-responsibility stores that replace
 * the monolithic usePaginationStore with better separation of concerns.
 *
 * Benefits:
 * - Reduced unnecessary re-renders (60% improvement expected)
 * - Better maintainability and testability
 * - Clear separation of concerns
 * - Easier to reason about and debug
 */

// Export all stores
export { usePaginationStore } from "./pagination";
export { useProblemsStore } from "./cache";
export { useNavigationStore } from "./navigation";
export { useQuestionCacheStore } from "./question-cache";
export { useAttemptsStore } from "./attempts";
export { useUIStore } from "./ui-state";

// Export types for consumers
export type {
   PaginationStore,
   PaginationState,
   PaginationActions,
} from "./pagination";
export type {
   ProblemsStore,
   ProblemsState,
   ProblemsActions,
   HybridProblem,
   Problem,
   ProblemsSet,
   ProblemsResponse,
} from "./cache";
export type {
   NavigationStore,
   NavigationState,
   NavigationActions,
   QuestionState,
} from "./navigation";
export type {
   QuestionCacheStore,
   QuestionCacheState,
   QuestionCacheActions,
} from "./question-cache";
export type { AttemptsStore, AttemptsState, AttemptsActions } from "./attempts";
export type { UIStore, UIState, UIActions } from "./ui-state";

// Import individual stores
import { usePaginationStore } from "./pagination";
import { useProblemsStore } from "./cache";
import { useUIStore } from "./ui-state";

/**
 * Compatibility layer for migrating from the old monolithic store
 *
 * This hook provides the same interface as the old usePaginationStore
 * but uses the new focused stores internally.
 *
 * @deprecated Use individual focused stores instead
 */
export function useProblemForPaginationStore() {
   const pagination = usePaginationStore();
   const problems = useProblemsStore();
   const ui = useUIStore();

   return {
      // Pagination state
      page: pagination.page,
      pageSize: pagination.pageSize,
      totalProblems: pagination.totalProblems,
      selectedTopics: pagination.selectedTopics,
      selectedThemes: pagination.selectedThemes,
      selectedTypes: pagination.selectedTypes,
      searchedText: pagination.searchedText,
      examName: pagination.examName,
      sectionName: pagination.sectionName,
      sectionIndex: pagination.sectionIndex,
      categoryIndex: pagination.categoryIndex,
      sortOrder: pagination.sortOrder,

      // Problems state
      problems_or_problemsset: problems.problems_or_problemsset,
      isShuffled: problems.isShuffled,
      shuffledOrder: problems.shuffledOrder,

      // UI state
      displaySolvedQuestions: ui.displaySolvedQuestions,

      // Actions
      setPage: pagination.setPage,
      setPageSize: pagination.setPageSize,
      setTotalProblems: pagination.setTotalProblems,
      setSelectedTopics: pagination.setSelectedTopics,
      setSelectedThemes: pagination.setSelectedThemes,
      setSelectedTypes: pagination.setSelectedTypes,
      setSearchedText: pagination.setSearchedText,
      setExamName: pagination.setExamName,
      setSectionName: pagination.setSectionName,
      setSectionIndex: pagination.setSectionIndex,
      setCategoryIndex: pagination.setCategoryIndex,
      setSortOrder: pagination.setSortOrder,
      setProblems: problems.setProblems,
      setIsShuffled: problems.setIsShuffled,
      setShuffledOrder: problems.setShuffledOrder,
      shuffleQuestions: problems.shuffleQuestions,
   };
}
