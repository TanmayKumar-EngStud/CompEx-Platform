"use client";
import { useQuery } from "@tanstack/react-query";
import { useState, useEffect, useMemo } from "react";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import {
   useProblemsStore,
   type Problem,
   type ProblemsSet,
   type ProblemsResponse,
   type HybridProblem,
} from "@/shared/stores/problems/cache";
import { type QuestionState } from "@/shared/stores/problems/navigation";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";

// Simple questionList function to replace deprecated import
function useQuestionList() {
   const navigation = useNavigationStore();
   const cache = useQuestionCacheStore();

   return {
      questionIds: navigation.questionIds,
      start: navigation.start,
      setStart: navigation.setStart,
      setQuestionIds: navigation.setQuestionIds,
      getFromCache: cache.getFromCache,
      markQuestionAccessed: cache.markQuestionAccessed,
      prefetchQuestions: (currentIndex: number) =>
         cache.prefetchQuestions(currentIndex, navigation.questionIds),
   };
}

function sortProblems(
   filteredProblemData: HybridProblem[],
   categoryIndex: number,
   sortOrder: 1 | 0 | -1
): HybridProblem[] {
   if (sortOrder === 0 || filteredProblemData.length === 0)
      return filteredProblemData; // No sorting

   const categoryKey = Object.keys(filteredProblemData[0])[
      categoryIndex
   ] as keyof HybridProblem;

   return filteredProblemData.sort((a, b) => {
      const aValue = a[categoryKey];
      const bValue = b[categoryKey];

      // Handle undefined values
      if (aValue === undefined && bValue === undefined) return 0;
      if (aValue === undefined) return sortOrder === 1 ? 1 : -1;
      if (bValue === undefined) return sortOrder === 1 ? -1 : 1;

      if (sortOrder === 1) {
         // Ascending
         return aValue < bValue ? -1 : 1;
      } else {
         // Descending
         return aValue > bValue ? -1 : 1;
      }
   });
}
function isProblemSet(item: HybridProblem) {
   if ("isExpanded" in item) {
      return true;
   } else {
      return false;
   }
}
export const fetchProblems_and_ProblemsSet = async (
   userid: number,
   examName: string,
   sectionName: string,
   filters: { topics: string[], themes: string[], types: string[] }
): Promise<ProblemsResponse> => {
   const { topics, themes, types } = filters;

   try {
      // Build query parameters
      const paramsObj = {
         userid: userid.toString(),
         examName,
         sectionName,
         ...(topics.length > 0 && { topics: JSON.stringify(topics) }),
         ...(themes.length > 0 && { themes: JSON.stringify(themes) }),
         ...(types.length > 0 && { types: JSON.stringify(types) }),
      };

      const problemsParams = new URLSearchParams(paramsObj);

      // Fetch single unified response from /api/problems which now includes both problems and sets
      const response = await fetch(`/api/problems?${problemsParams.toString()}`);

      if (!response.ok) {
         throw new Error(`Failed to fetch data. Status: ${response.status}`);
      }
      const data = await response.json();

      // Assign absolute indices to the unified dataset
      const combinedData = data.problemData || [];
      let absoluteIndex = 0;

      const hybridDataWithIndices = combinedData.map((item: any) => {
         if (isProblemSet(item)) {
            const problemSet = item as ProblemsSet;
            const updatedProblems = (problemSet.problems || []).map((problem) => ({
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
         totalProblems: data.totalProblems || hybridDataWithIndices.length,
         metadata: data.pagination,
      };
   } catch (error: any) {
      console.error("Error in fetchProblems_and_ProblemsSet:", error);
      throw error;
   }
};

export const usePaginatedProblems = () => {
   const [filteredProblemData, setFilteredProblemData] =
      useState<HybridProblem[]>();
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
   const { problems_or_problemsset, isShuffled } = useProblemsStore();
   const { userId } = useAttemptsStore();
   const { setQuestionIds } = useQuestionList();
   const [previousData, setPreviousData] = useState<ProblemsResponse | null>(
      null
   );
   const {
      initializeSection,
      initializeSectionWithHybridData,
      initializeService,
   } = usePaginationCacheStore();

   // Memoize filter arrays for query key stability
   const filterArraysStr = JSON.stringify({
      topics: selectedTopics,
      themes: selectedThemes,
      types: selectedTypes,
   });

   // EFFECT 1: RESET state on section/exam change
   // This prevents Quants data from "leaking" into Verbal section during transitions
   useEffect(() => {
      console.log(`🧹 Resetting filteredProblemData for new section: ${examName}-${sectionName}`);
      setFilteredProblemData(undefined);
      setPreviousData(null);
   }, [examName, sectionName]);

   const { status, data, error } = useQuery({
      queryKey: [
         "problems",
         userId,
         examName,
         sectionName,
         filterArraysStr,
      ],
      queryFn: () =>
         fetchProblems_and_ProblemsSet(
            userId,
            examName,
            sectionName,
            { topics: selectedTopics, themes: selectedThemes, types: selectedTypes }
         ),
      staleTime: 5 * 60 * 1000, // 5 minutes - much longer to prevent excessive refetches
      refetchOnWindowFocus: false,
   });
   useEffect(() => {
      if (status === "success" && data) {
         // SAFETY CHECK: Ensure data matches the current section context
         // This prevents race conditions where stale data initializes the cache for the wrong section
         if (
            data.metadata &&
            (data.metadata.examName !== examName ||
               data.metadata.sectionName?.toLowerCase() !== sectionName?.toLowerCase())
         ) {
            console.warn(
               `⚠️ Mismatched data received: Requested ${examName}/${sectionName}, but received ${data.metadata.examName}/${data.metadata.sectionName}. Ignoring.`
            );
            return;
         }

         setPreviousData(data);

         // Use shuffled data ONLY IF it belongs to the correct section context
         // This prevents Quants shuffled data from appearing when switching to Verbal
         const sourceData =
            isShuffled &&
               problems_or_problemsset.length > 0 &&
               (data.metadata?.sectionName?.toLowerCase() === sectionName?.toLowerCase())
               ? problems_or_problemsset
               : data.problemData;

         const filteredData = sourceData.filter((problem: HybridProblem) =>
            problem.title.toLowerCase().includes(searchedText.toLowerCase())
         );

         setFilteredProblemData(filteredData);

         // Initialize pagination cache with section data
         if (filteredData.length > 0 && examName && sectionName) {
            const sectionId = `${examName}-${sectionName}`;

            // Extract all individual question IDs (including children of problem sets)
            const questionIds: string[] = [];
            filteredData.forEach((problem) => {
               if (isProblemSet(problem)) {
                  // For problem sets, add all child question IDs
                  const problemSet = problem as ProblemsSet;
                  problemSet.problems.forEach((childProblem) => {
                     questionIds.push(childProblem.problemid.toString());
                  });
               } else {
                  // For individual problems, add the problem ID
                  questionIds.push((problem as Problem).problemid.toString());
               }
            });

            // Initialize service and section - make it synchronous to avoid race conditions
            console.log(
               `🔧 Initializing pagination cache for section: ${sectionId} with ${filteredData.length} hybrid problems`,
               `\n📋 Exam: ${examName}, Section: ${sectionName}`,
               `\n🔢 Total individual question IDs: ${questionIds.length}`,
               `\n🔍 First few hybrid problems:`,
               filteredData.slice(0, 5)
            );

            initializeService();

            // Try to initialize with HybridProblem data first, fall back to string IDs if it fails
            initializeSectionWithHybridData(
               sectionId,
               filteredData,
               filteredData.length
            )
               .then((success) => {
                  if (success) {
                     console.log(
                        "✅ Pagination cache initialized successfully with HybridProblem data for section:",
                        sectionId
                     );
                  } else {
                     console.warn(
                        "⚠️ Failed to initialize with HybridProblem data, falling back to string IDs for section:",
                        sectionId
                     );
                     // Fallback to string-based initialization
                     return initializeSection(sectionId, questionIds, filteredData.length);
                  }
               })
               .catch((error) => {
                  console.error(
                     "❌ Error initializing with HybridProblem data, falling back to string IDs:",
                     error
                  );
                  // Fallback to string-based initialization
                  return initializeSection(sectionId, questionIds, filteredData.length);
               });
         }
      }
   }, [
      data,
      status,
      isShuffled,
      problems_or_problemsset,
      searchedText,
      examName,
      sectionName,
      pageSize,
      initializeService,
      initializeSection,
      initializeSectionWithHybridData,
   ]);

   // Memoize question IDs calculation to prevent unnecessary recalculations
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
         // Properly get the problemid from individual problems
         return parseInt((problem as Problem).problemid, 10);
      });
   }, [filteredProblemData]);

   useEffect(() => {
      // Only update questionIds if not shuffled, to avoid overriding shuffle order
      if (questionIdsArray.length > 0 && !isShuffled && isDataSectionMatched) {
         console.log(
            "DEBUG: Updating useQuestionList with ids:",
            questionIdsArray.slice(0, 5),
            "Length:", questionIdsArray.length
         );
         setQuestionIds(questionIdsArray);
      }
   }, [questionIdsArray, setQuestionIds, isShuffled]);

   //Sorting problems
   const sortedProblemData = useMemo(() => {
      if (!filteredProblemData?.length) return [];
      const result = [...filteredProblemData]; // Avoid in-place mutation
      sortProblems(result, categoryIndex, sortOrder);
      return result;
   }, [filteredProblemData, categoryIndex, sortOrder]);

   const a = (page - 1) * pageSize;
   const b = pageSize;

   // Apply pagination slicing
   const paginatedData = sortedProblemData?.slice(a, a + b) || [];

   // Verify that the data we are about to return actually matches the requested section
   // This is a last-line of defense against stale display
   const isDataSectionMatched = useMemo(() => {
      if (!filteredProblemData || filteredProblemData.length === 0) return true;

      // If we have previousData, check if its metadata matches
      if (previousData?.metadata) {
         return (
            previousData.metadata.examName === examName &&
            previousData.metadata.sectionName?.toLowerCase() === sectionName?.toLowerCase()
         );
      }
      return true;
   }, [filteredProblemData, previousData, examName, sectionName]);

   const finalData = (data && isDataSectionMatched)
      ? {
         problemData: paginatedData,
         totalProblems: sortedProblemData?.length || data.totalProblems,
      }
      : { problemData: [], totalProblems: 0 };

   return {
      status,
      error,
      data: finalData,
      previousData,
      fullData: sortedProblemData, // Add full dataset for shuffling
   };
};

const fetchQuestionDetails = async (
   questionIds: (number | { [key: string]: number[] })[],
   windowSize: number,
   start: number,
   getFromCache: (id: number) => QuestionState | null
): Promise<QuestionState[]> => {
   let getQuestionOfIds: number[] = [];
   const cachedQuestions: QuestionState[] = [];

   // region getQuestionOfIds ✅
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
            // First try to get from cache
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
               // First try to get from cache
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
   // endregion

   let fetchedQuestions: QuestionState[] = [];
   if (getQuestionOfIds.length > 0) {
      console.log(`🌐 Fetching ${getQuestionOfIds.length} questions from API:`, getQuestionOfIds);
      // Use new RESTful endpoint for multiple questions
      const response = await fetch(
         `/api/problems/${getQuestionOfIds.join(",")}`
      );
      const result = await response.json();
      fetchedQuestions = result.questions || result;
      console.log(`✅ Fetched ${fetchedQuestions.length} questions from API`);
   } else {
      console.log(`ℹ️ No new questions to fetch (all cached or window empty)`);
   }

   // Combine cached and fetched questions
   const allQuestions = [...cachedQuestions, ...fetchedQuestions];
   return allQuestions;
};

export const callQuestions = () => {
   const { page, pageSize, categoryIndex, sortOrder } = usePaginationStore();
   const navigation = useNavigationStore();
   const cache = useQuestionCacheStore();

   const { questionIds, start, getFromCache, prefetchQuestions } =
      useQuestionList();

   const windowSize = navigation.windowSize;

   const { status, data, error } = useQuery({
      queryKey: ["questions", questionIds, start, windowSize],
      queryFn: () => {
         //start value comes here
         return fetchQuestionDetails(
            questionIds,
            windowSize,
            start,
            getFromCache
         );
      },
      staleTime: 10 * 60 * 1000, // 10 minutes - questions rarely change
      refetchOnWindowFocus: false,
      enabled: start >= 0,
   });

   useEffect(() => {
      if (status === "success" && data) {
         const sortedData: QuestionState[] = questionIds
            .map((id) =>
               data.find((question) => {
                  if (typeof id === "number") {
                     return question.problemid === id;
                  } else {
                     return Object.values(id)[0].includes(question.problemid);
                  }
               })
            )
            .filter((question) => question !== undefined) as QuestionState[];
         navigation.pasteQuestionDataList(sortedData);
      }
   }, [status, data, questionIds, navigation]);

   // Separate effect for prefetching to avoid dependency issues
   useEffect(() => {
      if (status === "success" && start >= 0 && questionIds.length > 0) {
         // Use setTimeout to defer prefetching and avoid blocking main thread
         const timeoutId = setTimeout(() => {
            prefetchQuestions(start).catch((error) =>
               console.warn("Prefetch failed:", error)
            );
         }, 500); // Increase delay to allow main UI to settle

         return () => clearTimeout(timeoutId);
      }
   }, [start, status, questionIds.length, prefetchQuestions]);

   return {
      status,
      data: navigation.questionDataList,
      error,
   };
};

// Interface for client-side attempt submission
interface AttemptSubmissionData {
   userId: number;
   Attempt: {
      problemId: number;
      option: string[];
      timetaken: string | null;
      partialcorrectnessscore: number | null;
   }[];
}

export const submitUserAttemptClient = async (data: AttemptSubmissionData) => {
   // Transform data format to match API expectations
   const transformedData = {
      userID: data.userId, // API expects userID, not userId
      Attempt:
         data.Attempt?.map((attempt) => ({
            questionID: attempt.problemId, // API expects questionID, not problemId
            option: attempt.option,
            timetaken: attempt.timetaken,
            partialcorrectnessscore: attempt.partialcorrectnessscore,
         })) || [],
   };

   const response = await fetch("/api/submit-answers", {
      method: "POST",
      headers: {
         "Content-Type": "application/json",
      },
      body: JSON.stringify(transformedData),
   });

   return response.json();
};
