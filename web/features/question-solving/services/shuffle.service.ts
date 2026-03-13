/**
 * Shuffle Service
 *
 * High-level service for managing question shuffling operations.
 * Integrates with the pagination cache service and provides advanced
 * shuffling strategies based on user preferences and performance data.
 */

import { QuestionIdManager } from "../lib/question-id-manager";
import {
   smartShuffle,
   fisherYatesShuffle,
   performanceWeightedShuffle,
   categoryBalancedShuffle,
   difficultyProgressiveShuffle,
   spacedRepetitionShuffle,
   createWeightedQuestions,
   validateShuffleResult,
   type ShuffleOptions,
   type WeightedQuestion,
   type ShuffleResult,
} from "../lib/shuffle-methods";

export type ShuffleStrategy =
   | "random"
   | "performance-weighted"
   | "category-balanced"
   | "difficulty-progressive"
   | "spaced-repetition"
   | "smart";

export interface ShuffleServiceConfig {
   defaultStrategy: ShuffleStrategy;
   enablePerformanceWeights: boolean;
   enableCategoryBalancing: boolean;
   enableDifficultyProgression: boolean;
   enableSpacedRepetition: boolean;
   maxConsecutiveCategory: number;
   preserveFilters: boolean;
   logShuffleEvents: boolean;
}

export interface ShuffleContext {
   sectionId: string;
   currentPage: number;
   isFiltered: boolean;
   activeFilters: string[];
   totalQuestions: number;
   questionsPerPage: number;
}

export interface ShuffleEventData {
   strategy: ShuffleStrategy;
   sectionId: string;
   questionCount: number;
   preservedPage: boolean;
   duration: number;
   metadata?: Record<string, any>;
}

export class ShuffleService {
   private config: ShuffleServiceConfig;
   private eventListeners: ((event: ShuffleEventData) => void)[] = [];

   constructor(config: Partial<ShuffleServiceConfig> = {}) {
      this.config = {
         defaultStrategy: "random",
         enablePerformanceWeights: false,
         enableCategoryBalancing: false,
         enableDifficultyProgression: false,
         enableSpacedRepetition: false,
         maxConsecutiveCategory: 3,
         preserveFilters: true,
         logShuffleEvents: true,
         ...config,
      };

      // if (this.config.logShuffleEvents) {
      //   console.log('🔀 ShuffleService initialized with config:', this.config);
      // }
   }

   /**
    * Shuffle questions using the specified strategy
    */
   async shuffleQuestions(
      questionIds: string[],
      strategy: ShuffleStrategy = this.config.defaultStrategy,
      context?: ShuffleContext,
      userPerformanceData?: Record<string, Partial<WeightedQuestion>>
   ): Promise<ShuffleResult> {
      const startTime = Date.now();

      if (this.config.logShuffleEvents) {
         console.log(
            `🔀 Shuffling ${questionIds.length} questions using ${strategy} strategy`
         );
      }

      try {
         // Convert to weighted questions if needed
         const weightedQuestions = createWeightedQuestions(
            questionIds,
            userPerformanceData
         );

         // Build shuffle options based on config and context
         const options: ShuffleOptions = {
            usePerformanceWeights:
               this.config.enablePerformanceWeights && strategy !== "random",
            maxConsecutiveCategory: this.config.maxConsecutiveCategory,
            maintainDifficultyProgression:
               this.config.enableDifficultyProgression && strategy !== "random",
            preserveGroups: context?.isFiltered && this.config.preserveFilters,
         };

         let result: ShuffleResult;

         // Apply the chosen shuffle strategy
         switch (strategy) {
            case "random":
               result = {
                  shuffledIds: fisherYatesShuffle(questionIds),
                  algorithm: "fisher-yates",
                  preservedOrder: false,
               };
               break;

            case "performance-weighted":
               if (!this.config.enablePerformanceWeights) {
                  console.warn(
                     "⚠️  Performance weights disabled, falling back to random shuffle"
                  );
                  result = {
                     shuffledIds: fisherYatesShuffle(questionIds),
                     algorithm: "fisher-yates-fallback",
                     preservedOrder: false,
                  };
               } else {
                  result = performanceWeightedShuffle(
                     weightedQuestions,
                     options
                  );
               }
               break;

            case "category-balanced":
               if (!this.config.enableCategoryBalancing) {
                  console.warn(
                     "⚠️  Category balancing disabled, falling back to random shuffle"
                  );
                  result = {
                     shuffledIds: fisherYatesShuffle(questionIds),
                     algorithm: "fisher-yates-fallback",
                     preservedOrder: false,
                  };
               } else {
                  result = categoryBalancedShuffle(weightedQuestions, options);
               }
               break;

            case "difficulty-progressive":
               if (!this.config.enableDifficultyProgression) {
                  console.warn(
                     "⚠️  Difficulty progression disabled, falling back to random shuffle"
                  );
                  result = {
                     shuffledIds: fisherYatesShuffle(questionIds),
                     algorithm: "fisher-yates-fallback",
                     preservedOrder: false,
                  };
               } else {
                  result = difficultyProgressiveShuffle(
                     weightedQuestions,
                     options
                  );
               }
               break;

            case "spaced-repetition":
               if (!this.config.enableSpacedRepetition) {
                  console.warn(
                     "⚠️  Spaced repetition disabled, falling back to random shuffle"
                  );
                  result = {
                     shuffledIds: fisherYatesShuffle(questionIds),
                     algorithm: "fisher-yates-fallback",
                     preservedOrder: false,
                  };
               } else {
                  result = spacedRepetitionShuffle(weightedQuestions, options);
               }
               break;

            case "smart":
               result = smartShuffle(weightedQuestions, options);
               break;

            default:
               console.warn(
                  `⚠️  Unknown shuffle strategy: ${strategy}, falling back to random`
               );
               result = {
                  shuffledIds: fisherYatesShuffle(questionIds),
                  algorithm: "fisher-yates-fallback",
                  preservedOrder: false,
               };
         }

         // Validate the shuffle result
         if (!validateShuffleResult(questionIds, result)) {
            throw new Error("Shuffle validation failed");
         }

         const duration = Date.now() - startTime;

         // Emit shuffle event
         const eventData: ShuffleEventData = {
            strategy,
            sectionId: context?.sectionId || "unknown",
            questionCount: questionIds.length,
            preservedPage: result.preservedOrder,
            duration,
            metadata: result.metadata,
         };

         this.emitShuffleEvent(eventData);

         if (this.config.logShuffleEvents) {
            console.log(
               `✅ Shuffle completed in ${duration}ms using ${result.algorithm} algorithm`
            );
         }

         return result;
      } catch (error) {
         console.error("❌ Shuffle failed:", error);

         // Fallback to basic random shuffle
         const fallbackResult: ShuffleResult = {
            shuffledIds: fisherYatesShuffle(questionIds),
            algorithm: "fisher-yates-emergency-fallback",
            preservedOrder: false,
         };

         const duration = Date.now() - startTime;
         this.emitShuffleEvent({
            strategy: "random",
            sectionId: context?.sectionId || "unknown",
            questionCount: questionIds.length,
            preservedPage: false,
            duration,
            metadata: {
               error: error instanceof Error ? error.message : "Unknown error",
            },
         });

         return fallbackResult;
      }
   }

   /**
    * Shuffle with QuestionIdManager integration
    */
   async shuffleWithManager(
      manager: QuestionIdManager,
      strategy: ShuffleStrategy = this.config.defaultStrategy,
      context?: ShuffleContext,
      userPerformanceData?: Record<string, Partial<WeightedQuestion>>
   ): Promise<{ result: ShuffleResult; newActiveIds: string[] }> {
      // Convert QuestionIdEntry to string for shuffle algorithms
      const activeIds = manager.getActiveIds();
      const activeStringIds =
         QuestionIdManager.extractStringIdsFromQuestionIdEntries(activeIds);
      const result = await this.shuffleQuestions(
         activeStringIds,
         strategy,
         context,
         userPerformanceData
      );

      // Convert shuffled string IDs back to QuestionIdEntry format for manager
      const shuffledQuestionIdEntries =
         this.convertShuffledIdsToQuestionIdEntries(
            result.shuffledIds,
            activeIds
         );

      // Apply the advanced shuffle result to the manager directly
      // This preserves the sophisticated shuffling algorithms instead of overriding with basic Fisher-Yates
      manager.setShuffledActiveIds(shuffledQuestionIdEntries);

      console.log(
         `✅ Applied ${result.algorithm} shuffle result to QuestionIdManager`
      );

      return { result, newActiveIds: result.shuffledIds };
   }

   /**
    * Convert shuffled string IDs back to QuestionIdEntry format while preserving order
    */
   private convertShuffledIdsToQuestionIdEntries(
      shuffledStringIds: string[],
      originalEntries: any[]
   ) {
      // Create a map from problemid to its original QuestionIdEntry
      const idToEntryMap = new Map();

      originalEntries.forEach((entry) => {
         if ("problemid" in entry) {
            // Individual problem
            idToEntryMap.set(String(entry.problemid), entry);
         } else if ("problemsSetId" in entry && entry.problems) {
            // Problem set - map each child problem to the parent set
            entry.problems.forEach((child: any) => {
               idToEntryMap.set(String(child.problemid), entry);
            });
         }
      });

      // Reconstruct in shuffled order, avoiding duplicates for problem sets
      const result: any[] = [];
      const addedSets = new Set<number>();

      shuffledStringIds.forEach((stringId) => {
         const entry = idToEntryMap.get(stringId);
         if (entry) {
            if ("problemsSetId" in entry) {
               // Only add problem set once, even if multiple children are in the shuffle
               if (!addedSets.has(entry.problemsSetId)) {
                  result.push(entry);
                  addedSets.add(entry.problemsSetId);
               }
            } else {
               // Individual problem
               result.push(entry);
            }
         }
      });

      return result;
   }

   /**
    * Get recommended shuffle strategy based on available data
    */
   getRecommendedStrategy(
      questionIds: string[],
      userPerformanceData?: Record<string, Partial<WeightedQuestion>>,
      context?: ShuffleContext
   ): ShuffleStrategy {
      // If smart shuffling is enabled, always recommend smart
      if (
         this.config.enablePerformanceWeights ||
         this.config.enableCategoryBalancing ||
         this.config.enableDifficultyProgression ||
         this.config.enableSpacedRepetition
      ) {
         return "smart";
      }

      // Check if performance data is available
      if (userPerformanceData && Object.keys(userPerformanceData).length > 0) {
         const hasAccuracyData = Object.values(userPerformanceData).some(
            (data) => data.userAccuracy !== undefined
         );
         const hasTimingData = Object.values(userPerformanceData).some(
            (data) => data.lastAttempted !== undefined
         );

         if (hasAccuracyData && this.config.enablePerformanceWeights) {
            return "performance-weighted";
         }

         if (hasTimingData && this.config.enableSpacedRepetition) {
            return "spaced-repetition";
         }
      }

      // Check if category data is available
      if (
         userPerformanceData &&
         Object.values(userPerformanceData).some(
            (data) => data.category !== undefined
         ) &&
         this.config.enableCategoryBalancing
      ) {
         return "category-balanced";
      }

      // Check if difficulty data is available
      if (
         userPerformanceData &&
         Object.values(userPerformanceData).some(
            (data) => data.difficulty !== undefined
         ) &&
         this.config.enableDifficultyProgression
      ) {
         return "difficulty-progressive";
      }

      // Default to random shuffle
      return "random";
   }

   /**
    * Preview shuffle without applying it
    */
   async previewShuffle(
      questionIds: string[],
      strategy: ShuffleStrategy,
      userPerformanceData?: Record<string, Partial<WeightedQuestion>>
   ): Promise<{
      previewIds: string[];
      strategy: ShuffleStrategy;
      algorithm: string;
      metadata?: Record<string, any>;
   }> {
      const result = await this.shuffleQuestions(
         questionIds,
         strategy,
         undefined,
         userPerformanceData
      );

      return {
         previewIds: result.shuffledIds,
         strategy,
         algorithm: result.algorithm,
         metadata: result.metadata,
      };
   }

   /**
    * Calculate shuffle similarity between two orderings
    */
   calculateShuffleSimilarity(
      originalIds: string[],
      shuffledIds: string[]
   ): number {
      if (originalIds.length !== shuffledIds.length) return 0;

      let matchingPositions = 0;
      for (let i = 0; i < originalIds.length; i++) {
         if (originalIds[i] === shuffledIds[i]) {
            matchingPositions++;
         }
      }

      return matchingPositions / originalIds.length;
   }

   /**
    * Get shuffle statistics for analytics
    */
   getShuffleStats(
      originalIds: string[],
      shuffledIds: string[],
      strategy: ShuffleStrategy
   ): {
      similarity: number;
      strategy: ShuffleStrategy;
      totalQuestions: number;
      firstQuestionChanged: boolean;
      lastQuestionChanged: boolean;
      avgPositionChange: number;
   } {
      const similarity = this.calculateShuffleSimilarity(
         originalIds,
         shuffledIds
      );

      let totalPositionChange = 0;
      for (let i = 0; i < originalIds.length; i++) {
         const originalPos = i;
         const newPos = shuffledIds.indexOf(originalIds[i]);
         totalPositionChange += Math.abs(newPos - originalPos);
      }

      return {
         similarity,
         strategy,
         totalQuestions: originalIds.length,
         firstQuestionChanged: originalIds[0] !== shuffledIds[0],
         lastQuestionChanged:
            originalIds[originalIds.length - 1] !==
            shuffledIds[shuffledIds.length - 1],
         avgPositionChange: totalPositionChange / originalIds.length,
      };
   }

   /**
    * Update service configuration
    */
   updateConfig(newConfig: Partial<ShuffleServiceConfig>): void {
      this.config = { ...this.config, ...newConfig };

      if (this.config.logShuffleEvents) {
         console.log("🔧 ShuffleService config updated:", newConfig);
      }
   }

   /**
    * Get current configuration
    */
   getConfig(): Readonly<ShuffleServiceConfig> {
      return { ...this.config };
   }

   /**
    * Add event listener for shuffle events
    */
   addShuffleEventListener(listener: (event: ShuffleEventData) => void): void {
      this.eventListeners.push(listener);
   }

   /**
    * Remove event listener
    */
   removeShuffleEventListener(
      listener: (event: ShuffleEventData) => void
   ): void {
      const index = this.eventListeners.indexOf(listener);
      if (index > -1) {
         this.eventListeners.splice(index, 1);
      }
   }

   /**
    * Emit shuffle event to all listeners
    */
   private emitShuffleEvent(event: ShuffleEventData): void {
      for (const listener of this.eventListeners) {
         try {
            listener(event);
         } catch (error) {
            console.warn("Shuffle event listener error:", error);
         }
      }
   }

   /**
    * Reset service state
    */
   reset(): void {
      this.eventListeners = [];

      if (this.config.logShuffleEvents) {
         console.log("🔄 ShuffleService reset");
      }
   }
}
