"use client";

import React from "react";

import { LazyResultWindow } from "@/shared/components/feedback/lazy/LazyResultWindow";
import { LazyQuestionWindow } from "@/shared/components/feedback/lazy/LazyQuestionWindow";

import { usePaginatedProblems } from "@/features/question-solving/hooks/(pagination)/fetchProblems";
import { useGetTags } from "@/features/question-solving/hooks/(pagination)/fetchTags";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useProblemsStore } from "@/shared/stores/problems/cache";
import { useUIStore } from "@/shared/stores/problems/ui-state";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { useProblemsPageState } from "./hooks/use-problems-page-state";
import { useQuestionWindowControls } from "./hooks/use-question-window-controls";
import { ProblemsPanelLayout } from "./components/problems-panel-layout";
import Loading from "@/shared/components/feedback/loading";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

/**
 * Main problems page component - Clean, focused component using extracted hooks
 *
 * @returns JSX.Element - The problems page layout with question window and result window
 */
export default function ProblemsPage() {
   const problemData = usePaginatedProblems();
   const tagData = useGetTags();
   const {
      bookmarksEnabled,
      setBookmarksEnabled,
      questionTagsEnabled,
      setQuestionTagsEnabled,
      userId,
   } = useAttemptsStore();
   const { examName, sectionName, page, pageSize } = usePaginationStore();
   const { clearProblems } = useProblemsStore();
   const { ensurePreferencesInitialized } = useUIStore();

   // Initialize pagination cache system
   const { initializeService, shuffleQuestions, clearCache } =
      usePaginationCacheStore();

   const pageState = useProblemsPageState();
   const windowControls = useQuestionWindowControls();

   // Initialize cache service and UI preferences on component mount
   React.useEffect(() => {
      initializeService({}, userId);
      ensurePreferencesInitialized();
   }, [initializeService, userId, ensurePreferencesInitialized]);

   // Use refs to track previous values of exam and section
   const prevExamNameRef = React.useRef(examName);
   const prevSectionNameRef = React.useRef(sectionName);

   const { setStart } = useNavigationStore();

   // Clear cache when exam type or section changes
   React.useEffect(() => {
      const examChanged = prevExamNameRef.current !== examName;
      const sectionChanged = prevSectionNameRef.current !== sectionName;

      if (examChanged || sectionChanged) {
         const oldSectionId = `${prevExamNameRef.current}-${prevSectionNameRef.current}`;
         const newSectionId = `${examName}-${sectionName}`;

         console.log(
            `🔄 Section change detected: ${oldSectionId} -> ${newSectionId}`
         );
         console.log(`🧹 Clearing all caches and resetting navigation`);

         clearProblems(); // Clear the global problems store state
         clearCache(); // Clear pagination cache to ensure clean state
         setStart(-1); // Reset navigation index to prevent stale index issues

         console.log(
            `🔄 Cache cleared, ready for new section: ${newSectionId}`
         );
      }

      // Update refs with current values
      prevExamNameRef.current = examName;
      prevSectionNameRef.current = sectionName;
   }, [examName, sectionName, clearProblems, clearCache, setStart]);

   React.useEffect(() => {
      if (pageState.isQuestionWindowOpen || pageState.isResultWindowOpen) {
         document.body.style.overflow = "hidden";
      } else {
         document.body.style.overflow = "auto";
      }
      return () => {
         document.body.style.overflow = "auto";
      };
   }, [pageState.isQuestionWindowOpen, pageState.isResultWindowOpen]);

   const { pageTours, startTour, isTourRunning } = useTutorialStore();

   // Trigger Problems Tour
   React.useEffect(() => {
      if (!pageTours.problems && !isTourRunning && !pageState.isQuestionWindowOpen) {
         const timer = setTimeout(() => startTour("problems"), 1000);
         return () => clearTimeout(timer);
      }
   }, [pageTours.problems, isTourRunning, pageState.isQuestionWindowOpen, startTour]);

   // Debug logging for result window rendering
   /*React.useEffect(() => {
      console.log("DEBUG: Page - isResultWindowOpen:", pageState.isResultWindowOpen);
      console.log("DEBUG: Page - hasValidAttempts:", windowControls.hasValidAttempts);
      console.log("DEBUG: Page - pendingLocalAttempts:", pageState.pendingLocalAttempts);
      console.log("DEBUG: Page - Should render result window:", 
         pageState.isResultWindowOpen && (windowControls.hasValidAttempts || pageState.pendingLocalAttempts)
      );
   }, [pageState.isResultWindowOpen, windowControls.hasValidAttempts, pageState.pendingLocalAttempts]);
   */
   const processedProblemData = React.useMemo(() => {
      // The cache system now handles both normal and shuffled data
      // No need for separate shuffle data processing here
      return problemData;
   }, [problemData]);



   return (
      <div className="p-4 w-full">
         {pageState.isResultWindowOpen &&
            (windowControls.hasValidAttempts ||
               pageState.pendingLocalAttempts) && (
               <LazyResultWindow
                  onClose={() =>
                     windowControls.handleCloseResultWindow(
                        pageState.setIsResultWindowOpen,
                        pageState.setPendingLocalAttempts
                     )
                  }
                  localAttempts={pageState.pendingLocalAttempts}
                  hideLabels={true}
               />
            )}

         {pageState.isQuestionWindowOpen && (
            <LazyQuestionWindow
               onClose={() =>
                  windowControls.handleCloseQuestionWindow(
                     pageState.setIsQuestionWindowOpen
                  )
               }
               onFinish={(localAttempts: Map<number, any>) =>
                  windowControls.handleFinishSession(
                     pageState.setIsQuestionWindowOpen,
                     pageState.setIsResultWindowOpen,
                     pageState.setPendingLocalAttempts,
                     localAttempts || new Map()
                  )
               }
               showTimer={pageState.showTimer}
               hideLabels={true}
            />
         )}

         <ProblemsPanelLayout
            tagData={tagData}
            problemData={processedProblemData}
            bookmarksEnabled={bookmarksEnabled}
            setBookmarksEnabled={setBookmarksEnabled}
            showTimer={pageState.showTimer}
            setShowTimer={pageState.setShowTimer}
            showDifficulty={pageState.showDifficulty}
            setShowDifficulty={pageState.setShowDifficulty}
            questionTagsEnabled={questionTagsEnabled}
            setQuestionTagsEnabled={setQuestionTagsEnabled}
            openQuestion={() =>
               windowControls.handleOpenQuestionWindow(
                  pageState.setIsQuestionWindowOpen
               )
            }
            onShuffle={async (targetSectionId?: string) => {
               pageState.setIsShuffling(true);
               try {
                  const success = await shuffleQuestions(targetSectionId);
                  if (success) {
                     console.log(
                        `✅ Questions shuffled successfully for ${targetSectionId || 'current section'} via cache system`
                     );
                  }
               } catch (error) {
                  console.error("❌ Shuffle failed:", error);
               } finally {
                  pageState.setIsShuffling(false);
               }
            }}
            isShuffling={pageState.isShuffling}
         />
      </div>
   );
}
