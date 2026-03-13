/**
 * Enhanced Question Window with Priority Caching
 *
 * This is an enhanced version of the existing question window that integrates
 * with the priority caching system for better performance.
 */

import React, { useEffect, useState, useCallback, useRef } from "react";
import { QuestionFloatingWindowProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useNavigationStore } from "@/shared/stores/problems/navigation";

// Use priority-enhanced hooks
import { callQuestionsWithPriority } from "@/features/question-solving/hooks/(pagination)/fetchProblemsWithPriority";
import { usePriorityCacheContext } from "@/shared/components/providers/priority-cache-provider";
import { PriorityCacheProgressCompact } from "@/shared/components/feedback/PriorityCacheProgress";

import QuestionDisplay from "./QuestionDisplay/questionDisplay";
import {
   questionResult,
   useResultData,
} from "@/features/user-analytics/hooks/resultWindowDefinitions";
import Loading from "@/shared/components/feedback/loading";
import { useTimerStore } from "@/features/user-analytics/hooks/timerDefinition";
import Timer from "@/features/user-analytics/components/timer/timer";
import { Bookmark, Database } from "lucide-react";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import QuestionTags from "@/features/question-solving/components/QuestionTags";

const QuestionAttemptWithPriority: React.FC<QuestionFloatingWindowProps> = ({
   onClose,
   showTimer = true,
}) => {
   // Use priority-enhanced question fetching
   const { status, data: question } = callQuestionsWithPriority();
   const [questionData, setQuestionData] = useState(question[0]);

   // Get current exam context for priority caching
   const { examName, sectionName, selectedTopics, selectedThemes, selectedTypes } = usePaginationStore();
   const { loadingState, initializePriorityCache, updateUserBehavior } =
      usePriorityCacheContext();

   // Combine all selected categorical tags for caching system
   const allSelectedTags = React.useMemo(() => [
      ...selectedTopics,
      ...selectedThemes,
      ...selectedTypes
   ], [selectedTopics, selectedThemes, selectedTypes]);

   useEffect(() => {
      if (question[0]) {
         setQuestionData(question[0]);
         // Set isLongOptions based on option text length
         setIsLongOptions(
            question[0].problemoptions?.some(
               (option: any) => option.optiontext.length > 50
            ) || false
         );
      }
   }, [question]);

   // Initialize priority caching when component mounts or context changes
   useEffect(() => {
      if (examName && sectionName) {
         initializePriorityCache(examName, sectionName, { topics: selectedTopics, themes: selectedThemes, types: selectedTypes });
         updateUserBehavior(examName, sectionName);
      }
   }, [
      examName,
      sectionName,
      allSelectedTags,
      initializePriorityCache,
      updateUserBehavior,
   ]);

   const { start, questionIds, setStart } = useNavigationStore();

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

   const [selectedOption, setSelectedOption] = useState<string[]>([]);
   const [showCacheProgress, setShowCacheProgress] = useState(false);
   const [isLongOptions, setIsLongOptions] = useState(false);

   // Extract tags for display
   const questionTags = React.useMemo(() => {
      return (questionData as any)?.problemtags?.flatMap((pt: any) => [
         pt.tags.topic,
         pt.tags.theme,
         pt.tags.type,
         pt.tags.name,
      ]).filter((tag: string | null) => tag !== null && tag !== undefined && tag !== "") || [];
   }, [questionData]);

   // Show cache progress when background loading is happening
   useEffect(() => {
      const isLoading =
         loadingState.immediate || loadingState.high || loadingState.background;
      setShowCacheProgress(isLoading && loadingState.progress.total > 0);
   }, [loadingState]);

   // Enhanced navigation with priority awareness
   const navigateToQuestion = useCallback(
      (newStart: number) => {
         // Update user behavior for background service
         if (examName && sectionName) {
            updateUserBehavior(examName, sectionName);
         }

         setStart(newStart);
         if (questionIds[newStart]) {
            const questionId =
               typeof questionIds[newStart] === "number"
                  ? (questionIds[newStart] as number)
                  : parseInt(Object.keys(questionIds[newStart] as object)[0]);

            switchQuestion(currentQuestionId, questionId);
         }
      },
      [
         examName,
         sectionName,
         updateUserBehavior,
         setStart,
         questionIds,
         switchQuestion,
         currentQuestionId,
      ]
   );

   const handleNext = useCallback(() => {
      if (start < questionIds.length - 1) {
         navigateToQuestion(start + 1);
      }
   }, [start, questionIds.length, navigateToQuestion]);

   const handlePrevious = useCallback(() => {
      if (start > 0) {
         navigateToQuestion(start - 1);
      }
   }, [start, navigateToQuestion]);

   const handleOptionSelect = useCallback(
      (option: string | string[]) => {
         const newOption = Array.isArray(option) ? option : [option];
         setSelectedOption(newOption);
         if (questionData?.problemid) {
            recordOptionSelectedTime(questionData.problemid);
         }
      },
      [recordOptionSelectedTime, questionData]
   );

   const handleSubmit = useCallback(() => {
      if (selectedOption.length > 0 && questionData) {
         const attemptTime = getElapsedTime(questionData.problemid);
         addAttempt({
            problemId: questionData.problemid,
            option: selectedOption,
            timetaken: attemptTime.toString(),
            partialcorrectnessscore: null,
         });

         // Clear selection and move to next question
         setSelectedOption([]);
         clearRecordedTime(questionData.problemid);

         if (start < questionIds.length - 1) {
            navigateToQuestion(start + 1);
         }
      }
   }, [
      selectedOption,
      questionData,
      getElapsedTime,
      addAttempt,
      clearRecordedTime,
      start,
      questionIds.length,
      navigateToQuestion,
   ]);

   const handleClearAll = useCallback(() => {
      // Clear current selection
      setSelectedOption([]);

      // Clear all store attempts
      resetAttempt();

      // Clear all recorded times for all questions in current set
      questionIds.forEach((id) => {
         const questionId =
            typeof id === "number"
               ? id
               : parseInt(Object.keys(id as object)[0]);
         clearRecordedTime(questionId);
      });
   }, [resetAttempt, clearRecordedTime, questionIds]);

   // Transform options to match expected format - always include group for TC/SE detection
   const transformedOptions = questionData?.problemoptions?.reduce(
      (acc, option, index) => {
         acc[index.toString()] = {
            optiontext: option.optiontext,
            group: option.group,
         };
         return acc;
      },
      {} as { [key: string]: { optiontext: string; group?: string } }
   );

   // Loading state with priority awareness
   if (status === "pending" || !questionData) {
      return (
         <div className="flex flex-col items-center justify-center h-64 space-y-4">
            <Loading />
            <div className="text-sm text-muted-foreground">
               Loading questions with priority caching...
            </div>
            {showCacheProgress && (
               <PriorityCacheProgressCompact
                  loadingState={loadingState}
                  className="w-64"
               />
            )}
         </div>
      );
   }

   if (status === "error") {
      return (
         <div className="flex flex-col items-center justify-center h-64 space-y-4">
            <div className="text-red-500">Error loading questions</div>
            <button
               onClick={() => window.location.reload()}
               className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
               Retry
            </button>
         </div>
      );
   }

   return (
      <div className="flex flex-col h-full relative">
         {/* Priority Cache Progress (compact) */}
         {showCacheProgress && (
            <div className="absolute top-2 right-2 z-10">
               <PriorityCacheProgressCompact
                  loadingState={loadingState}
                  className="w-48"
               />
            </div>
         )}

         {/* Timer */}
         {showTimer && (
            <div className="flex justify-between items-center p-4 border-b">
               <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-blue-500" />
                  <span className="text-sm text-muted-foreground">
                     Smart Caching: {loadingState.progress.completed}/
                     {loadingState.progress.total}
                  </span>
               </div>
               <Timer questionId={questionData?.problemid || 0} />
            </div>
         )}

         {/* Question Content */}
         <div className="flex-1 overflow-auto p-6 pt-1">
            {/* Question tags row */}
            {questionTagsEnabled && questionTags.length > 0 && (
               <div className="mb-4">
                  <QuestionTags tags={questionTags} />
               </div>
            )}

            {questionData && transformedOptions && (
               <QuestionDisplay
                  key={questionData.problemid}
                  type={questionData.type}
                  title={questionData.title}
                  text={questionData.text}
                  options_type={questionData.options_type}
                  options={transformedOptions}
                  selectedOption={selectedOption}
                  handleOptionClick={handleOptionSelect}
                  isLongOptions={isLongOptions}
                  handleClear={() => setSelectedOption([])}
                  handleClearAll={handleClearAll}
                  questionId={questionData.problemid}
                  showPagination={true}
                  size={5}
                  metadata={questionData.metadata}
                  localAttempts={new Map()}
                  tags={questionTags}
               />
            )}
         </div>

         {/* Navigation and Actions */}
         <div className="flex justify-between items-center p-4 border-t bg-background">
            <div className="flex items-center space-x-2">
               <span className="text-sm text-muted-foreground">
                  Question {start + 1} of {questionIds.length}
               </span>
               {bookmarksEnabled && (
                  <button
                     onClick={() => toggleFlag(questionData.problemid)}
                     className={`p-1 rounded ${isFlagged(questionData.problemid)
                        ? "text-yellow-500"
                        : "text-gray-400 hover:text-yellow-500"
                        }`}
                  >
                     <Bookmark className="h-4 w-4" />
                  </button>
               )}
            </div>

            <div className="flex space-x-2">
               <button
                  onClick={handlePrevious}
                  disabled={start === 0}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
               >
                  Previous
               </button>

               <button
                  onClick={handleSubmit}
                  disabled={selectedOption.length === 0}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
               >
                  Submit & Next
               </button>

               <button
                  onClick={handleNext}
                  disabled={start >= questionIds.length - 1}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
               >
                  Skip
               </button>
            </div>
         </div>

         {/* Close button */}
         <button
            onClick={() => onClose()}
            className="absolute top-4 right-4 p-2 text-gray-500 hover:text-gray-700"
         >
            ✕
         </button>
      </div>
   );
};

export default QuestionAttemptWithPriority;
