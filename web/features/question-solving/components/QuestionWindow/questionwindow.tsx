import React, {
   useEffect,
   useState,
   useCallback,
   useRef,
   useMemo,
} from "react";
import { QuestionFloatingWindowProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { callQuestions } from "@/features/question-solving/hooks/(pagination)/fetchProblems";

// DEBUG: Log what we imported (moved to component to avoid SSR issues)
import QuestionDisplay from "./QuestionDisplay/questionDisplay";
import {
   questionResult,
   useResultData,
} from "@/features/user-analytics/hooks/resultWindowDefinitions";
import Loading from "@/shared/components/feedback/loading";
import { useTimerStore } from "@/features/user-analytics/hooks/timerDefinition";
import Timer from "@/features/user-analytics/components/timer/timer";
import { Bookmark, X } from "lucide-react";
import QuestionTags from "@/features/question-solving/components/QuestionTags";
import { useStreak } from "@/shared/contexts/StreakContext";

const QuestionAttempt: React.FC<QuestionFloatingWindowProps> = ({
   onClose,
   onFinish,
   showTimer = true,
   hideLabels = false,
}) => {
   const { status, data: question } = callQuestions();
   const [questionData, setQuestionData] = useState(question?.[0]);
   useEffect(() => {
      if (question && question.length > 0) {
         console.log("🔍 QUESTION DATA SET DEBUG:", {
            newQuestionId: question[0].problemid,
            previousQuestionId: questionData?.problemid,
         });
         setQuestionData(question[0]);
      } else {
         console.log("⚠️ QUESTION DATA EMPTY OR NULL:", { question, status });
      }
   }, [question, status]);
   // console.log(questionData.problemoptions);
   const { start, questionIds, setStart } = useNavigationStore();
   const { masterQuestionIds } = usePaginationCacheStore();

   const { getFromCache, markQuestionAccessed } = useQuestionCacheStore();
   const {
      userId,
      Attempt,
      addAttempt,
      resetAttempt,
      toggleFlag,
      isFlagged,
      bookmarksEnabled,
      questionTagsEnabled,
   } = useAttemptsStore();
   const {
      switchQuestion,
      recordOptionSelectedTime,
      clearRecordedTime,
      getElapsedTime,
      currentQuestionId,
   } = useTimerStore();
   const { incrementStreakForToday, shouldIncrementStreak } = useStreak();

   const [selectedOption, setSelectedOption] = useState<string[]>([]);
   const [isLongOptions, setIsLongOptions] = useState(false);
   const [localAttempts, setLocalAttempts] = useState<Map<number, string[]>>(
      new Map()
   );

   // Debug effect to track localAttempts changes
   useEffect(() => {
      console.log("DEBUG: localAttempts changed:", localAttempts);
   }, [localAttempts]);
   const { setResultData } = useResultData();

   // Use ref to avoid dependency issues with getFromCache
   const getCacheRef = useRef(getFromCache);
   getCacheRef.current = getFromCache;

   const flattenQuestionIds = useCallback(() => {
      // Always use masterQuestionIds as the single source of truth for consistent navigation
      // This ensures the same order is maintained between question-table and questionwindow
      const sourceToUse =
         masterQuestionIds.length > 0 ? masterQuestionIds : questionIds;
      let ids: number[] = [];
      sourceToUse.forEach((id) => {
         if (typeof id === "number") {
            ids.push(id);
         } else {
            // For parent-child questions, add all child question IDs
            Object.values(id)[0].forEach((i) => {
               ids.push(i);
            });
         }
      });
      return ids;
   }, [masterQuestionIds, questionIds]);

   // Optimize question loading with memoization and reduced re-renders
   useEffect(() => {
      const flattenedIds = flattenQuestionIds();

      // Use navigation store as single source of truth
      // The start index directly corresponds to the position in the flattened IDs
      const targetQuestionId = flattenedIds[start];

      console.log("🔍 QUESTION WINDOW NAVIGATION DEBUG:", {
         start: start,
         targetQuestionId: targetQuestionId,
         currentQuestionId: questionData?.problemid,
         flattenedIdsLength: flattenedIds.length,
         first10FlattenedIds: flattenedIds.slice(0, 10),
         masterQuestionIdsLength: masterQuestionIds.length,
         questionIdsLength: questionIds.length,
         usingMasterIds: masterQuestionIds.length > 0,
      });

      if (targetQuestionId && targetQuestionId !== questionData?.problemid) {
         // Handle timer switching
         switchQuestion(currentQuestionId, targetQuestionId);

         // First try to get from cache for instant loading
         const cachedQuestion = getCacheRef.current(targetQuestionId);

         if (cachedQuestion) {
            // Use cached data immediately for faster UI response
            // console.log(
            //    `✅ Serving question ${targetQuestionId} from cache (instant load)`
            // );
            markQuestionAccessed(targetQuestionId); // Mark as accessed for LRU tracking
            setQuestionData(cachedQuestion);
            setIsLongOptions(
               Object.entries(cachedQuestion.problemoptions).some(
                  ([, { optiontext }]) => optiontext.length > 50
               )
            );
         } else if (question.length) {
            // Fallback to fetched data if not in cache
            const newQuestion = question.find(
               (q) => q.problemid === targetQuestionId
            );
            if (newQuestion) {
               console.log(
                  `🔄 Serving question ${targetQuestionId} from fetch (network load)`
               );
               markQuestionAccessed(targetQuestionId); // Mark as accessed for LRU tracking
               setQuestionData(newQuestion);
               setIsLongOptions(
                  Object.entries(newQuestion.problemoptions).some(
                     ([, { optiontext }]) => optiontext.length > 50
                  )
               );
            }
         }
      }
   }, [
      start,
      question,
      switchQuestion,
      currentQuestionId,
      questionData?.problemid,
      flattenQuestionIds,
   ]);

   // Separate effect to handle loading selected options for the current question
   useEffect(() => {
      if (questionData?.problemid) {
         const localAttempt = localAttempts.get(questionData.problemid);
         const existingAttempt = Attempt?.find(
            (attempt) => attempt.problemId === questionData.problemid
         );
         const selectedOptions = localAttempt || existingAttempt?.option || [];

         // Only update if the selection is different
         if (
            JSON.stringify(selectedOptions) !== JSON.stringify(selectedOption)
         ) {
            setSelectedOption(selectedOptions);
         }
      }
   }, [questionData?.problemid, localAttempts, Attempt, selectedOption]);
   const size = 11; // Configurable size for better UI

   const handleOptionClick = useCallback(
      (option: string | string[]) => {
         console.log("DEBUG: handleOptionClick - option:", option);
         console.log(
            "DEBUG: handleOptionClick - questionData.problemid:",
            questionData.problemid
         );

         const newOption = Array.isArray(option) ? option : [option];
         setSelectedOption(newOption);

         // Store in local attempts instead of immediately adding to store
         setLocalAttempts((prev) => {
            const updated = new Map(prev);

            // If the option is empty (deselected), remove from local attempts
            if (
               newOption.length === 0 ||
               (newOption.length === 1 && newOption[0] === "")
            ) {
               updated.delete(questionData.problemid);
            } else {
               updated.set(questionData.problemid, newOption);
            }

            console.log(
               "DEBUG: handleOptionClick - updated localAttempts:",
               updated
            );
            return updated;
         });

         recordOptionSelectedTime(questionData.problemid);
      },
      [questionData, recordOptionSelectedTime]
   );

   const handleClear = useCallback(() => {
      setSelectedOption([]);

      // Clear from local attempts
      setLocalAttempts((prev) => {
         const updated = new Map(prev);
         updated.delete(questionData.problemid);
         return updated;
      });

      // Also remove from store attempts if it exists
      const updatedAttempts = Attempt?.filter(
         (attempt) => attempt.problemId !== questionData.problemid
      );
      resetAttempt();
      if (updatedAttempts?.length) {
         updatedAttempts.forEach((attempt) => addAttempt(attempt));
      }

      // Clear the recorded time from timer but keep timer running
      clearRecordedTime(questionData.problemid);
   }, [questionData, Attempt, resetAttempt, addAttempt, clearRecordedTime]);

   const handleClearAll = useCallback(() => {
      // Clear current selection
      setSelectedOption([]);

      // Clear all local attempts
      setLocalAttempts(new Map());

      // Clear all store attempts
      resetAttempt();

      // Clear all recorded times for all questions
      const flattenedIds = flattenQuestionIds();
      flattenedIds.forEach((questionId: number) => {
         clearRecordedTime(questionId);
      });
   }, [resetAttempt, clearRecordedTime, flattenQuestionIds]);
   const handlePageChange = useCallback(
      (id: number) => {
         // Save current selection to local attempts before navigating
         // Save current selection to local attempts logic removed to prevent race conditions
         // handleOptionClick already handles saving to localAttempts immediately

         // Use navigation store as single source of truth
         const flattenedIds = flattenQuestionIds();
         const newIndex = flattenedIds.findIndex((q: number) => q === id);

         if (newIndex !== -1) {
            setStart(newIndex);
         }
      },
      [setStart, flattenQuestionIds, questionData, selectedOption]
   );

   const handleKeyNavigation = useCallback(
      (direction: "next" | "prev") => {
         // Save current selection to local attempts before navigating
         // Save logic removed to prevent race conditions

         // Use navigation store as single source of truth
         const currentQuestionList = flattenQuestionIds();
         const currentIndex = currentQuestionList.findIndex(
            (id: number) => id === questionData?.problemid
         );

         if (currentIndex === -1) return;

         let newIndex: number;
         if (direction === "next") {
            newIndex =
               currentIndex < currentQuestionList.length - 1
                  ? currentIndex + 1
                  : 0;
         } else {
            newIndex =
               currentIndex > 0
                  ? currentIndex - 1
                  : currentQuestionList.length - 1;
         }

         const newQuestionId = currentQuestionList[newIndex];
         handlePageChange(newQuestionId);
      },
      [
         questionData?.problemid,
         selectedOption,
         handlePageChange,
         flattenQuestionIds,
      ]
   );

   const handleSubmit = useCallback(
      (callbackfn: (localAttempts?: Map<number, string[]>) => void) => {
         console.log(
            "DEBUG: handleSubmit - questionData:",
            questionData?.problemid
         );
         console.log("DEBUG: handleSubmit - selectedOption:", selectedOption);
         console.log(
            "DEBUG: handleSubmit - current localAttempts:",
            localAttempts
         );

         // Create final attempts including current selection and all previous selections
         let finalLocalAttempts = new Map(localAttempts);

         // Always add current selection if there is one
         if (questionData && selectedOption.length > 0) {
            console.log(
               "DEBUG: handleSubmit - Adding current selection to finalLocalAttempts"
            );
            finalLocalAttempts.set(questionData.problemid, selectedOption);
         }

         // Also check if localAttempts is empty but we have a current selection
         if (
            finalLocalAttempts.size === 0 &&
            questionData &&
            selectedOption.length > 0
         ) {
            console.log(
               "DEBUG: handleSubmit - localAttempts was empty, creating new Map with current selection"
            );
            finalLocalAttempts = new Map();
            finalLocalAttempts.set(questionData.problemid, selectedOption);
         }

         console.log(
            "DEBUG: handleSubmit - finalLocalAttempts:",
            finalLocalAttempts
         );
         console.log(
            "DEBUG: handleSubmit - finalLocalAttempts size:",
            finalLocalAttempts.size
         );

         // Update the state for consistency
         setLocalAttempts(finalLocalAttempts);

         // Pass localAttempts to callback for result window logic
         callbackfn(finalLocalAttempts);
      },
      [questionData, selectedOption, localAttempts]
   );
   // Memoize transform options to avoid recalculating on every render
   const transformedOptions = useMemo(() => {
      if (!questionData?.problemoptions) return {};

      return questionData.problemoptions.reduce((acc, option, index) => {
         if (questionData.type.toLowerCase().includes("tc")) {
            acc[index.toString()] = {
               optiontext: option.optiontext,
               group: option.group,
            };
         } else {
            acc[index.toString()] = {
               optiontext: option.optiontext,
               group: option.group,
            };
         }
         return acc;
      }, {} as { [key: string]: { optiontext: string; group?: string } });
   }, [questionData?.problemoptions, questionData?.type]);

   // Use the original format for pagination component (it does its own flattening)
   const paginationQuestionIds = useMemo(() => {
      const result =
         masterQuestionIds.length > 0 ? masterQuestionIds : questionIds;
      console.log("🔍 PAGINATION QUESTION IDS DEBUG:", {
         resultLength: result.length,
         first3Items: result
            .slice(0, 3)
            .map((id) =>
               typeof id === "number" ? id : `Set:${Object.keys(id)[0]}`
            ),
         currentQuestionId: questionData?.problemid,
         usingMasterIds: masterQuestionIds.length > 0,
      });
      return result;
   }, [masterQuestionIds, questionIds, questionData?.problemid]);

   // Add keyboard event listener
   useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
         // Only handle arrow keys when no input elements are focused
         const activeElement = document.activeElement as HTMLElement;
         if (
            activeElement?.tagName === "INPUT" ||
            activeElement?.tagName === "TEXTAREA" ||
            activeElement?.contentEditable === "true"
         ) {
            return;
         }

         switch (event.key) {
            case "ArrowLeft":
               event.preventDefault();
               event.stopPropagation();
               handleKeyNavigation("prev");
               break;
            case "ArrowRight":
               event.preventDefault();
               event.stopPropagation();
               handleKeyNavigation("next");
               break;
            case "Escape":
               event.preventDefault();
               onClose();
               break;
         }
      };

      // Use capture phase so this fires BEFORE Radix RadioGroup's roving focus handler
      document.addEventListener("keydown", handleKeyDown, true);
      return () => document.removeEventListener("keydown", handleKeyDown, true);
   }, [
      handleKeyNavigation,
      handleClearAll,
      onClose,
      localAttempts,
      Attempt,
      handleSubmit,
   ]);

   const { questionTags, parentTags } = React.useMemo(() => {
      // Deduplicate tags by name, ensuring we trim whitespace
      const tagSet = new Set<string>();
      (questionData as any)?.problemtags?.forEach((pt: any) => {
         const name = pt.tags?.name;
         if (name && typeof name === "string" && name.trim().length > 0) {
            tagSet.add(name.trim());
         }
      });

      const pTags = (questionData as any)?.parentTags || [];
      const parentTagSet = new Set<string>();
      pTags.forEach((name: string) => {
         if (name && typeof name === "string" && name.trim().length > 0) {
            parentTagSet.add(name.trim());
         }
      });

      return {
         questionTags: Array.from(tagSet),
         parentTags: Array.from(parentTagSet),
      };
   }, [questionData]);

   // Memoize header content separately for better performance
   const headerContent = React.useMemo(() => {

      return (
         <div className="bg-background px-6 py-4 border-b border-border/50 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-4 flex-1 min-w-0">
               <button
                  onClick={onClose}
                  className="p-1.5 rounded-full hover:bg-muted transition-colors text-muted-foreground/60 hover:text-foreground flex-shrink-0"
                  title="Close without saving"
               >
                  <X size={20} />
               </button>

               <div className="h-4 w-px bg-border/60 mx-1 flex-shrink-0" />

               <div className="flex flex-col min-w-0">
                  <span className="text-[10px] font-bold text-primary/40 uppercase tracking-[0.2em] leading-none mb-1">
                     Question Reference
                  </span>
                  <div className="flex items-center gap-3">
                     {questionData && (
                        <h2
                           className="text-sm font-semibold text-foreground/80 truncate"
                           title={questionData.title}
                        >
                           {questionData.title}
                        </h2>
                     )}
                  </div>
               </div>
            </div>

            <div className="flex items-center gap-6">
               <div className="flex items-center gap-4">
                  {questionData && showTimer && <Timer questionId={questionData.problemid} />}

                  {questionData && bookmarksEnabled && (
                     <button
                        onClick={() => toggleFlag(questionData.problemid)}
                        className={`p-2 rounded-lg transition-all duration-200 ${isFlagged(questionData.problemid)
                           ? "bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400"
                           : "text-muted-foreground/40 hover:text-foreground hover:bg-muted"
                           }`}
                        title={isFlagged(questionData.problemid) ? "Remove bookmark" : "Bookmark question"}
                     >
                        <Bookmark
                           size={18}
                           fill={isFlagged(questionData.problemid) ? "currentColor" : "none"}
                        />
                     </button>
                  )}
               </div>

               <div className="h-6 w-px bg-border/50" />

               <button
                  className="bg-primary text-primary-foreground px-5 py-2 rounded-full text-sm font-semibold hover:bg-primary/90 transition-all active:scale-95 shadow-sm shadow-primary/20"
                  onClick={() => {
                     handleSubmit(onFinish);
                  }}
               >
                  Finish Session
               </button>
            </div>
         </div>
      );
   }, [
      questionData?.problemid,
      questionData?.title,
      bookmarksEnabled,
      questionTagsEnabled,
      isFlagged,
      toggleFlag,
      Attempt,
      localAttempts,
      handleSubmit,
      onClose,
      onFinish,
   ]);

   return (
      <div data-tour="question-window" className="fixed inset-0 flex items-center justify-center bg-black/40 backdrop-blur-[2px] z-50">
         <div className="relative bg-background shadow-2xl rounded-2xl w-11/12 max-w-5xl h-5/6 select-none overflow-hidden border border-border/60 flex flex-col">
            {headerContent}
            <div className="flex-1 overflow-hidden p-6 pt-1 pb-1 flex flex-col">
               {questionData !== undefined ? (
                  <QuestionDisplay
                     isLoading={status === "pending"}
                     type={questionData.type}
                     title={questionData.title}
                     text={questionData.text}
                     options_type={questionData.options_type}
                     options={transformedOptions}
                     selectedOption={selectedOption}
                     handleOptionClick={handleOptionClick}
                     isLongOptions={isLongOptions}
                     handleClear={handleClear}
                     handleClearAll={handleClearAll}
                     handlePageChange={handlePageChange}
                     questionIds={paginationQuestionIds}
                     questionId={questionData.problemid}
                     size={size}
                     showPagination={true}
                     metadata={questionData.metadata}
                     localAttempts={localAttempts}
                     tags={questionTags}
                     parentTags={parentTags}
                     showTitle={false}
                  />
               ) : (
                  <div className="flex items-center justify-center h-full">
                     <Loading size="lg" message="Loading first question..." />
                  </div>
               )}
            </div>
         </div>
      </div>
   );
};

export default QuestionAttempt;
