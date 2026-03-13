"use client";
import React from "react";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useTimerStore } from "@/features/user-analytics/hooks/timerDefinition";
import { useResultData } from "@/features/user-analytics/hooks/resultWindowDefinitions";
import { useStreak } from "@/shared/contexts/StreakContext";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";

export function useQuestionWindowControls() {
   const {
      Attempt,
      userId,
      resetAttempt,
      addAttempt
   } = useAttemptsStore();
   const { setStart, questionIds, start } = useNavigationStore();
   const { getElapsedTime } = useTimerStore();
   const { setResultData } = useResultData();
   const { incrementStreakForToday, shouldIncrementStreak } = useStreak();
   const { currentPage, currentSectionId } = usePaginationCacheStore();

   const handleCloseQuestionWindow = React.useCallback(
      (
         setIsQuestionWindowOpen: React.Dispatch<React.SetStateAction<boolean>>
      ) => {
         setIsQuestionWindowOpen(false);
         setStart(-1);
         console.log("DEBUG: handleCloseQuestionWindow - Closed without submission");
      },
      [setStart]
   );

   const handleFinishSession = React.useCallback(
      async (
         setIsQuestionWindowOpen: React.Dispatch<React.SetStateAction<boolean>>,
         setIsResultWindowOpen: React.Dispatch<React.SetStateAction<boolean>>,
         setPendingLocalAttempts: React.Dispatch<React.SetStateAction<Map<number, string[]> | null>>,
         localAttempts: Map<number, string[]>
      ) => {
         setIsQuestionWindowOpen(false);
         setStart(-1);

         // Check localAttempts first, then fallback to store attempts
         const hasLocalAttempts = localAttempts && localAttempts.size > 0 &&
            Array.from(localAttempts.values()).some(options => options.length > 0);
         const hasStoreAttempts = Attempt?.some(
            (attempt) => attempt.option.length > 0
         );

         console.log("DEBUG: handleFinishSession - localAttempts:", localAttempts);
         console.log("DEBUG: handleFinishSession - hasLocalAttempts:", hasLocalAttempts);
         console.log("DEBUG: handleFinishSession - hasStoreAttempts:", hasStoreAttempts);

         if (hasLocalAttempts) {
            console.log("DEBUG: Processing localAttempts and opening result window");

            try {
               // Process localAttempts here instead of in result window
               const processedAttempts: typeof Attempt = [];

               localAttempts.forEach((option, problemId) => {
                  if (option.length > 0) {
                     const elapsedTimeMs = getElapsedTime(problemId);
                     const elapsedTimeSeconds = Math.floor(elapsedTimeMs / 1000);
                     const timetakenFormatted =
                        elapsedTimeSeconds >= 60
                           ? `${Math.floor(elapsedTimeSeconds / 60)} min ${elapsedTimeSeconds % 60
                           } sec`
                           : `${elapsedTimeSeconds} sec`;

                     processedAttempts.push({
                        problemId,
                        option,
                        timetaken: timetakenFormatted,
                        partialcorrectnessscore: null,
                     });
                  }
               });

               // Add to store
               resetAttempt();
               processedAttempts.forEach((attempt) => addAttempt(attempt));

               // Call API
               const payload = {
                  userID: userId,
                  Attempt: processedAttempts.map((attempt) => ({
                     questionID: attempt.problemId,
                     option: attempt.option,
                     timetaken: attempt.timetaken,
                     partialcorrectnessscore: attempt.partialcorrectnessscore,
                  })),
               };

               console.log("DEBUG: handleFinishSession - Calling API with payload:", payload);

               const response = await fetch("/api/submit-answers", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(payload),
               });

               if (!response.ok) throw new Error(`HTTP ${response.status}`);

               const result = await response.json();
               console.log("DEBUG: handleFinishSession - API response:", result);
               setResultData(result);

               // Increment streak for first submission of the day
               if (shouldIncrementStreak()) {
                  incrementStreakForToday();
               }

               // Clear pending attempts since we processed them
               setPendingLocalAttempts(null);

               // Now open result window with processed data
               setIsResultWindowOpen(true);

            } catch (error) {
               console.error("🆕 SUBMIT ERROR in handleFinishSession:", error);
            }
         } else if (hasStoreAttempts) {
            console.log("DEBUG: Opening result window with existing store attempts");
            setIsResultWindowOpen(true);
         } else {
            console.log("DEBUG: No valid attempts, not opening result window");
         }
      },
      [Attempt, setStart, getElapsedTime, resetAttempt, addAttempt, userId, setResultData, shouldIncrementStreak, incrementStreakForToday]
   );

   const handleOpenQuestionWindow = React.useCallback(
      (
         setIsQuestionWindowOpen: React.Dispatch<React.SetStateAction<boolean>>
      ) => {
         // Only open if we have questions available
         if (questionIds && questionIds.length > 0) {
            // Only set start to 0 if no valid start index is already set
            if (start < 0) {
               setStart(0);
            }
            setIsQuestionWindowOpen(true);
         } else {
            console.warn("Cannot open question window: No questions available yet. Please wait for questions to load.");
         }
      },
      [setStart, questionIds, start]
   );

   const handleCloseResultWindow = React.useCallback(
      (
         setIsResultWindowOpen: React.Dispatch<React.SetStateAction<boolean>>,
         setPendingLocalAttempts: React.Dispatch<React.SetStateAction<Map<number, string[]> | null>>
      ) => {
         // Store the current page before any operations that might reset it
         const preservedPage = currentPage;

         setStart(-1);
         setIsResultWindowOpen(false);
         // Clear pending attempts after viewing results to start fresh
         setPendingLocalAttempts(null);

         // Use a timeout to ensure any side effects from the above operations complete
         // before attempting to restore the page number
         setTimeout(() => {
            const { currentPage: updatedPage, jumpToPage } = usePaginationCacheStore.getState();
            if (updatedPage !== preservedPage && preservedPage > 0) {
               console.log(`🔄 Restoring pagination to page ${preservedPage} after result window close`);
               jumpToPage(preservedPage);
            }
         }, 0);
      },
      [setStart, currentPage]
   );

   return {
      handleCloseQuestionWindow,
      handleFinishSession,
      handleOpenQuestionWindow,
      handleCloseResultWindow,
      hasValidAttempts: Attempt?.some((attempt) => attempt.option.length > 0),
   };
}
