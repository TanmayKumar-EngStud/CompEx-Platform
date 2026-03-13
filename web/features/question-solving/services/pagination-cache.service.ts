/**
 * Pagination Cache Service
 *
 * This service orchestrates the intelligent pagination caching system using
 * doubly-linked lists for each section. It provides the main interface for
 * all cache operations and implements the scenarios defined in the roadmap.
 */

import { DoublyLinkedList } from "../lib/doubly-linked-list";
import {
   SectionCache,
   GlobalCache,
   CacheConfig,
   CacheOperationResult,
   NavigationState,
   CacheStats,
   CacheEvent,
   QuestionIdEntry,
} from "../types/pagination-cache.types";
import { HybridProblem, Problem, ProblemsSet } from "@/shared/stores/problems/cache";
import { ShuffleService, type ShuffleStrategy } from "./shuffle.service";
import { QuestionIdManager } from "../lib/question-id-manager";

export class PaginationCacheService {
   private globalCache: GlobalCache;
   private config: CacheConfig;
   private sectionLists: Map<string, DoublyLinkedList> = new Map();
   private questionIdManagers: Map<string, QuestionIdManager> = new Map();
   private shuffleService: ShuffleService;
   private navigationState: NavigationState;
   private stats: CacheStats;
   private eventListeners: ((event: CacheEvent) => void)[] = [];
   private userId: number = 1; // Store user ID for API calls

   constructor(config: Partial<CacheConfig> = {}) {
      this.config = {
         maxPagesPerSection: 3,
         questionsPerPage: 10,
         enablePrefetch: true,
         prefetchDistance: 1,
         cacheTTL: 5 * 60 * 1000, // 5 minutes
         ...config,
      };

      // Initialize shuffle service
      this.shuffleService = new ShuffleService({
         defaultStrategy: "smart",
         enablePerformanceWeights: true,
         enableCategoryBalancing: true,
         enableDifficultyProgression: true,
         enableSpacedRepetition: false, // Can be enabled when user analytics are available
         logShuffleEvents: true,
      });

      this.globalCache = {
         sections: new Map(),
         currentSectionId: "",
         maxCacheSize: this.config.maxPagesPerSection,
         createdAt: Date.now(),
      };

      this.navigationState = {
         currentPage: 1,
         previousPage: 1,
         direction: "next",
         lastNavigationTime: Date.now(),
      };

      this.stats = {
         hits: 0,
         misses: 0,
         hitRatio: 0,
         totalCachedPages: 0,
         estimatedMemoryUsage: 0,
         prefetchCount: 0,
      };

      // console.log(
      //    "🚀 PaginationCacheService initialized with config:",
      //    this.config
      // );
   }

   /**
    * Update cache configuration dynamically
    */
   async updateConfig(newConfig: Partial<CacheConfig>): Promise<void> {
      const oldQuestionsPerPage = this.config.questionsPerPage;
      this.config = { ...this.config, ...newConfig };

      // If boundary-changing values modified, we must clear caches
      if (
         newConfig.questionsPerPage !== undefined &&
         newConfig.questionsPerPage !== oldQuestionsPerPage
      ) {
         console.log(
            `📏 Page size changed from ${oldQuestionsPerPage} to ${this.config.questionsPerPage}. Clearing page caches.`
         );

         // Clear only page nodes, keep section metadata
         this.clearPageCachesOnly();

         // Re-initialize question managers with new page size for any existing sections
         for (const [sectionId, manager] of this.questionIdManagers.entries()) {
            const activeIds = manager.getActiveIds();
            const newManager = new QuestionIdManager(
               activeIds,
               this.config.questionsPerPage
            );
            this.questionIdManagers.set(sectionId, newManager);

            const sectionCache = this.globalCache.sections.get(sectionId);
            if (sectionCache) {
               sectionCache.questionsPerPage = this.config.questionsPerPage;
               sectionCache.totalPages = Math.ceil(
                  sectionCache.totalQuestions / this.config.questionsPerPage
               );
            }
         }

         // Re-fetch current page for the active section if possible
         if (this.globalCache.currentSectionId) {
            await this.jumpToPage(this.globalCache.currentSectionId, 1);
         }
      }

      this.emitEvent({
         type: "prefetch_completed", // Re-using existing type or could add config_updated
         sectionId: this.globalCache.currentSectionId,
         pageNumber: 0,
      });
   }

   /**
    * Get current configuration
    */
   getConfig(): CacheConfig {
      return { ...this.config };
   }

   /**
    * Set the user ID for API calls
    */
   setUserId(userId: number): void {
      this.userId = userId;
      // console.log(`👤 User ID set to ${userId} for cache service`);
   }

   /**
    * Initialize a new section cache with HybridProblem data (preferred method)
    */
   initializeSectionWithHybridData(
      sectionId: string,
      hybridProblems: HybridProblem[],
      totalQuestions: number
   ): CacheOperationResult {
      try {
         console.log(
            `📂 Initializing section cache: ${sectionId} (${totalQuestions} questions)`
         );
         console.log(`🔍 Sample hybrid problems:`, hybridProblems.slice(0, 3));

         const totalPages = Math.ceil(
            totalQuestions / this.config.questionsPerPage
         );

         // Create doubly-linked list for this section
         const sectionList = new DoublyLinkedList(
            sectionId,
            this.config.maxPagesPerSection
         );
         this.sectionLists.set(sectionId, sectionList);

         // Convert HybridProblem to QuestionIdEntry for the manager with error handling
         let questionIdEntries;
         try {
            questionIdEntries =
               this.convertHybridProblemsToQuestionIdEntries(hybridProblems);
         } catch (conversionError) {
            console.error(
               `❌ Failed to convert HybridProblems for section ${sectionId}:`,
               conversionError
            );
            throw new Error(
               `HybridProblem conversion failed: ${conversionError}`
            );
         }

         const questionIdManager = new QuestionIdManager(
            questionIdEntries,
            this.config.questionsPerPage
         );
         this.questionIdManagers.set(sectionId, questionIdManager);
         console.log(
            "Here is how questionIdManagers look like:-\n",
            questionIdManager.getActiveIds()
         );

         // Create section cache metadata using extracted question entries
         const sectionCache: SectionCache = {
            sectionId,
            currentNode: null as any, // Will be set when first page is added
            questionEntries: questionIdEntries,
            filteredQuestionEntries: [],
            totalQuestions: questionIdEntries.length,
            totalPages,
            isShuffled: false,
            isFiltered: false,
            activeFilters: [],
            originalPosition: 1,
            questionsPerPage: this.config.questionsPerPage,
         };

         this.globalCache.sections.set(sectionId, sectionCache);
         this.globalCache.currentSectionId = sectionId; // Set current section ID

         console.log(
            `✅ Section cache initialized successfully for ${sectionId}`
         );
         console.log(
            `📊 Cache status: ${this.globalCache.sections.size} sections cached`
         );

         this.emitEvent({
            type: "section_switched",
            fromSectionId: "",
            toSectionId: sectionId,
         });

         return { success: true, data: sectionCache };
      } catch (error) {
         console.error(`❌ Failed to initialize section ${sectionId}:`, error);
         return {
            success: false,
            error: `Failed to initialize section: ${error}`,
         };
      }
   }

   /**
    * Initialize a new section cache (legacy method with string IDs)
    */
   initializeSection(
      sectionId: string,
      questionIds: string[],
      totalQuestions: number
   ): CacheOperationResult {
      try {
         console.log(
            `📂 Initializing section cache: ${sectionId} (${totalQuestions} questions)`
         );
         console.log(`🔍 Sample question IDs:`, questionIds.slice(0, 10));

         const totalPages = Math.ceil(
            totalQuestions / this.config.questionsPerPage
         );

         // Create doubly-linked list for this section
         const sectionList = new DoublyLinkedList(
            sectionId,
            this.config.maxPagesPerSection
         );
         this.sectionLists.set(sectionId, sectionList);

         // Convert string IDs to QuestionIdEntry format for the manager
         const questionIdEntries =
            this.convertStringIdsToQuestionIdEntries(questionIds);
         const questionIdManager = new QuestionIdManager(
            questionIdEntries,
            this.config.questionsPerPage
         );
         this.questionIdManagers.set(sectionId, questionIdManager);
         console.log(
            "Here is how questionIdManagers look like:-\n",
            questionIdManager.getActiveIds()
         );

         // Create section cache metadata using the extractedEntries
         const sectionCache: SectionCache = {
            sectionId,
            currentNode: null as any, // Will be set when first page is added
            questionEntries: questionIdEntries,
            filteredQuestionEntries: [],
            totalQuestions: questionIdEntries.length,
            totalPages,
            isShuffled: false,
            isFiltered: false,
            activeFilters: [],
            originalPosition: 1,
            questionsPerPage: this.config.questionsPerPage,
         };

         this.globalCache.sections.set(sectionId, sectionCache);
         this.globalCache.currentSectionId = sectionId; // Set current section ID

         console.log(
            `✅ Section cache initialized successfully for ${sectionId}`
         );
         console.log(
            `📊 Cache status: ${this.globalCache.sections.size} sections cached`
         );

         this.emitEvent({
            type: "section_switched",
            fromSectionId: "",
            toSectionId: sectionId,
         });

         return { success: true, data: sectionCache };
      } catch (error) {
         console.error(`❌ Failed to initialize section ${sectionId}:`, error);
         return {
            success: false,
            error: `Failed to initialize section: ${error}`,
         };
      }
   }

   /**
    * SCENARIO 1: Sequential Page Navigation (Adjacent Pages)
    * Navigate to the next or previous page with instant response from cache
    */
   async navigateToAdjacentPage(
      sectionId: string,
      direction: "next" | "previous"
   ): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);

      if (!sectionCache || !sectionList) {
         return { success: false, error: "Section not initialized" };
      }

      const currentNode = sectionList.getCurrentPage();
      if (!currentNode) {
         return { success: false, error: "No current page set" };
      }

      const targetPageNumber =
         direction === "next"
            ? currentNode.pageNumber + 1
            : currentNode.pageNumber - 1;

      // Check bounds
      if (targetPageNumber < 1 || targetPageNumber > sectionCache.totalPages) {
         return { success: false, error: "Page out of bounds" };
      }

      // Try to get from cache first (instant response)
      const cachedNode = sectionList.getPage(targetPageNumber);

      if (cachedNode) {
         // INSTANT RESPONSE - show from cache
         sectionList.setCurrentPage(targetPageNumber);
         sectionCache.currentNode = cachedNode;
         this.updateNavigationState(targetPageNumber, direction);

         this.stats.hits++;
         this.emitEvent({
            type: "cache_hit",
            sectionId,
            pageNumber: targetPageNumber,
         });

         // Background prefetch next page
         if (this.config.enablePrefetch) {
            const prefetchTargets = sectionList.getPrefetchTargets(direction);
            for (const pageNum of prefetchTargets) {
               this.prefetchPage(sectionId, pageNum);
            }
         }

         return { success: true, data: cachedNode };
      } else {
         // Cache miss - need to fetch
         this.stats.misses++;
         this.emitEvent({
            type: "cache_miss",
            sectionId,
            pageNumber: targetPageNumber,
         });

         const result = await this.fetchAndCachePage(
            sectionId,
            targetPageNumber
         );
         if (result.success) {
            sectionList.setCurrentPage(targetPageNumber);
            this.updateNavigationState(targetPageNumber, direction);
         }
         return result;
      }
   }

   /**
    * SCENARIO 3: Direct Page Jump (Non-Adjacent)
    * Navigate directly to a specific page with loading state
    */
   async jumpToPage(
      sectionId: string,
      targetPage: number
   ): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);

      if (!sectionCache || !sectionList) {
         return { success: false, error: "Section not initialized" };
      }

      if (targetPage < 1 || targetPage > sectionCache.totalPages) {
         return { success: false, error: "Page out of bounds" };
      }

      console.log(`🎯 Jumping to page ${targetPage} in section ${sectionId}`);

      // Clear entire cache for this section (as per roadmap)
      sectionList.clear();

      // Fetch target page data
      const result = await this.fetchAndCachePage(sectionId, targetPage);

      if (result.success) {
         sectionList.setCurrentPage(targetPage);
         sectionCache.currentNode = result.data;
         this.updateNavigationState(targetPage, "jump");

         // Background prefetch adjacent pages
         if (this.config.enablePrefetch) {
            const prefetchTargets = sectionList.getPrefetchTargets("both");
            for (const pageNum of prefetchTargets) {
               this.prefetchPage(sectionId, pageNum);
            }
         }
      }

      return result;
   }

   /**
    * SCENARIO 4: Section Switching
    * Switch between sections preserving cache state
    */
   switchToSection(
      fromSectionId: string,
      toSectionId: string
   ): CacheOperationResult {
      console.log(`🔄 Switching from ${fromSectionId} to ${toSectionId}`);

      const fromSection = this.globalCache.sections.get(fromSectionId);
      const toSection = this.globalCache.sections.get(toSectionId);

      // Store current state of fromSection (automatically preserved in cache)
      if (fromSection) {
         const fromList = this.sectionLists.get(fromSectionId);
         if (fromList) {
            const currentPage = fromList.getCurrentPage();
            if (currentPage) {
               console.log(
                  `💾 Preserved ${fromSectionId} at page ${currentPage.pageNumber}`
               );
            }
         }
      }

      // Switch to toSection
      if (toSection) {
         this.globalCache.currentSectionId = toSectionId;
         const toList = this.sectionLists.get(toSectionId);

         if (toList && toList.getCurrentPage()) {
            // Restore to where user left off
            const restoredPage = toList.getCurrentPage()!;
            console.log(
               `🔄 Restored ${toSectionId} to page ${restoredPage.pageNumber}`
            );

            this.emitEvent({
               type: "section_switched",
               fromSectionId,
               toSectionId,
            });
            return { success: true, data: restoredPage };
         } else {
            // No existing cache, will need to load page 1
            this.emitEvent({
               type: "section_switched",
               fromSectionId,
               toSectionId,
            });
            return { success: true, data: null };
         }
      }

      return { success: false, error: "Target section not found" };
   }

   /**
    * SCENARIO 5: Question Shuffling
    * Shuffle questions and rebuild cache using advanced shuffle service
    */
   async shuffleQuestions(
      sectionId: string,
      strategy: ShuffleStrategy = "smart"
   ): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);
      const questionIdManager = this.questionIdManagers.get(sectionId);

      if (!sectionCache || !sectionList || !questionIdManager) {
         return { success: false, error: "Section not initialized" };
      }

      console.log(
         `🔀 Shuffling questions for section: ${sectionId} using ${strategy} strategy`
      );

      const currentPage = sectionList.getCurrentPage()?.pageNumber || 1;

      try {
         // Get current active question IDs
         const activeIds = questionIdManager.getActiveIds();

         // Use the shuffle service for intelligent shuffling
         const shuffleContext = {
            sectionId,
            currentPage,
            isFiltered: sectionCache.isFiltered,
            activeFilters: sectionCache.activeFilters,
            totalQuestions: sectionCache.totalQuestions,
            questionsPerPage: this.config.questionsPerPage,
         };

         // Update question ID manager ⚠️⚠️⚠️⚠️
         await this.shuffleService.shuffleWithManager(
            questionIdManager,
            strategy,
            shuffleContext
         );
         sectionCache.isShuffled = true;

         // Clear cache and rebuild with shuffled data
         sectionList.clear();
         this.emitEvent({ type: "cache_cleared", sectionId });

         // Try to maintain current page position
         const targetPage = Math.min(currentPage, sectionCache.totalPages);

         const shuffledEntries = questionIdManager.getActiveIds();
         const result = await this.fetchAndCachePage(
            sectionId,
            targetPage,
            shuffledEntries
         );

         if (result.success) {
            sectionList.setCurrentPage(targetPage);
            sectionCache.currentNode = result.data;
            console.log(
               "⚠️ This is how questionIdManager looks like:-\n ",
               questionIdManager.getActiveIds()
            );
            // Background prefetch adjacent pages with shuffled data
            if (this.config.enablePrefetch) {
               const prefetchTargets = sectionList.getPrefetchTargets("both");
               for (const pageNum of prefetchTargets) {
                  this.prefetchPage(sectionId, pageNum, shuffledEntries);
               }
            }

            // Emit shuffle completion event
            this.emitEvent({
               type: "shuffle_completed",
               sectionId,
               strategy,
               algorithm: "fisher-yates",
               questionCount: questionIdManager.getActiveIds().length,
            });
         }

         return result;
      } catch (error) {
         console.error(`❌ Shuffle failed for section ${sectionId}:`, error);

         // Fallback to basic Fisher-Yates shuffle
         const entries = sectionCache.isFiltered
            ? sectionCache.filteredQuestionEntries
            : sectionCache.questionEntries;

         const shuffledEntries = this.fisherYatesShuffle(entries) as QuestionIdEntry[];

         // Update the appropriate entries list
         if (sectionCache.isFiltered) {
            sectionCache.filteredQuestionEntries = shuffledEntries;
         } else {
            sectionCache.questionEntries = shuffledEntries;
         }

         sectionCache.isShuffled = true;

         // Clear cache and rebuild with shuffled data
         sectionList.clear();
         this.emitEvent({ type: "cache_cleared", sectionId });

         // Try to maintain current page position
         const targetPage = Math.min(currentPage, sectionCache.totalPages);
         const result = await this.fetchAndCachePage(
            sectionId,
            targetPage,
            shuffledEntries
         );

         if (result.success) {
            sectionList.setCurrentPage(targetPage);
            sectionCache.currentNode = result.data;
         }

         return result;
      }
   }

   /**
    * SCENARIO 6: Move Solved Questions to End
    * Deterministic reorder: unsolved questions first (original order), solved last (original order)
    */
   async moveSolvedToEnd(
      sectionId: string
   ): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);
      const questionIdManager = this.questionIdManagers.get(sectionId);

      if (!sectionCache || !sectionList || !questionIdManager) {
         return { success: false, error: "Section not initialized" };
      }

      console.log(
         `📤 Moving solved questions to end for section: ${sectionId}`
      );

      try {
         // Get all active question IDs
         const activeIds = questionIdManager.getActiveIds();
         const allStringIds =
            QuestionIdManager.extractStringIdsFromQuestionIdEntries(activeIds);

         if (allStringIds.length === 0) {
            return { success: false, error: "No questions found" };
         }

         // Fetch iscorrect status for ALL questions in one batch
         const allQuestionData = await this.fetchQuestionDataByIds(
            allStringIds,
            this.userId
         );

         // Build a set of solved problem IDs
         const solvedProblemIds = new Set<number>();
         allQuestionData.forEach((item: any) => {
            if ("problems" in item && item.problems) {
               // Problem set: solved if ALL children are solved
               const allChildrenSolved = item.problems.every(
                  (child: any) =>
                     child.iscorrect !== null && child.iscorrect !== undefined
               );
               if (allChildrenSolved) {
                  // Mark all child IDs as solved
                  item.problems.forEach((child: any) => {
                     solvedProblemIds.add(
                        typeof child.problemid === "string"
                           ? parseInt(child.problemid, 10)
                           : child.problemid
                     );
                  });
               }
            } else if ("problemid" in item) {
               // Individual problem
               if (item.iscorrect !== null && item.iscorrect !== undefined) {
                  const pid =
                     typeof item.problemid === "string"
                        ? parseInt(item.problemid, 10)
                        : item.problemid;
                  solvedProblemIds.add(pid);
               }
            }
         });

         console.log(
            `📊 Found ${solvedProblemIds.size} solved problem IDs out of ${allStringIds.length} total`
         );

         // Helper to check if a QuestionIdEntry is solved
         const isEntrySolved = (entry: QuestionIdEntry): boolean => {
            if ("problemsSetId" in entry && entry.problems) {
               // Problem set: solved if ALL children are solved
               return entry.problems.every((child) =>
                  solvedProblemIds.has(child.problemid)
               );
            } else if ("problemid" in entry) {
               return solvedProblemIds.has(entry.problemid);
            }
            return false;
         };

         // Separate into unsolved and solved, preserving original order
         const unsolved = activeIds.filter((entry) => !isEntrySolved(entry));
         const solved = activeIds.filter((entry) => isEntrySolved(entry));

         console.log(
            `📤 Reordering: ${unsolved.length} unsolved first, ${solved.length} solved last`
         );

         // Combine: unsolved first, solved last
         const reordered = [...unsolved, ...solved];

         // Apply to the question ID manager
         questionIdManager.setShuffledActiveIds(reordered);
         sectionCache.isShuffled = true;

         // Clear cache and rebuild with reordered data
         sectionList.clear();
         this.emitEvent({ type: "cache_cleared", sectionId });

         // Jump to page 1
         const result = await this.fetchAndCachePage(
            sectionId,
            1,
            reordered
         );

         if (result.success) {
            sectionList.setCurrentPage(1);
            sectionCache.currentNode = result.data;

            // Prefetch adjacent pages
            if (this.config.enablePrefetch) {
               const prefetchTargets = sectionList.getPrefetchTargets("both");
               for (const pageNum of prefetchTargets) {
                  this.prefetchPage(sectionId, pageNum, reordered);
               }
            }

            this.emitEvent({
               type: "shuffle_completed",
               sectionId,
               strategy: "move-solved-to-end",
               algorithm: "deterministic-reorder",
               questionCount: reordered.length,
            });
         }

         return result;
      } catch (error) {
         console.error(
            `❌ Move solved to end failed for section ${sectionId}:`,
            error
         );
         return {
            success: false,
            error: `Failed to move solved to end: ${error}`,
         };
      }
   }

   /**
    * Apply tag filters to a section
    */
   async applyTagFilter(
      sectionId: string,
      selectedTags: string[]
   ): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);

      if (!sectionCache || !sectionList) {
         return { success: false, error: "Section not initialized" };
      }

      console.log(`🏷️  Applying tag filter to ${sectionId}:`, selectedTags);

      // Store original state
      if (!sectionCache.isFiltered) {
         const currentPage = sectionList.getCurrentPage()?.pageNumber || 1;
         sectionCache.originalPosition = currentPage;
      }

      sectionCache.activeFilters = selectedTags;
      sectionCache.isFiltered = true;
      sectionCache.isShuffled = false; // Reset shuffle state for new filter

      try {
         const filteredEntries = await this.fetchFilteredQuestionEntries(
            sectionId,
            selectedTags
         );
         sectionCache.filteredQuestionEntries = filteredEntries;
         sectionCache.totalQuestions = filteredEntries.length;
         sectionCache.totalPages = Math.ceil(
            filteredEntries.length / this.config.questionsPerPage
         );

         // Clear cache and rebuild with filtered data
         sectionList.clear();
         this.emitEvent({ type: "cache_cleared", sectionId });

         // Start from page 1 of filtered results
         const result = await this.fetchAndCachePage(sectionId, 1, filteredEntries);

         if (result.success) {
            sectionList.setCurrentPage(1);
            sectionCache.currentNode = result.data;

            // Background prefetch page 2 of filtered results
            if (this.config.enablePrefetch && sectionCache.totalPages > 1) {
               this.prefetchPage(sectionId, 2, filteredEntries);
            }
         }

         return result;
      } catch (error) {
         console.error("❌ Failed to apply tag filter:", error);
         return { success: false, error: `Failed to apply filter: ${error}` };
      }
   }

   /**
    * Remove all filters and return to unfiltered state
    */
   async removeAllFilters(sectionId: string): Promise<CacheOperationResult> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const sectionList = this.sectionLists.get(sectionId);

      if (!sectionCache || !sectionList) {
         return { success: false, error: "Section not initialized" };
      }

      console.log(`🔄 Removing all filters from section: ${sectionId}`);

      // Restore original state
      sectionCache.isFiltered = false;
      sectionCache.activeFilters = [];
      sectionCache.isShuffled = false;
      sectionCache.totalQuestions = sectionCache.questionEntries.length;
      sectionCache.totalPages = Math.ceil(
         sectionCache.questionEntries.length / this.config.questionsPerPage
      );

      // Determine target page (try to restore original position)
      const targetPage = Math.min(
         sectionCache.originalPosition,
         sectionCache.totalPages
      );

      // Clear cache and rebuild with original data
      sectionList.clear();
      this.emitEvent({ type: "cache_cleared", sectionId });

      const result = await this.fetchAndCachePage(
         sectionId,
         targetPage,
         sectionCache.questionEntries
      );

      if (result.success) {
         sectionList.setCurrentPage(targetPage);
         sectionCache.currentNode = result.data;

         // Background prefetch adjacent pages
         if (this.config.enablePrefetch) {
            const prefetchTargets = sectionList.getPrefetchTargets("both");
            for (const pageNum of prefetchTargets) {
               this.prefetchPage(sectionId, pageNum, sectionCache.questionEntries);
            }
         }
      }

      return result;
   }

   /**
    * Get current page data for a section
    */
   getCurrentPageData(sectionId: string): HybridProblem[] | null {
      const sectionList = this.sectionLists.get(sectionId);
      if (!sectionList) return null;

      const currentNode = sectionList.getCurrentPage();
      return currentNode ? currentNode.questionData : null;
   }

   /**
    * Get cache statistics
    */
   getCacheStats(): CacheStats {
      // Update stats
      this.stats.hitRatio =
         this.stats.hits / (this.stats.hits + this.stats.misses) || 0;
      this.stats.totalCachedPages = Array.from(
         this.sectionLists.values()
      ).reduce((total, list) => total + list.getStats().size, 0);

      this.stats.estimatedMemoryUsage = Array.from(
         this.sectionLists.values()
      ).reduce((total, list) => total + list.getStats().memoryEstimate, 0);

      return { ...this.stats };
   }

   // Private helper methods

   private async fetchAndCachePage(
      sectionId: string,
      pageNumber: number,
      questionEntries?: QuestionIdEntry[]
   ): Promise<CacheOperationResult> {
      try {
         const sectionCache = this.globalCache.sections.get(sectionId);
         const sectionList = this.sectionLists.get(sectionId);

         if (!sectionCache || !sectionList) {
            return { success: false, error: "Section not initialized" };
         }

         // Use provided entries or fall back to section's current list
         const entries =
            questionEntries ||
            (sectionCache.isFiltered
               ? sectionCache.filteredQuestionEntries
               : sectionCache.questionEntries);

         // Calculate which entries (rows) to fetch for this page
         const startIndex = (pageNumber - 1) * this.config.questionsPerPage;
         const endIndex = startIndex + this.config.questionsPerPage;
         const pageEntries = entries.slice(startIndex, endIndex);

         // Extract flattened IDs for API call
         const pageQuestionIds =
            QuestionIdManager.extractStringIdsFromQuestionIdEntries(pageEntries);

         if (pageQuestionIds.length === 0) {
            return {
               success: false,
               error: "No questions found for this page",
            };
         }

         // Fetch question data from API
         console.log(
            `📡 Fetching page ${pageNumber} data for ${sectionId} (${pageQuestionIds.length} questions)`
         );
         console.log(
            `🔍 Question IDs for page ${pageNumber}:`,
            pageQuestionIds.slice(0, 5),
            pageQuestionIds.length > 5 ? "..." : ""
         );
         const questionData = await this.fetchQuestionDataByIds(
            pageQuestionIds,
            this.userId
         );
         console.log(
            `📊 Fetched ${questionData.length} questions for page ${pageNumber}`
         );

         // Add to cache
         const cacheNode = sectionList.addPage(pageNumber, questionData);
         this.emitEvent({ type: "page_cached", sectionId, pageNumber });

         return { success: true, data: cacheNode };
      } catch (error) {
         console.error(`❌ Failed to fetch page ${pageNumber}:`, error);
         return { success: false, error: `Failed to fetch page: ${error}` };
      }
   }

   private async prefetchPage(
      sectionId: string,
      pageNumber: number,
      questionEntries?: QuestionIdEntry[]
   ): Promise<void> {
      const sectionList = this.sectionLists.get(sectionId);
      if (!sectionList || sectionList.hasPage(pageNumber)) {
         return; // Already cached
      }

      console.log(`🚀 Prefetching page ${pageNumber} for ${sectionId}`);
      this.emitEvent({ type: "prefetch_started", sectionId, pageNumber });

      try {
         await this.fetchAndCachePage(sectionId, pageNumber, questionEntries);
         this.stats.prefetchCount++;
         this.emitEvent({ type: "prefetch_completed", sectionId, pageNumber });
      } catch (error) {
         console.warn(`⚠️  Prefetch failed for page ${pageNumber}:`, error);
      }
   }

   private async fetchQuestionDataByIds(
      questionIds: string[],
      userId: number = 1
   ): Promise<HybridProblem[]> {
      try {
         console.log(
            `🔍 fetchQuestionDataByIds called with:`,
            questionIds.slice(0, 5),
            questionIds.length > 5 ? "..." : ""
         );

         // Convert string IDs to numbers
         const numericIds = questionIds
            .map((id) => parseInt(id, 10))
            .filter((id) => !isNaN(id));

         if (numericIds.length === 0) {
            console.warn("⚠️ No valid numeric IDs found in:", questionIds);
            return [];
         }

         // For cache system, we need to fetch problems in the exact order specified by questionIds
         // while preserving both individual problems and problem sets with user attempt data

         const sectionIdParts = this.globalCache.currentSectionId.split("-");
         const examName = sectionIdParts[0];
         const sectionName = sectionIdParts[1];

         if (!examName || !sectionName) {
            console.error(
               `❌ Invalid section ID format: ${this.globalCache.currentSectionId}. Expected format: 'ExamName-SectionName'`
            );
            throw new Error(
               `Invalid section ID format: ${this.globalCache.currentSectionId}`
            );
         }

         // Use the API endpoint with specific question IDs to get the problems in the right format
         const apiResponse = await fetch(
            `/api/problems?userid=${userId}&examName=${examName}&sectionName=${sectionName}&questionIds=${numericIds.join(
               ","
            )}`
         );

         if (!apiResponse.ok) {
            throw new Error(
               `API request failed with status ${apiResponse.status}`
            );
         }

         const apiData = await apiResponse.json();
         let processedProblems = apiData.problemData || [];

         // The API should now handle problem sets correctly, but if not, log a warning
         if (
            processedProblems.length > 0 &&
            !("problems" in processedProblems[0]) &&
            !("isExpanded" in processedProblems[0])
         ) {
            console.warn(
               "⚠️ API returned individual questions instead of proper problem sets structure"
            );
            // For now, we'll use the individual questions as-is, but this should be fixed in the API
         }

         // ⚠️ CRITICAL FIX: The API returns filtered results but NOT in the requested order
         // We need to reorder the results to match the original questionIds order

         // First, transform the API data to match HybridProblem format
         const transformedProblems: HybridProblem[] = [];
         let absoluteIndex = 0;

         processedProblems.forEach((item: any) => {
            // Check if this is a Problem Set
            if ("problems" in item && "isExpanded" in item) {
               const problemSet = item;

               // Transform child problems with proper numbering and attempt data
               const transformedChildren = problemSet.problems.map(
                  (childProblem: any) => ({
                     problemid: String(childProblem.problemid),
                     title: childProblem.title,
                     difficulty: childProblem.difficulty || 0,
                     addedDate: childProblem.addedDate,
                     problemtags: [],
                     iscorrect: childProblem.iscorrect, // Preserve attempt data
                     absoluteIndex: absoluteIndex++,
                  })
               );

               // Return Problem Set with proper numbering and attempt data
               transformedProblems.push({
                  problemsSetId: problemSet.problemsSetId,
                  title: problemSet.title,
                  difficulty:
                     Math.round(
                        transformedChildren.reduce(
                           (acc: number, p: any) => acc + (p.difficulty || 0),
                           0
                        ) / transformedChildren.length
                     ) || 0,
                  addedDate:
                     transformedChildren[0]?.addedDate ||
                     new Date().toISOString(),
                  isExpanded: problemSet.isExpanded || false,
                  problems: transformedChildren,
                  absoluteIndex: absoluteIndex - transformedChildren.length, // Set to first child's index
               });
            } else {
               // This is an individual problem
               transformedProblems.push({
                  problemid: String(item.problemid),
                  title: item.title,
                  difficulty: item.difficulty || 0,
                  addedDate: item.addedDate,
                  problemtags: [],
                  iscorrect: item.iscorrect, // Preserve attempt data
                  absoluteIndex: absoluteIndex++,
               });
            }
         });

         // Now reorder the transformed problems to match the original questionIds order
         const results: HybridProblem[] = [];
         const problemMap = new Map<string, HybridProblem>();

         // Create a map of all problems and their child problems for fast lookup
         transformedProblems.forEach((problem) => {
            if ("problemsSetId" in problem && problem.problems) {
               // For problem sets, map each child problem ID
               problem.problems.forEach((child) => {
                  problemMap.set(child.problemid, problem);
               });
            } else if ("problemid" in problem) {
               // For individual problems
               problemMap.set(problem.problemid, problem);
            }
         });

         // Maintain the original questionIds order by looking up each ID
         const addedProblemSets = new Set<number>(); // Track added problem sets to avoid duplicates

         // Build final results array preserving requested order
         const addedRows = new Set<string>();

         questionIds.forEach((requestedId) => {
            const problem = problemMap.get(requestedId);
            if (problem) {
               const rowKey = "problemsSetId" in problem
                  ? `set_${(problem as ProblemsSet).problemsSetId}`
                  : (problem as Problem).problemid;

               if (!addedRows.has(rowKey)) {
                  results.push(problem);
                  addedRows.add(rowKey);
               }
            } else {
               console.warn(
                  `⚠️ Requested question ID ${requestedId} not found in API response`
               );
            }
         });

         console.log(
            `✅ Reordered ${results.length} problems to match requested order`
         );
         console.log(
            `🔍 Original order: [${questionIds.slice(0, 5).join(", ")}${questionIds.length > 5 ? "..." : ""
            }]`
         );
         console.log(
            `🔍 Result order: [${results
               .slice(0, 5)
               .map((p) =>
                  "problemsSetId" in p ? `Set:${p.problemsSetId}` : p.problemid
               )
               .join(", ")}${results.length > 5 ? "..." : ""}]`
         );

         return results;
      } catch (error) {
         console.error("❌ Error fetching question data by IDs:", error);
         return [];
      }
   }

   private async fetchFilteredQuestionEntries(
      sectionId: string,
      tags: string[]
   ): Promise<QuestionIdEntry[]> {
      // Make API call to get filtered question entries (rows)
      const response = await fetch("/api/problems/filtered-ids", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ sectionId, tags }),
      });

      if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.questionEntries || [];
   }

   private fisherYatesShuffle<T>(array: T[]): T[] {
      const shuffled = [...array];
      for (let i = shuffled.length - 1; i > 0; i--) {
         const j = Math.floor(Math.random() * (i + 1));
         [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
   }

   private updateNavigationState(
      pageNumber: number,
      direction: "next" | "previous" | "jump"
   ): void {
      this.navigationState = {
         previousPage: this.navigationState.currentPage,
         currentPage: pageNumber,
         direction,
         lastNavigationTime: Date.now(),
      };
   }

   private emitEvent(event: CacheEvent): void {
      this.eventListeners.forEach((listener) => {
         try {
            listener(event);
         } catch (error) {
            console.warn("Event listener error:", error);
         }
      });
   }

   /**
    * Add event listener for cache events
    */
   addEventListener(listener: (event: CacheEvent) => void): void {
      this.eventListeners.push(listener);
   }

   /**
    * Remove event listener
    */
   removeEventListener(listener: (event: CacheEvent) => void): void {
      const index = this.eventListeners.indexOf(listener);
      if (index > -1) {
         this.eventListeners.splice(index, 1);
      }
   }

   /**
    * Get the shuffle service instance
    */
   getShuffleService(): ShuffleService {
      return this.shuffleService;
   }

   /**
    * Get question ID manager for a section
    */
   getQuestionIdManager(sectionId: string): QuestionIdManager | undefined {
      return this.questionIdManagers.get(sectionId);
   }

   /**
    * Advanced shuffle with custom strategy
    */
   async shuffleWithStrategy(
      sectionId: string,
      strategy: ShuffleStrategy,
      _userPerformanceData?: Record<string, any>
   ): Promise<CacheOperationResult> {
      return this.shuffleQuestions(sectionId, strategy);
   }

   /**
    * Preview shuffle result without applying it
    */
   async previewShuffle(
      sectionId: string,
      strategy: ShuffleStrategy = "smart"
   ): Promise<{ success: boolean; previewIds?: string[]; error?: string }> {
      const sectionCache = this.globalCache.sections.get(sectionId);
      const questionIdManager = this.questionIdManagers.get(sectionId);

      if (!sectionCache || !questionIdManager) {
         return { success: false, error: "Section not initialized" };
      }

      try {
         const activeIds = questionIdManager.getActiveIds();
         const activeStringIds =
            QuestionIdManager.extractStringIdsFromQuestionIdEntries(activeIds);
         const preview = await this.shuffleService.previewShuffle(
            activeStringIds,
            strategy
         );

         return {
            success: true,
            previewIds: preview.previewIds,
         };
      } catch (error) {
         return {
            success: false,
            error: error instanceof Error ? error.message : "Preview failed",
         };
      }
   }

   /**
    * Clear all cached pages across all sections, but KEEP section metadata
    */
   clearPageCachesOnly(): void {
      this.sectionLists.forEach((list) => list.clear());
      this.emitEvent({ type: "cache_cleared", sectionId: "all" });
   }

   /**
    * Clear cache for a specific section
    */
   clearSectionCache(sectionId: string): void {
      console.log(`🧹 Clearing cache for section: ${sectionId}`);

      // Remove section from global cache
      this.globalCache.sections.delete(sectionId);

      // Remove section's doubly linked list
      this.sectionLists.delete(sectionId);

      // Remove section's question ID manager
      this.questionIdManagers.delete(sectionId);

      // Reset current section if it matches
      if (this.globalCache.currentSectionId === sectionId) {
         this.globalCache.currentSectionId = "";
      }

      this.emitEvent({ type: "section_cleared", sectionId });
   }

   /**
    * Clear all caches
    */
   clearAllCaches(): void {
      console.log("🧹 Clearing all caches");

      // Clear all sections
      this.globalCache.sections.clear();
      this.sectionLists.clear();
      this.questionIdManagers.clear();

      // Reset global cache
      this.globalCache.currentSectionId = "";
      this.globalCache.createdAt = Date.now();

      // Reset navigation state
      this.navigationState = {
         currentPage: 1,
         previousPage: 1,
         direction: "next",
         lastNavigationTime: Date.now(),
      };

      // Reset stats
      this.stats = {
         hits: 0,
         misses: 0,
         hitRatio: 0,
         totalCachedPages: 0,
         estimatedMemoryUsage: 0,
         prefetchCount: 0,
      };

      this.emitEvent({ type: "all_caches_cleared" });
   }

   /**
    * Get current cache status for debugging
    */
   getCacheStatus(): any {
      return {
         currentSectionId: this.globalCache.currentSectionId,
         activeSections: Array.from(this.globalCache.sections.keys()),
         totalSections: this.globalCache.sections.size,
         stats: this.stats,
      };
   }

   /**
    * Convert HybridProblem array to QuestionIdEntry array for QuestionIdManager
    */
   private convertHybridProblemsToQuestionIdEntries(
      hybridProblems: HybridProblem[]
   ) {
      console.log(
         "🔍 Converting HybridProblems to QuestionIdEntries:",
         hybridProblems.slice(0, 3)
      );

      return hybridProblems
         .map((item, index) => {
            console.log(`🔍 Processing item ${index}:`, {
               hasProblemsSetId: "problemsSetId" in item,
               hasProblemId: "problemid" in item,
               problemsSetId:
                  "problemsSetId" in item ? (item as any).problemsSetId : "N/A",
               problemid: "problemid" in item ? (item as any).problemid : "N/A",
               structure: Object.keys(item),
            });

            if ("problemsSetId" in item) {
               const problemSet = item as any;

               // Check if this is actually an individual problem misclassified as a ProblemsSet
               if (
                  problemSet.problemsSetId === null ||
                  problemSet.problemsSetId === undefined
               ) {
                  console.log(
                     `🔧 Converting misclassified ProblemsSet to individual Problem:`,
                     item
                  );
                  // This is actually an individual problem, convert it
                  if ("problemid" in item) {
                     return {
                        problemid: parseInt((item as any).problemid, 10),
                     };
                  } else {
                     console.warn(
                        `⚠️ Item has problemsSetId: null but no problemid:`,
                        item
                     );
                     // Skip this invalid item by returning null (we'll filter it out)
                     return null;
                  }
               }

               // This is a genuine ProblemsSet
               console.log(
                  `🔍 Processing genuine ProblemsSet at index ${index}:`,
                  item
               );

               if (
                  !problemSet.problems ||
                  !Array.isArray(problemSet.problems)
               ) {
                  console.warn(
                     `⚠️ ProblemsSet ${problemSet.problemsSetId} has invalid or missing problems array:`,
                     problemSet.problems
                  );
                  // If problems array is missing/invalid AND this is a genuine ProblemsSet (not null),
                  // return empty problems array. But if problemsSetId is null, treat as individual problem
                  if (
                     problemSet.problemsSetId === null ||
                     problemSet.problemsSetId === undefined
                  ) {
                     console.log(
                        `🔧 Converting ProblemsSet with null ID and no problems to individual Problem:`,
                        item
                     );
                     if ("problemid" in item) {
                        return {
                           problemid: parseInt((item as any).problemid, 10),
                        };
                     } else {
                        console.warn(
                           `⚠️ Item has problemsSetId: null, no problems array, and no problemid:`,
                           item
                        );
                        return null;
                     }
                  }
                  // Return a valid structure with empty problems array for genuine problem sets
                  return {
                     problemsSetId: problemSet.problemsSetId,
                     problems: [],
                  };
               }

               return {
                  problemsSetId: problemSet.problemsSetId,
                  problems: problemSet.problems.map((p: Problem) => ({
                     problemid: parseInt(p.problemid, 10),
                  })),
               };
            } else {
               // This is an individual Problem
               return {
                  problemid: parseInt(item.problemid, 10),
               };
            }
         })
         .filter((item) => item !== null); // Remove null entries
   }

   /**
    * Convert string IDs to QuestionIdEntry array for QuestionIdManager
    * Since we only have string IDs at initialization, we treat them all as individual problems
    */
   private convertStringIdsToQuestionIdEntries(stringIds: string[]) {
      return stringIds.map((id) => ({
         problemid: parseInt(id, 10),
      }));
   }
}
