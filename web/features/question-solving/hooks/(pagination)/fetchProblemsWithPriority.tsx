/**
 * Enhanced fetchProblems with priority-based caching
 *
 * This replaces the existing fetchProblems implementation with intelligent
 * priority-based data loading that improves performance by loading critical
 * data first and background-loading related data.
 */

"use client";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useProblemsStore } from "@/shared/stores/problems/cache";
import {
   ProblemsSet,
   ProblemsResponse,
   QuestionState,
   usePaginationStore,
   HybridProblem,
} from "./problemDefinition";
import {
   CachePriority,
   usePriorityCache,
} from "@/shared/lib/cache/priority-cache";

// Re-export existing utility functions
function sortProblems(
   filteredProblemData: HybridProblem[],
   categoryIndex: number,
   sortOrder: 1 | 0 | -1
): HybridProblem[] {
   if (sortOrder === 0 || filteredProblemData.length === 0)
      return filteredProblemData;

   const categoryKey = Object.keys(filteredProblemData[0])[
      categoryIndex
   ] as keyof HybridProblem;

   return filteredProblemData.sort((a, b) => {
      const aValue = a[categoryKey];
      const bValue = b[categoryKey];

      if (aValue === undefined && bValue === undefined) return 0;
      if (aValue === undefined) return sortOrder === 1 ? 1 : -1;
      if (bValue === undefined) return sortOrder === 1 ? -1 : 1;

      if (sortOrder === 1) {
         return aValue < bValue ? -1 : 1;
      } else {
         return aValue > bValue ? -1 : 1;
      }
   });
}

function isProblemSet(item: HybridProblem) {
   return "isExpanded" in item;
}

// Enhanced fetch function with priority handling
const fetchProblems_and_ProblemsSet_Priority = async (
   userid: number,
   examName: string,
   sectionName: string,
   Tags: string[],
   priority: CachePriority = CachePriority.IMMEDIATE
): Promise<ProblemsResponse> => {
   const tags = Tags.length > 0 ? Tags : null;

   try {
      // For immediate priority, fetch directly
      if (priority === CachePriority.IMMEDIATE) {
         const [response_A, response_B] = await Promise.all([
            fetch("/api/problems/getProblems", {
               method: "POST",
               headers: { "Content-Type": "application/json" },
               body: JSON.stringify({ userid, examName, sectionName, tags }),
            }),
            fetch("/api/problems/getProblemsSets", {
               method: "POST",
               headers: { "Content-Type": "application/json" },
               body: JSON.stringify({ userid, examName, sectionName, tags }),
            }),
         ]);

         if (!response_A.ok || !response_B.ok) {
            throw new Error(
               `Failed to fetch data. Problems Status: ${response_A.status}, ProblemSets Status: ${response_B.status}`
            );
         }

         const data_A = await response_A.json();
         const data_B = await response_B.json();

         return processProblemsData(data_A, data_B);
      }

      // For lower priority, use single request to reduce server load
      const response = await fetch("/api/problems/getProblems", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ userid, examName, sectionName, tags }),
      });

      if (!response.ok) {
         throw new Error(`Failed to fetch problems: ${response.status}`);
      }

      const data = await response.json();
      return {
         problemData: data.problemData || [],
         totalProblems: data.totalProblems || 0,
      };
   } catch (error: any) {
      console.error("Error in fetchProblems_and_ProblemsSet_Priority:", error);
      throw error;
   }
};

// Process and combine problems data
function processProblemsData(data_A: any, data_B: any): ProblemsResponse {
   let parentProblems: HybridProblem[] = [];

   if (data_B.problemSetWithProblems) {
      parentProblems = data_B.problemSetWithProblems.map(
         (set: ProblemsSet) => ({
            problemsSetId: set.problemsSetId,
            title: set.title,
            difficulty:
               Math.round(
                  set.problems.reduce(
                     (acc, problem) => acc + problem.difficulty,
                     0
                  ) / set.problems.length
               ) || 0,
            addedDate: set.problems[0].addedDate,
            isParent: true,
            problems: set.problems.map((problem) => ({
               ...problem,
               iscorrect: problem.iscorrect,
            })),
            isExpanded: false,
         })
      );
   }

   const combinedData = [...data_A.problemData, ...parentProblems];
   let absoluteIndex = 0;

   const hybridDataWithIndices = combinedData.map((item) => {
      if (isProblemSet(item)) {
         const problemSet = item as ProblemsSet;
         const updatedProblems = problemSet.problems.map((problem) => ({
            ...problem,
            absoluteIndex: absoluteIndex++,
         }));
         return {
            ...problemSet,
            problems: updatedProblems,
            absoluteIndex: absoluteIndex - updatedProblems.length,
         };
      } else {
         return {
            ...item,
            absoluteIndex: absoluteIndex++,
         };
      }
   });

   return {
      problemData: hybridDataWithIndices,
      totalProblems: data_A.totalProblems + parentProblems.length,
   };
}

// Loading state interface
interface LoadingState {
   immediate: boolean;
   high: boolean;
   background: boolean;
   progress: {
      completed: number;
      total: number;
      currentTask: string;
   };
}

// Enhanced hook with priority caching
export const usePaginatedProblemsWithPriority = () => {
   const [filteredProblemData, setFilteredProblemData] =
      useState<HybridProblem[]>();
   const [loadingState, setLoadingState] = useState<LoadingState>({
      immediate: false,
      high: false,
      background: false,
      progress: { completed: 0, total: 0, currentTask: "" },
   });

   const {
      page,
      pageSize,
      examName,
      sectionName,
      selectedTopics,
      selectedThemes,
      selectedTypes,
      searchedText,
      categoryIndex,
      sortOrder,
   } = usePaginationStore();

   // Combine all selected categorical tags
   const allSelectedTags = useMemo(() => [
      ...selectedTopics,
      ...selectedThemes,
      ...selectedTypes
   ].sort(), [selectedTopics, selectedThemes, selectedTypes]);
   const { problems_or_problemsset, isShuffled } = useProblemsStore();

   const { userId } = useAttemptsStore();
   const { setQuestionIds } = useNavigationStore();
   const [previousData, setPreviousData] = useState<ProblemsResponse | null>(
      null
   );
   const queryClient = useQueryClient();
   const priorityCache = usePriorityCache();

   // Primary query for immediate data (current exam/section)
   const { status, data, error } = useQuery({
      queryKey: [
         "problems-priority",
         userId,
         examName,
         sectionName,
         allSelectedTags,
      ],
      queryFn: () =>
         fetchProblems_and_ProblemsSet_Priority(
            userId,
            examName,
            sectionName,
            allSelectedTags,
            CachePriority.IMMEDIATE
         ),
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
   });

   // Initialize priority caching when exam/section changes
   useEffect(() => {
      if (!examName || !sectionName) return;

      const initializePriorityCache = async () => {
         setLoadingState((prev) => ({
            ...prev,
            immediate: true,
            background: true,
         }));

         try {
            // Execute priority caching plan
            await priorityCache.executePriorityPlan(
               examName,
               sectionName,
               { topics: selectedTopics, themes: selectedThemes, types: selectedTypes },
               (progress) => {
                  setLoadingState((prev) => ({
                     ...prev,
                     progress,
                  }));
               }
            );

            console.log(
               "✅ Priority caching completed for",
               examName,
               sectionName
            );
         } catch (error) {
            console.error("❌ Priority caching failed:", error);
         } finally {
            setLoadingState((prev) => ({
               ...prev,
               immediate: false,
               high: false,
               background: false,
            }));
         }
      };

      // Debounce cache initialization to avoid excessive calls
      const timeoutId = setTimeout(initializePriorityCache, 300);
      return () => clearTimeout(timeoutId);
   }, [examName, sectionName, allSelectedTags, priorityCache]);

   // Handle data updates
   useEffect(() => {
      if (status === "success" && data) {
         setPreviousData(data);

         const sourceData =
            isShuffled && problems_or_problemsset.length > 0
               ? problems_or_problemsset
               : data.problemData;

         setFilteredProblemData(
            sourceData.filter((problem: HybridProblem) =>
               problem.title.toLowerCase().includes(searchedText.toLowerCase())
            )
         );
      }
   }, [data, status, isShuffled, problems_or_problemsset, searchedText]);

   // Memoize question IDs calculation
   const questionIdsArray = useMemo(() => {
      if (!filteredProblemData) return [];

      return filteredProblemData.map((problem) => {
         if (isProblemSet(problem)) {
            let temp = [];
            for (let i = 0; i < (problem as ProblemsSet).problems.length; i++) {
               temp.push(
                  parseInt((problem as ProblemsSet).problems[i].problemid)
               );
            }
            let res: { [key: string]: number[] } = {};
            res[(problem as ProblemsSet).problemsSetId] = temp;
            return res;
         }
         return parseInt(Object.values(problem)[0], 10);
      });
   }, [filteredProblemData]);

   useEffect(() => {
      if (questionIdsArray.length > 0) {
         setQuestionIds(questionIdsArray);
      }
   }, [questionIdsArray, setQuestionIds]);

   // Sort problems
   if (filteredProblemData?.length) {
      sortProblems(filteredProblemData, categoryIndex, sortOrder);
   }

   // Pagination
   const a = (page - 1) * pageSize;
   const b = pageSize;
   const finalData = data
      ? {
         problemData: filteredProblemData?.slice(a, a + b) || [],
         totalProblems: filteredProblemData?.length || data.totalProblems,
      }
      : { problemData: [], totalProblems: 0 };

   // Prefetch related data when current data is loaded
   const prefetchRelatedData = useCallback(async () => {
      if (status !== "success" || !data) return;

      // Get related sections to prefetch
      const relatedSections =
         examName === "GRE"
            ? sectionName === "quants"
               ? ["verbal"]
               : ["quants"]
            : examName === "GMAT"
               ? sectionName === "quants"
                  ? ["verbal"]
                  : ["quants"]
               : [];

      // Prefetch related section data
      relatedSections.forEach((section) => {
         queryClient.prefetchQuery({
            queryKey: ["problems-priority", userId, examName, section, []],
            queryFn: () =>
               fetchProblems_and_ProblemsSet_Priority(
                  userId,
                  examName,
                  section,
                  [],
                  CachePriority.HIGH
               ),
            staleTime: 10 * 60 * 1000,
         });
      });
   }, [status, data, examName, sectionName, userId, queryClient]);

   useEffect(() => {
      prefetchRelatedData();
   }, [prefetchRelatedData]);

   return {
      status,
      error,
      data: finalData,
      previousData,
      fullData: filteredProblemData,
      loadingState,
      cacheStats: priorityCache.getCacheStats(),
   };
};

// Enhanced questions hook with priority awareness
export const callQuestionsWithPriority = () => {
   const {
      questionIds,
      start,
      windowSize,
      questionDataList,
      pasteQuestionDataList,
   } = useNavigationStore();
   const { getFromCache } = useQuestionCacheStore();

   // Enhanced fetchQuestionDetails with priority caching
   const fetchQuestionDetailsWithPriority = async (
      questionIds: (number | { [key: string]: number[] })[],
      windowSize: number,
      start: number,
      getFromCache: (id: number) => QuestionState | null
   ): Promise<QuestionState[]> => {
      let getQuestionOfIds: number[] = [];
      const cachedQuestions: QuestionState[] = [];

      // Collect question IDs with cache checking
      let questionsCovered = 0;
      for (
         let i = 0;
         getQuestionOfIds.length < windowSize && i < questionIds.length;
         i++
      ) {
         let id: number;
         if (typeof questionIds[i] === "number") {
            id = questionIds[i] as number;
            if (questionsCovered >= start) {
               const cached = getFromCache(id);
               if (cached) {
                  cachedQuestions.push(cached);
               } else {
                  getQuestionOfIds.push(id);
               }
            }
            questionsCovered++;
         } else {
            for (
               let j = 0;
               getQuestionOfIds.length + cachedQuestions.length < windowSize &&
               j < Object.values(questionIds[i])[0].length;
               j++
            ) {
               id = Object.values(questionIds[i])[0][j];
               if (questionsCovered >= start) {
                  const cached = getFromCache(id);
                  if (cached) {
                     cachedQuestions.push(cached);
                  } else {
                     getQuestionOfIds.push(id);
                  }
               }
               questionsCovered++;
            }
         }
      }

      let fetchedQuestions: QuestionState[] = [];
      if (getQuestionOfIds.length > 0) {
         const response = await fetch("/api/problems/getQuestions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ questionId: getQuestionOfIds }),
         });

         if (!response.ok) {
            throw new Error(`Failed to fetch questions: ${response.status}`);
         }

         fetchedQuestions = await response.json();
      }

      return [...cachedQuestions, ...fetchedQuestions];
   };

   const { status, data, error } = useQuery({
      queryKey: ["questions-priority", questionIds, start, windowSize],
      queryFn: () => {
         return fetchQuestionDetailsWithPriority(
            questionIds,
            windowSize,
            start,
            getFromCache
         );
      },
      staleTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
      enabled: start >= 0,
   });

   useEffect(() => {
      if (status === "success" && data) {
         const sortedData: QuestionState[] = questionIds
            .map((id: number | { [key: string]: number[] }) =>
               data.find((question: QuestionState) => {
                  if (typeof id === "number") {
                     return question.problemid === id;
                  } else {
                     return (Object.values(id)[0] as number[]).includes(question.problemid);
                  }
               })
            )
            .filter((question: QuestionState | undefined) => question !== undefined) as QuestionState[];
         pasteQuestionDataList(sortedData);
      }
   }, [status, data, questionIds, pasteQuestionDataList]);

   // Enhanced prefetching with priority awareness
   useEffect(() => {
      if (status === "success" && start >= 0 && questionIds.length > 0) {
         const timeoutId = setTimeout(() => {
            const cache = useQuestionCacheStore.getState();
            const navigation = useNavigationStore.getState();
            cache
               .prefetchQuestions(start, navigation.questionIds)
               .catch((error) =>
                  console.warn("Priority prefetch failed:", error)
               );
         }, 300); // Reduced delay for better responsiveness

         return () => clearTimeout(timeoutId);
      }
   }, [start, status]);

   return {
      status,
      data: questionDataList,
      error,
   };
};

// Legacy exports for backward compatibility
export { usePaginatedProblemsWithPriority as usePaginatedProblems };
export { callQuestionsWithPriority as callQuestions };

// Interface for client-side attempt submission (unchanged)
interface AttemptSubmissionData {
   userId: number;
   Attempt: {
      problemId: number;
      option: string[];
      timetaken: string | string | null;
      partialcorrectnessscore: number | null;
   }[];
}

export const submitUserAttemptClient = async (data: AttemptSubmissionData) => {
   const transformedData = {
      userID: data.userId,
      Attempt:
         data.Attempt?.map((attempt) => ({
            questionID: attempt.problemId,
            option: attempt.option,
            timetaken: attempt.timetaken,
            partialcorrectnessscore: attempt.partialcorrectnessscore,
         })) || [],
   };

   const response = await fetch("/api/problems/returnAttempt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(transformedData),
   });

   return response.json();
};
