/**
 * Pagination Cache Store
 *
 * Zustand store that integrates with the PaginationCacheService to provide
 * reactive state management for the intelligent pagination caching system.
 * This store replaces the inefficient fetch-all approach with smart caching.
 */

import { create } from "zustand";
import { HybridProblem } from "@/shared/stores/problems/cache";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { PaginationCacheService } from "../services/pagination-cache.service";
import { QuestionIdManager } from "../lib/question-id-manager";
import { CacheStats, NavigationState } from "../types/pagination-cache.types";

// Global instance of the cache service
let cacheService: PaginationCacheService;

/**
 * Helper function to sync navigation store with master question ID list
 * This ensures navigation store contains the complete question order for cross-page navigation
 * @param sectionId - The section ID to get master question list from cache
 * @param context - Context for logging (e.g., 'shuffle', 'initialization')
 */
const syncNavigationStoreWithMasterList = (
   sectionId: string,
   context: string = "sync"
) => {
   try {
      if (!cacheService) {
         console.warn(
            `⚠️ Cache service not available for navigation store sync during ${context}`
         );
         return;
      }

      const questionIdManager = cacheService.getQuestionIdManager(sectionId);
      if (questionIdManager) {
         const questionIdEntries = questionIdManager.getActiveIds();

         // Convert QuestionIdEntry to the format expected by navigation store
         const navigationQuestionIds: (number | { [key: string]: number[] })[] =
            [];

         questionIdEntries.forEach((entry) => {
            if ("problemid" in entry) {
               // Individual problem
               navigationQuestionIds.push(entry.problemid);
            } else if ("problemsSetId" in entry && entry.problems) {
               // Problem set - add as an object with key being the set ID
               const problemSetKey = `set_${entry.problemsSetId}`;
               const childIds = entry.problems.map((p) => p.problemid);
               navigationQuestionIds.push({ [problemSetKey]: childIds });
            }
         });

         // Update both navigation store and our master list
         useNavigationStore.getState().setQuestionIds(navigationQuestionIds);

         // Update master list in cache store
         usePaginationCacheStore.setState({
            masterQuestionIds: navigationQuestionIds,
         });

         console.log(
            `✅ Navigation store and master list synced with ${navigationQuestionIds.length} questions during ${context}`
         );
         console.log("🔍 SYNC DEBUG:", {
            context: context,
            navigationQuestionIdsLength: navigationQuestionIds.length,
            first10NavigationIds: navigationQuestionIds
               .slice(0, 10)
               .map((id) =>
                  typeof id === "number" ? id : `Set:${Object.keys(id)[0]}`
               ),
         });
      } else {
         console.warn(
            `⚠️ Question ID manager not found for section ${sectionId} during ${context}`
         );
      }
   } catch (syncError) {
      console.warn(
         `⚠️ Failed to sync navigation store during ${context}:`,
         syncError
      );
      // Don't throw - sync failures shouldn't break main operations
   }
};

export interface PaginationCacheState {
   // Master question ID list - single source of truth for all question ordering
   masterQuestionIds: (number | { [key: string]: number[] })[];

   // Current page data (subset of master list)
   currentPageData: HybridProblem[];

   // Navigation state
   currentPage: number;
   totalPages: number;
   totalQuestions: number;

   // Section management
   currentSectionId: string;
   availableSections: string[];

   // Filter and shuffle state
   isShuffled: boolean;
   isFiltered: boolean;
   activeFilters: string[];

   // Loading states
   isLoading: boolean;
   isShuffling: boolean;
   isMovingSolved: boolean;
   isPrefetching: boolean;

   // Cache statistics
   cacheStats: CacheStats;

   // Initialization state
   isCacheInitialized: boolean;

   // Error state
   lastError: string | null;
}

export interface PaginationCacheActions {
   // Service initialization
   initializeService: (config?: any, userId?: number) => void;

   // Section management
   initializeSection: (
      sectionId: string,
      questionIds: string[],
      totalQuestions: number
   ) => Promise<boolean>;
   initializeSectionWithHybridData: (
      sectionId: string,
      hybridProblems: HybridProblem[],
      totalQuestions: number
   ) => Promise<boolean>;
   switchToSection: (sectionId: string) => Promise<boolean>;

   // Navigation actions
   navigateToPage: (pageNumber: number) => Promise<boolean>;
   navigateNext: () => Promise<boolean>;
   navigatePrevious: () => Promise<boolean>;
   jumpToPage: (pageNumber: number) => Promise<boolean>;
   updateConfig: (config: any) => Promise<void>;

   // Filter actions
   applyTagFilter: (tags: string[]) => Promise<boolean>;
   removeAllFilters: () => Promise<boolean>;

   // Shuffle actions
   shuffleQuestions: (sectionId?: string) => Promise<boolean>;
   moveSolvedToEnd: () => Promise<boolean>;
   restoreOriginalOrder: () => Promise<boolean>;

   // Cache management
   clearCache: (sectionId?: string) => void;
   refreshCacheStats: () => void;

   // Error handling
   clearError: () => void;
   setError: (error: string) => void;

   // Direct state updates (for internal use)
   setCurrentPageData: (data: HybridProblem[]) => void;
   setLoadingState: (isLoading: boolean) => void;
   setShufflingState: (isShuffling: boolean) => void;
   setPrefetchingState: (isPrefetching: boolean) => void;

   // Attempt data updates
   updateCacheWithAttemptData: (
      attemptResults: Array<{ problemid: number; iscorrect: boolean }>
   ) => void;
}

export type PaginationCacheStore = PaginationCacheState &
   PaginationCacheActions;

/**
 * Initialize the cache service if not already initialized
 */
function ensureCacheService() {
   if (!cacheService) {
      cacheService = new PaginationCacheService({
         maxPagesPerSection: 3,
         questionsPerPage: 10,
         enablePrefetch: true,
         prefetchDistance: 1,
         cacheTTL: 5 * 60 * 1000,
      });

      // Set up event listeners for cache events
      cacheService.addEventListener((event) => {
         console.log("Cache event:", event);
         // Could emit to analytics or monitoring here
      });
   }
}

/**
 * Zustand store for pagination cache management
 */
export const usePaginationCacheStore = create<PaginationCacheStore>(
   (set, get) => ({
      // Initial state
      masterQuestionIds: [],
      currentPageData: [],
      currentPage: 1,
      totalPages: 0,
      totalQuestions: 0,
      currentSectionId: "",
      availableSections: [],
      isShuffled: false,
      isFiltered: false,
      activeFilters: [],
      isLoading: false,
      isShuffling: false,
      isMovingSolved: false,
      isPrefetching: false,
      cacheStats: {
         hits: 0,
         misses: 0,
         hitRatio: 0,
         totalCachedPages: 0,
         estimatedMemoryUsage: 0,
         prefetchCount: 0,
      },
      isCacheInitialized: false,
      lastError: null,

      // Service initialization
      initializeService: (config = {}, userId) => {
         // Re-initialize the singleton service if config or userId changed significantly
         // or just update parameters on existing one
         ensureCacheService();

         if (userId && cacheService) {
            cacheService.setUserId(userId);
         }

         // If initializing a new service context, clear store state
         set({ lastError: null });
         console.log("✅ PaginationCacheService synced with store");
      },

      // Section management with HybridProblem data
      initializeSectionWithHybridData: async (
         sectionId: string,
         hybridProblems: HybridProblem[],
         totalQuestions: number
      ) => {
         try {
            ensureCacheService();
            // IMMEDIATE RESET: Clear previous data to prevent stale display
            set({
               isLoading: true,
               lastError: null,
               currentSectionId: sectionId,
               currentPageData: [], // Clear old data
               masterQuestionIds: [], // Clear old indices
               isCacheInitialized: false
            });

            console.log(`📂 Initializing section ${sectionId} with ${hybridProblems.length} hybrid problems`);

            const result = cacheService.initializeSectionWithHybridData(
               sectionId,
               hybridProblems,
               totalQuestions
            );

            if (result.success) {
               const questionsPerPage = cacheService.getConfig().questionsPerPage;
               const totalPages = Math.ceil(totalQuestions / questionsPerPage);

               set({
                  totalPages,
                  totalQuestions,
                  isShuffled: false,
                  isFiltered: false,
                  activeFilters: [],
               });

               // Add to available sections if not already present
               const state = get();
               if (!state.availableSections.includes(sectionId)) {
                  set({
                     availableSections: [...state.availableSections, sectionId],
                  });
               }

               // CRITICAL: Successfully loading the first page is required to set up the cache
               try {
                  const firstPageResult = await cacheService.jumpToPage(sectionId, 1);

                  if (firstPageResult.success) {
                     // Sync navigation store BEFORE turning off loading
                     // This prevents the user from clicking before the store is ready
                     syncNavigationStoreWithMasterList(sectionId, "initialization");

                     set({
                        currentPageData: firstPageResult.data.questionData,
                        currentPage: 1,
                        isLoading: false,
                        isCacheInitialized: true
                     });

                     console.log(`✅ Section ${sectionId} initialization complete. Ready.`);
                  } else {
                     throw new Error(firstPageResult.error || "Failed to load first page data");
                  }
               } catch (error: any) {
                  console.error("❌ Error loading first page during initialization:", error);
                  set({ isLoading: false, lastError: error.message });
               }

               return true;
            } else {
               console.error("❌ Failed to initialize section:", result.error);
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to initialize section",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error in initializeSectionWithHybridData:", error);
            set({
               isLoading: false,
               lastError: error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      // Section management (legacy method)
      initializeSection: async (sectionId, questionIds, totalQuestions) => {
         try {
            ensureCacheService();
            set({
               isLoading: true,
               lastError: null,
               currentSectionId: sectionId,
               currentPageData: [],
               masterQuestionIds: [],
               isCacheInitialized: false
            });

            const result = cacheService.initializeSection(
               sectionId,
               questionIds,
               totalQuestions
            );

            if (result.success) {
               const questionsPerPage = cacheService.getConfig().questionsPerPage;
               const totalPages = Math.ceil(totalQuestions / questionsPerPage);

               set({
                  totalPages,
                  totalQuestions,
               });

               // Automatically load first page
               try {
                  const firstPageResult = await cacheService.jumpToPage(sectionId, 1);

                  if (firstPageResult.success) {
                     syncNavigationStoreWithMasterList(sectionId, "initialization");
                     set({
                        currentPageData: firstPageResult.data.questionData,
                        currentPage: 1,
                        isLoading: false,
                        isCacheInitialized: true
                     });
                  } else {
                     throw new Error(firstPageResult.error);
                  }
               } catch (error: any) {
                  set({ isLoading: false, lastError: error.message });
               }

               return true;
            } else {
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to initialize section",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error in initializeSection:", error);
            set({
               isLoading: false,
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      switchToSection: async (sectionId) => {
         try {
            ensureCacheService();
            if (get().currentSectionId === sectionId) return true;

            set({ isLoading: true, lastError: null });

            const result = cacheService.switchToSection(
               get().currentSectionId,
               sectionId
            );

            if (result.success) {
               const restoredPageData = result.data
                  ? result.data.questionData
                  : [];
               const restoredPage = result.data ? result.data.pageNumber : 1;

               // Sync navigation store FIRST
               syncNavigationStoreWithMasterList(sectionId, "section-switch");

               set({
                  currentSectionId: sectionId,
                  currentPageData: restoredPageData,
                  currentPage: restoredPage,
                  isLoading: false,
               });

               return true;
            } else {
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to switch section",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error switching section:", error);
            set({
               isLoading: false,
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      // Navigation actions
      navigateToPage: async (pageNumber) => {
         const state = get();
         const currentPage = state.currentPage;

         // Determine if this is adjacent navigation or a jump
         const isAdjacent = Math.abs(pageNumber - currentPage) === 1;

         if (isAdjacent) {
            const direction = pageNumber > currentPage ? "next" : "previous";
            if (direction === "next") {
               return get().navigateNext();
            } else {
               return get().navigatePrevious();
            }
         } else {
            return get().jumpToPage(pageNumber);
         }
      },

      navigateNext: async () => {
         try {
            ensureCacheService();
            const state = get();
            console.log(
               `📄 Attempting to navigate to next page from page ${state.currentPage} in section ${state.currentSectionId}`
            );
            set({ lastError: null });

            const result = await cacheService.navigateToAdjacentPage(
               state.currentSectionId,
               "next"
            );

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: result.data.pageNumber,
               });

               // Master list doesn't change when navigating pages - no sync needed

               return true;
            } else {
               // If no current page is set, try to jump to page 1
               if (result.error === "No current page set") {
                  return get().jumpToPage(1);
               }
               set({
                  lastError: result.error || "Failed to navigate to next page",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error navigating to next page:", error);
            set({
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      navigatePrevious: async () => {
         try {
            ensureCacheService();
            const state = get();
            set({ lastError: null });

            const result = await cacheService.navigateToAdjacentPage(
               state.currentSectionId,
               "previous"
            );

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: result.data.pageNumber,
               });

               // Master list doesn't change when navigating pages - no sync needed

               return true;
            } else {
               // If no current page is set, try to jump to page 1
               if (result.error === "No current page set") {
                  return get().jumpToPage(1);
               }
               set({
                  lastError:
                     result.error || "Failed to navigate to previous page",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error navigating to previous page:", error);
            set({
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      jumpToPage: async (pageNumber) => {
         try {
            ensureCacheService();
            const state = get();
            set({ isLoading: true, lastError: null });

            const result = await cacheService.jumpToPage(
               state.currentSectionId,
               pageNumber
            );

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: result.data.pageNumber,
                  isLoading: false,
               });

               // Master list doesn't change when jumping to pages - no sync needed

               return true;
            } else {
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to jump to page",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error jumping to page:", error);
            set({
               isLoading: false,
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      // Filter actions
      applyTagFilter: async (tags) => {
         try {
            ensureCacheService();
            const state = get();
            set({ isLoading: true, lastError: null });

            const result = await cacheService.applyTagFilter(
               state.currentSectionId,
               tags
            );

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: 1, // Filters start from page 1
                  isFiltered: true,
                  activeFilters: tags,
                  isShuffled: false, // Reset shuffle when filtering
                  isLoading: false,
               });

               // Sync navigation store with filtered question order
               syncNavigationStoreWithMasterList(
                  state.currentSectionId,
                  "filter"
               );

               return true;
            } else {
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to apply filter",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error applying filter:", error);
            set({
               isLoading: false,
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      removeAllFilters: async () => {
         try {
            ensureCacheService();
            const state = get();
            set({ isLoading: true, lastError: null });

            const result = await cacheService.removeAllFilters(
               state.currentSectionId
            );

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: result.data.pageNumber,
                  isFiltered: false,
                  activeFilters: [],
                  isShuffled: false, // Reset shuffle when removing filters
                  isLoading: false,
               });

               // Sync navigation store with restored question order
               syncNavigationStoreWithMasterList(
                  state.currentSectionId,
                  "filter-removal"
               );

               return true;
            } else {
               set({
                  isLoading: false,
                  lastError: result.error || "Failed to remove filters",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error removing filters:", error);
            set({
               isLoading: false,
               lastError:
                  error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      // Shuffle actions
      shuffleQuestions: async (targetSectionId?: string) => {
         try {
            ensureCacheService();
            const state = get();
            const sectionToShuffle = targetSectionId || state.currentSectionId;

            set({ isShuffling: true, lastError: null });

            // Wait for section to be initialized if it's currently empty or different from target
            if (!get().currentSectionId || (targetSectionId && get().currentSectionId !== targetSectionId)) {
               console.log(
                  `⏳ Waiting for section ${sectionToShuffle || 'initialization'}...`
               );

               let attempts = 0;
               const maxAttempts = 50; // 50 * 100ms = 5 seconds

               while (get().currentSectionId !== sectionToShuffle && attempts < maxAttempts) {
                  await new Promise((resolve) => setTimeout(resolve, 100));
                  attempts++;

                  // If we don't have a target but currentSectionId just became available, stop waiting
                  if (!targetSectionId && get().currentSectionId) break;
               }

               const currentState = get();
               if (!currentState.currentSectionId || (targetSectionId && currentState.currentSectionId !== targetSectionId)) {
                  set({
                     isShuffling: false,
                     lastError:
                        "Section not properly initialized. Please wait for the page to load completely and try again.",
                  });
                  return false;
               }
            }

            const finalSectionId = get().currentSectionId;
            const result = await cacheService.shuffleQuestions(finalSectionId);

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: result.data.pageNumber,
                  isShuffled: true,
                  isShuffling: false,
               });

               syncNavigationStoreWithMasterList(finalSectionId, "shuffle");
               return true;
            } else {
               set({
                  isShuffling: false,
                  lastError: result.error || "Failed to shuffle questions",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error shuffling questions:", error);
            set({
               isShuffling: false,
               lastError: error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      moveSolvedToEnd: async () => {
         try {
            ensureCacheService();
            const state = get();
            const sectionId = state.currentSectionId;

            if (!sectionId) {
               console.warn("⚠️ No section initialized for moveSolvedToEnd");
               return false;
            }

            set({ isMovingSolved: true, lastError: null });

            const result = await cacheService.moveSolvedToEnd(sectionId);

            if (result.success) {
               set({
                  currentPageData: result.data.questionData,
                  currentPage: 1,
                  isShuffled: true,
                  isMovingSolved: false,
               });

               syncNavigationStoreWithMasterList(sectionId, "move-solved-to-end");
               return true;
            } else {
               set({
                  isMovingSolved: false,
                  lastError: result.error || "Failed to move solved questions to end",
               });
               return false;
            }
         } catch (error) {
            console.error("❌ Error moving solved to end:", error);
            set({
               isMovingSolved: false,
               lastError: error instanceof Error ? error.message : "Unknown error",
            });
            return false;
         }
      },

      restoreOriginalOrder: async () => {
         // For now, removing filters will restore original order
         // This could be enhanced to have separate restore functionality
         return get().removeAllFilters();
      },

      // Cache management
      clearCache: (sectionId) => {
         if (cacheService) {
            if (sectionId) {
               // Clear specific section
               cacheService.clearSectionCache(sectionId);
            } else {
               // Clear all caches
               cacheService.clearAllCaches();
            }
         }

         // Reset relevant state
         set({
            currentPageData: [],
            currentPage: 1,
            totalPages: 0,
            totalQuestions: 0,
            currentSectionId: sectionId ? get().currentSectionId : "",
            isShuffled: false,
            isFiltered: false,
            activeFilters: [],
            cacheStats: {
               hits: 0,
               misses: 0,
               hitRatio: 0,
               totalCachedPages: 0,
               estimatedMemoryUsage: 0,
               prefetchCount: 0,
            },
         });
      },

      updateConfig: async (config) => {
         ensureCacheService();
         if (cacheService) {
            await cacheService.updateConfig(config);

            // Update totalPages if questionsPerPage changed
            if (config.questionsPerPage) {
               const state = get();
               const totalPages = Math.ceil(
                  state.totalQuestions / config.questionsPerPage
               );

               // Also update the current page data from the newly fetched page 1 in the service
               const newCurrentPageData = cacheService.getCurrentPageData(state.currentSectionId) || [];

               set({
                  totalPages,
                  currentPage: 1,
                  currentPageData: newCurrentPageData
               });
            }
         }
      },

      refreshCacheStats: () => {
         if (cacheService) {
            const stats = cacheService.getCacheStats();
            set({ cacheStats: stats });
         }
      },

      // Error handling
      clearError: () => set({ lastError: null }),

      setError: (error) => set({ lastError: error }),

      // Direct state updates (for internal use)
      setCurrentPageData: (data) => set({ currentPageData: data }),

      setLoadingState: (isLoading) => set({ isLoading }),

      setShufflingState: (isShuffling) => set({ isShuffling }),

      setPrefetchingState: (isPrefetching) => set({ isPrefetching }),

      // Update cache with attempt data from result window
      updateCacheWithAttemptData: (attemptResults) => {
         const state = get();

         // Create a map for quick lookup of attempt results
         const attemptMap = new Map<number, boolean>();
         attemptResults.forEach((result) => {
            attemptMap.set(result.problemid, result.iscorrect);
         });

         // Update current page data with new attempt information
         const updatedPageData = state.currentPageData.map((problem) => {
            if ("problemid" in problem) {
               // Individual problem
               const problemId = parseInt(problem.problemid, 10);
               if (attemptMap.has(problemId)) {
                  return {
                     ...problem,
                     iscorrect: attemptMap.get(problemId),
                  };
               }
            } else if ("problemsSetId" in problem && problem.problems) {
               // Problem set - update individual problems within the set
               const updatedProblems = problem.problems.map((childProblem) => {
                  const childId = parseInt(childProblem.problemid, 10);
                  if (attemptMap.has(childId)) {
                     return {
                        ...childProblem,
                        iscorrect: attemptMap.get(childId),
                     };
                  }
                  return childProblem;
               });

               return {
                  ...problem,
                  problems: updatedProblems,
               };
            }
            return problem;
         });

         // Update the store with the new data
         set({ currentPageData: updatedPageData });

         console.log(
            `✅ Updated cache with attempt data for ${attemptResults.length} questions`
         );
      },
   })
);

// Hook for easier access to just the service instance
export function usePaginationCacheService(): PaginationCacheService {
   ensureCacheService();
   return cacheService;
}
