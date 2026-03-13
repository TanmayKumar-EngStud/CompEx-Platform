/**
 * @deprecated This file is being migrated to focused stores.
 * Use the new focused stores from @/shared/stores/problems instead.
 *
 * Compatibility layer for existing code during migration.
 */

// Import and re-export focused stores and types
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useNavigationStore, type QuestionState } from "@/shared/stores/problems/navigation";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";
import { useAttemptsStore, type AttemptsStore } from "@/shared/stores/problems/attempts";
import {
   type Problem,
   type ProblemsSet,
   type HybridProblem,
   type ProblemsResponse,
} from "@/shared/stores/problems/cache";

// Re-export for compatibility
export {
   usePaginationStore,
   type Problem,
   type ProblemsSet,
   type HybridProblem,
   type ProblemsResponse,
};

// Re-export types
export { type QuestionState } from "@/shared/stores/problems/navigation";
export type UserAttempts = AttemptsStore;

/**
 * Compatibility wrapper for questionList that combines navigation and cache stores
 * @deprecated Use focused stores directly from @/shared/stores/problems
 */
export function questionList() {
   const navigation = useNavigationStore();
   const cache = useQuestionCacheStore();

   const storeAPI = {
      // Navigation state and actions
      questionIds: navigation.questionIds,
      questionDataList: navigation.questionDataList,
      windowSize: navigation.windowSize,
      start: navigation.start,
      setStart: navigation.setStart,
      setQuestionIds: navigation.setQuestionIds,
      pasteQuestionDataList: navigation.pasteQuestionDataList,
      setQuestionDataList: navigation.setQuestionDataList,

      // Cache state and actions
      questionCache: cache.questionCache,
      cacheSize: cache.cacheSize,
      prefetchSize: cache.prefetchSize,
      lastPrefetchIndex: cache.lastPrefetchIndex,
      addToCache: cache.addToCache,
      getFromCache: cache.getFromCache,
      markQuestionAccessed: cache.markQuestionAccessed,
      evictLRUFromCache: cache.evictLRUFromCache,
      clearCache: cache.clearCache,

      // Prefetch with navigation context
      prefetchQuestions: (currentIndex: number) =>
         cache.prefetchQuestions(currentIndex, navigation.questionIds),

      // Zustand compatibility - getState returns the same object
      getState: () => storeAPI,
   };

   return storeAPI;
}

/**
 * Legacy compatibility export
 * @deprecated Use useAttemptsStore from focused stores
 */
export const useAttemptStore = useAttemptsStore;

// Legacy export for backward compatibility
export const questionDetails = {
   type: "",
   problemid: 0,
   title: "questionTitle",
   text: "question",
   problemoptions: [{ optionid: 0, optiontext: "" }],
   metadata: {},
};

// Keep legacy interface for backward compatibility
export interface PorblemsResponse {
   problemData: HybridProblem[];
   totalProblems: number;
}
