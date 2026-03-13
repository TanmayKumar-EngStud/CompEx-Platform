import React from "react";
import { LazyQuestionTable } from "@/shared/components/feedback/lazy/LazyQuestionTable";
import SmartDataLoader from "@/shared/components/feedback/SmartDataLoader";
import { QuestionTableSkeleton } from "@/shared/components/feedback/SkeletonLoaders";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useUIStore } from "@/shared/stores/problems/ui-state";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { PaginationControls } from "@/features/question-solving/components/PaginationControls";
import { ShuffleLoadingState } from "@/features/question-solving/components/LoadingStates";
import { HybridProblem } from "@/shared/stores/problems/cache";
import {
   ProblemWithAttempt,
   ProblemSetWithAttempts,
} from "@/features/question-solving/services/question-pagination-service";
import uiStrings from "../config/ui-strings.json";
import { Switch } from "@/shared/components/ui/switch";
import { ArrowDownToLine } from "lucide-react";

interface ProblemsTableSectionProps {
   problemData: {
      status: string;
      error: unknown;
      data: any;
      previousData: any;
      fullData?: any;
   };
   showDifficulty: boolean;
   openQuestion: () => void;
   isShuffling?: boolean;
}

/**
 * Helper function to safely convert date to ISO string
 */
function formatDateToISOString(date: Date | string | null | undefined): string {
   if (!date) {
      return new Date().toISOString();
   }

   if (typeof date === "string") {
      return date; // Already a string
   }

   if (date instanceof Date) {
      return date.toISOString();
   }

   // Try to parse if it's some other format
   try {
      return new Date(date).toISOString();
   } catch (error) {
      console.warn("Unable to parse date:", date, error);
      return new Date().toISOString();
   }
}

/**
 * Recalculate absoluteIndex for cache data based on current page and shuffled order
 */
function recalculateAbsoluteIndices(
   cacheData: HybridProblem[],
   currentPage: number,
   questionsPerPage: number = 10
): HybridProblem[] {
   const pageStartIndex = (currentPage - 1) * questionsPerPage;
   let absoluteIndex = pageStartIndex;

   return cacheData.map((item): HybridProblem => {
      if ('problems' in item && item.problems) {
         // This is a Problem Set - recalculate indices for children
         const updatedProblems = item.problems.map((childProblem) => ({
            ...childProblem,
            absoluteIndex: absoluteIndex++,
         }));

         return {
            ...item,
            problems: updatedProblems,
            absoluteIndex: pageStartIndex + (absoluteIndex - pageStartIndex - updatedProblems.length), // Set to first child's index
         };
      } else {
         // This is an individual problem
         return {
            ...item,
            absoluteIndex: absoluteIndex++,
         };
      }
   });
}

/**
 * Transform API data to match UI expectations
 * Converts ProblemWithAttempt | ProblemSetWithAttempts to HybridProblem[]
 */
function transformApiDataToHybridProblems(
   apiData: (ProblemWithAttempt | ProblemSetWithAttempts)[]
): HybridProblem[] {
   let absoluteIndex = 0;

   return apiData.map((item, index): HybridProblem => {
      // Check if this is a Problem Set
      if ("problems" in item && "isExpanded" in item) {
         const problemSet = item as ProblemSetWithAttempts;

         // Transform child problems with proper numbering
         const transformedProblems = problemSet.problems.map(
            (childProblem) => ({
               problemid: String(childProblem.problemid),
               title: childProblem.title,
               difficulty: childProblem.difficulty || 0,
               addedDate: formatDateToISOString(childProblem.addedDate),
               problemtags: childProblem.problemtags || [],
               iscorrect: childProblem.iscorrect,
               absoluteIndex: absoluteIndex++,
            })
         );

         // Return Problem Set with proper numbering
         return {
            problemsSetId: problemSet.problemsSetId,
            title: problemSet.title,
            difficulty:
               transformedProblems.length > 0
                  ? Math.round(
                     transformedProblems.reduce(
                        (acc, p) => acc + (p.difficulty || 0),
                        0
                     ) / transformedProblems.length
                  )
                  : 0,
            addedDate:
               transformedProblems[0]?.addedDate || new Date().toISOString(),
            isExpanded: problemSet.isExpanded,
            problems: transformedProblems,
            absoluteIndex: absoluteIndex - transformedProblems.length, // Set to first child's index
         };
      } else {
         // This is an individual problem
         const problem = item as ProblemWithAttempt;

         return {
            problemid: String(problem.problemid),
            title: problem.title,
            difficulty: problem.difficulty || 0,
            addedDate: formatDateToISOString(problem.addedDate),
            problemtags: problem.problemtags || [],
            iscorrect: problem.iscorrect,
            absoluteIndex: absoluteIndex++,
         };
      }
   });
}

export const ProblemsTableSection = React.memo(function ProblemsTableSection({
   problemData,
   showDifficulty,
   openQuestion,
   isShuffling = false,
}: ProblemsTableSectionProps) {
   const { examName, sectionName, pageSize, setPageSize, setPage } = usePaginationStore();
   const { displaySolvedQuestions, setDisplaySolvedQuestions } = useUIStore();
   const {
      currentPage,
      totalPages,
      totalQuestions,
      currentPageData,
      currentSectionId, // Temporarily unused while prioritizing API data
      isLoading,
      isShuffling: cacheIsShuffling,
      isMovingSolved,
      navigateToPage,
      moveSolvedToEnd,
      updateConfig, // Extract updateConfig
      // jumpToPage, // Temporarily unused
      lastError,
   } = usePaginationCacheStore();

   // Use cache state if available, otherwise fall back to problem data
   const effectiveIsShuffling = isShuffling || cacheIsShuffling;

   const handleMoveSolvedToEnd = React.useCallback(async () => {
      const success = await moveSolvedToEnd();
      if (!success) {
         console.warn("Move solved to end failed — cache may not be initialized");
      }
   }, [moveSolvedToEnd]);

   const handlePageChange = React.useCallback(async (page: number) => {
      const success = await navigateToPage(page);
      if (!success) {
         console.error("Failed to navigate to page:", page);
      }
   }, [navigateToPage]);

   const handlePageSizeChange = React.useCallback(async (limit: number) => {
      console.log(`📏 Changing page size to: ${limit}`);
      setPageSize(limit);
      setPage(1); // Reset to page 1 to prevent being on a "ghost" page

      // IMPORTANT: Sync with cache store
      await updateConfig({ questionsPerPage: limit });
   }, [setPageSize, setPage, updateConfig]);

   // Stable dataKey that doesn't change on every question navigation
   const stableDataKey = React.useMemo(() => {
      return `problems-${sectionName}-${currentPage}-${totalQuestions}`;
   }, [sectionName, currentPage, totalQuestions]);

   // Removed handleJumpToPage as it's currently unused
   // const handleJumpToPage = async (page: number) => {
   //    const success = await jumpToPage(page);
   //    if (!success) {
   //       console.error('Failed to jump to page:', page);
   //    }
   // };

   // Show shuffle loading state if shuffling

   return (
      <div>
         <div className="flex items-center justify-between mb-4 mt-3">
            <h1 className="text-2xl tracking-tight">
               {uiStrings.headers.problems}
            </h1>
            <div
               data-tour="display-solved-switch"
               className="flex items-center gap-3 bg-muted/30 px-3 py-1.5 rounded-full border border-border/50 backdrop-blur-sm"
            >
               <label
                  htmlFor="display-solved-switch"
                  className="text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer select-none"
               >
                  {uiStrings.labels.displaySolvedQuestions}
               </label>
               <Switch
                  id="display-solved-switch"
                  checked={displaySolvedQuestions}
                  onCheckedChange={setDisplaySolvedQuestions}
                  className="scale-90"
               />
               <div className="w-px h-4 bg-border/50" />
               <button
                  onClick={handleMoveSolvedToEnd}
                  disabled={isMovingSolved}
                  className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
                  title="Move solved questions to the last pages"
               >
                  <ArrowDownToLine size={14} className={isMovingSolved ? "animate-bounce" : ""} />
                  {isMovingSolved ? "Moving..." : "Move solved to end"}
               </button>
            </div>
         </div>

         {/* Error display */}
         {lastError && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
               <p className="text-destructive text-sm">{lastError}</p>
            </div>
         )}

         <SmartDataLoader
            status={problemData.status as any}
            data={problemData}
            error={problemData.error}
            loader={<QuestionTableSkeleton />}
            loadingMessage={uiStrings.messages.loadingProblems}
            className="min-h-[400px]"
            suppressLoadingWhenDataExists={true}
            dataKey={stableDataKey}
         >
            {(data) => {
               // Verify that the cache actually belongs to the current section
               const expectedSectionId = `${examName}-${sectionName}`;
               const isCacheSectionMatched = currentSectionId === expectedSectionId;

               const shouldUseCacheData =
                  currentPageData &&
                  currentPageData.length > 0 &&
                  isCacheSectionMatched;

               let effectiveData;
               if (shouldUseCacheData) {
                  console.log(`✅ Using CACHE data with ${currentPageData.length} items on page ${currentPage} for section ${currentSectionId}`);
                  // Cache data is already in HybridProblem format with proper iscorrect values
                  // But we need to recalculate absoluteIndex based on current page and shuffled order
                  const correctedPageData = recalculateAbsoluteIndices(currentPageData, currentPage, pageSize);
                  effectiveData = {
                     ...data,
                     data: {
                        problemData: correctedPageData,
                        totalProblems: totalQuestions,
                     },
                  };
               } else {
                  // Transform API data from ProblemWithAttempt|ProblemSetWithAttempts to HybridProblem[]
                  const apiProblems = data?.data?.problemData || [];
                  const transformedProblems =
                     transformApiDataToHybridProblems(apiProblems);
                  console.log(
                     "🌐 Using API data with",
                     transformedProblems.length,
                     "items (fallback - cache not available)"
                  );

                  effectiveData = {
                     ...data,
                     data: {
                        problemData: transformedProblems,
                        totalProblems:
                           data?.data?.totalProblems ||
                           transformedProblems.length,
                     },
                  };
               }


               return (
                  <div className="space-y-4 relative" data-tour="problems-table">
                     {/* Shuffle Loading Overlay */}
                     {effectiveIsShuffling && (
                        <div className="absolute inset-x-0 -inset-y-2 z-20 flex items-center justify-center bg-background/60 backdrop-blur-[1px] rounded-md transition-all duration-300">
                           <ShuffleLoadingState />
                        </div>
                     )}
                     <LazyQuestionTable
                        queryData={effectiveData}
                        openQuestion={openQuestion}
                        displaySolvedQuestions={displaySolvedQuestions}
                        showDifficulty={showDifficulty}
                        isShuffling={effectiveIsShuffling}
                     />

                     {/* Enhanced Pagination Controls */}
                     {totalPages > 1 && (
                        <PaginationControls
                           currentPage={currentPage}
                           totalPages={totalPages}
                           totalQuestions={totalQuestions}
                           questionsPerPage={pageSize}
                           onPageChange={handlePageChange}
                           onPageSizeChange={handlePageSizeChange}
                           isLoading={isLoading}
                           loadingType="navigation"
                           showPageSizeSelector={true} // Enable page size selector
                           showQuickJump={totalPages > 5}
                           className="mt-6"
                        />
                     )}
                  </div>
               );
            }}
         </SmartDataLoader>
      </div>
   );
});
