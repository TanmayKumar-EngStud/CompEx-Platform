"use client";

import React, { useState, useCallback, useEffect, lazy, Suspense } from "react";
import { ResultWindowProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import { useResultData } from "@/features/user-analytics/hooks/resultWindowDefinitions";
import { QuestionProps } from "@/features/question-solving/components/QuestionWindow/QuestionDisplay/questionDisplay";

// Breaking circular/complex dependency with lazy loading
const QuestionDisplay = lazy(() => import("@/features/question-solving/components/QuestionWindow/QuestionDisplay/questionDisplay"));
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useProblemsStore } from "@/shared/stores/problems/cache";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";

import { Bookmark, CheckCircle2, XCircle, Clock, Target, Activity, ArrowLeft, X, MessageSquareHeart } from "lucide-react";
import { truncateBrackets } from "@/shared/lib/utils/formatting";
import QuestionFeedbackModal from "@/features/user-analytics/components/feedback/QuestionFeedbackModal";

const truncateText = (text: string, maxLength: number) => {
   return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
};

const ResultWindow: React.FC<ResultWindowProps> = ({
   onClose,
   hideLabels = false,
   isFullPage = false,
   closeButtonText = "Exit Results"
}) => {
   const [questionDisplayProps, setQuestionDisplayProps] =
      useState<QuestionProps | null>(null);
   const { resultData } = useResultData();

   const { Attempt, resetAttempt, isFlagged, bookmarksEnabled } =
      useAttemptsStore();

   const { updateProblemsWithAttemptData } = useProblemsStore();
   const { updateCacheWithAttemptData } = usePaginationCacheStore();
   const { invalidateQuestions } = useQuestionCacheStore();

   // Feedback modal state
   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
   const [feedbackQuestionId, setFeedbackQuestionId] = useState<number | null>(null);

   const handleOpenFeedback = useCallback(() => {
      if (questionDisplayProps?.questionId) {
         setFeedbackQuestionId(questionDisplayProps.questionId);
         setShowFeedbackModal(true);
      }
   }, [questionDisplayProps]);

   const handleCloseFeedback = useCallback(() => {
      setShowFeedbackModal(false);
      setFeedbackQuestionId(null);
   }, []);

   const handleFeedbackSubmit = useCallback((rating: number, comment: string) => {
      console.log('Feedback submitted:', rating, comment);
   }, []);

   const handleBack = useCallback(() => {
      setQuestionDisplayProps(null);
   }, []);

   const handlePageChange = (id: number) => {
      if (resultData) {
         const newResult = resultData.find((result) => result.problemid === id);
         if (!newResult) return;

         const questionIds = resultData.map((resultdata) => resultdata.problemid);
         const isLongOptions = newResult?.options.some((option) => option.optiontext.length > 10);

         const transformedOptions = newResult?.options.reduce(
            (acc, option, index) => {
               acc[index.toString()] = {
                  optiontext: option.optiontext,
                  group: option.group,
               };
               return acc;
            },
            {} as { [key: string]: { optiontext: string; group: string } }
         );

         setQuestionDisplayProps({
            type: newResult.type,
            title: newResult.title,
            text: newResult.text,
            options: transformedOptions,
            selectedOption: newResult.selectedoption,
            correctOption: newResult.correctoption,
            isLongOptions: isLongOptions,
            questionId: newResult.problemid,
            questionIds: questionIds,
            size: Math.min(questionIds.length, 9),
            showPagination: true,
            showSolution: true,
            solution: newResult.solution,
            handlePageChange: handlePageChange,
            tags: ((newResult as any).problemtags || []).flatMap((pt: any) => [
               pt.tags.topic,
               pt.tags.theme,
               pt.tags.type,
               pt.tags.name,
            ]).filter((tag: string | null) => tag).map((t: string) => truncateBrackets(t)),
            parentTags: (newResult as any).parentTags || [],
            options_type: newResult.options_type,
            metadata: {
               ...newResult.metadata,
               difficulty: newResult.difficulty,
            },
         });
      }
   };

   const handleQuestionClick = useCallback(
      (
         questionId: number,
         type: string,
         title: string,
         text: string,
         diagram: string | null,
         options: { optiontext: string; group: string }[],
         selectedOption: string[],
         correctOption: string[],
         solution: any,
         metadata: any,
         tags: string[],
         options_type: string | null,
         difficulty: number,
         parentTags: string[] = []
      ) => {
         const isLongOptions = options.some((option) => option.optiontext.length > 10);
         const currentQuestionIds = resultData?.map((resultdata) => resultdata.problemid) || [];

         const transformedOptions = options.reduce((acc, option, index) => {
            acc[index.toString()] = {
               optiontext: option.optiontext,
               group: option.group,
            };
            return acc;
         }, {} as { [key: string]: { optiontext: string; group: string } });

         setQuestionDisplayProps({
            type,
            title,
            text,
            options: transformedOptions,
            selectedOption,
            correctOption,
            isLongOptions,
            questionId,
            questionIds: currentQuestionIds,
            size: Math.min(currentQuestionIds.length, 9),
            showPagination: true,
            showSolution: true,
            solution,
            tags,
            parentTags,
            handlePageChange: handlePageChange,
            options_type,
            metadata: {
               ...metadata,
               difficulty: difficulty,
            },
            hideLabels: hideLabels,
         });
      },
      [resultData, handlePageChange]
   );

   const compareList = useCallback((list1: string[], list2: string[]) => {
      if (!list1 || !list2) return false;
      return list1.length === list2.length && list1.every((item) => list2.includes(item));
   }, []);

   const handleClose = useCallback(() => {
      if (resultData && resultData.length > 0) {
         const attemptResults = resultData.map(result => ({
            problemid: result.problemid,
            iscorrect: compareList(result.correctoption, result.selectedoption)
         }));
         updateProblemsWithAttemptData(attemptResults);
         updateCacheWithAttemptData(attemptResults);
         // Invalidate LRU question cache so re-navigation fetches fresh data with iscorrect
         invalidateQuestions(attemptResults.map(r => r.problemid));
      }
      resetAttempt();
      onClose();
   }, [resetAttempt, onClose, resultData, updateProblemsWithAttemptData, updateCacheWithAttemptData, invalidateQuestions, compareList]);

   const resultStats = (() => {
      if (!resultData || !Attempt) return null;

      const correctAnswers = resultData.filter((item) =>
         compareList(item.correctoption, item.selectedoption)
      ).length;

      const accuracy = ((correctAnswers / resultData.length) * 100).toFixed(1);

      const totalSeconds = resultData.reduce((total, item) => {
         const timeStr = item.timetaken;
         let seconds = 0;
         if (timeStr.includes("min")) {
            const parts = timeStr.split(" ");
            const minIndex = parts.findIndex((p) => p === "min");
            const secIndex = parts.findIndex((p) => p === "sec");
            if (minIndex > 0) seconds += parseInt(parts[minIndex - 1]) * 60;
            if (secIndex > 0 && secIndex !== minIndex + 1) {
               seconds += parseInt(parts[secIndex - 1]);
            }
         } else if (timeStr.includes("sec")) {
            const match = timeStr.match(/(\d+)\s*sec/);
            if (match) seconds = parseInt(match[1]);
         }
         return total + seconds;
      }, 0);

      const formattedTime = totalSeconds >= 60
         ? `${Math.floor(totalSeconds / 60)}m ${totalSeconds % 60}s`
         : `${totalSeconds}s`;

      return {
         totalQuestions: resultData.length,
         correctAnswers,
         accuracy,
         totalTime: formattedTime,
      };
   })();

   const resultAttempts = React.useMemo(() => {
      const attemptMap = new Map<number, string[]>();
      resultData?.forEach((result) => {
         if (result.selectedoption?.length > 0) {
            attemptMap.set(result.problemid, result.selectedoption);
         }
      });
      return attemptMap;
   }, [resultData]);

   const correctnessData = React.useMemo(() => {
      const correctnessMap = new Map<number, boolean>();
      resultData?.forEach((result) => {
         correctnessMap.set(result.problemid, compareList(result.correctoption, result.selectedoption));
      });
      return correctnessMap;
   }, [resultData, compareList]);

   // Keyboard navigation for question analysis
   useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
         if (!questionDisplayProps || !resultData) return;

         // Find current index
         const currentIndex = resultData.findIndex(r => r.problemid === questionDisplayProps.questionId);
         if (currentIndex === -1) return;

         if (e.key === "ArrowRight") {
            const nextIndex = (currentIndex + 1) % resultData.length;
            handlePageChange(resultData[nextIndex].problemid);
         } else if (e.key === "ArrowLeft") {
            const prevIndex = (currentIndex - 1 + resultData.length) % resultData.length;
            handlePageChange(resultData[prevIndex].problemid);
         }
      };

      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
   }, [questionDisplayProps, resultData]);

   const truncateBracketsInTags = (tagList: string[]) => {
      return tagList.map(tag => truncateBrackets(tag));
   };

   const getContent = () => {
      if (questionDisplayProps) {
         return (
            <div data-tour="result-solution-view" className={`flex flex-col h-full gap-4 w-full ${isFullPage ? '' : 'max-w-7xl mx-auto px-6 sm:px-10 lg:px-16'}`}>
               <div className="flex-grow min-h-0 flex flex-col">
                  <Suspense fallback={<div className="h-full flex items-center justify-center">Loading analysis...</div>}>
                     <QuestionDisplay
                        {...questionDisplayProps}
                        localAttempts={resultAttempts}
                        resultCorrectnessData={correctnessData}
                        isResultWindow={true}
                        tags={questionDisplayProps.tags}
                        parentTags={questionDisplayProps.parentTags}
                     />
                  </Suspense>
               </div>
            </div>
         );
      }

      if (resultData) {
         return (
            <div className="flex-1 overflow-y-auto p-6 sm:p-10 lg:p-16 animate-in fade-in slide-in-from-bottom-4 duration-500">
               <div className="max-w-7xl mx-auto">
                  <div className="mb-8 text-center pt-2">
                     <h2 className="text-3xl font-extrabold text-foreground tracking-tight sm:text-4xl">
                        Session Summary
                     </h2>
                     <p className="mt-2 text-muted-foreground">Great job! Here's how you performed in this session.</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
                     <StatCard
                        label="Accuracy"
                        value={`${resultStats?.accuracy}%`}
                        icon={<Target className="w-5 h-5 text-indigo-500" />}
                        bg="bg-indigo-50 dark:bg-indigo-900/10"
                        border="border-indigo-100 dark:border-indigo-900/20"
                     />
                     <StatCard
                        label="Score"
                        value={`${resultStats?.correctAnswers} / ${resultStats?.totalQuestions}`}
                        icon={<Activity className="w-5 h-5 text-emerald-500" />}
                        bg="bg-emerald-50 dark:bg-emerald-900/10"
                        border="border-emerald-100 dark:border-emerald-900/20"
                     />
                     <StatCard
                        label="Total Time"
                        value={resultStats?.totalTime || "0s"}
                        icon={<Clock className="w-5 h-5 text-amber-500" />}
                        bg="bg-amber-50 dark:bg-amber-900/10"
                        border="border-amber-100 dark:border-amber-900/20"
                     />
                     <StatCard
                        label="Questions"
                        value={resultStats?.totalQuestions.toString() || "0"}
                        icon={<CheckCircle2 className="w-5 h-5 text-blue-500" />}
                        bg="bg-blue-50 dark:bg-blue-900/10"
                        border="border-blue-100 dark:border-blue-900/20"
                     />
                  </div>

                  <div className="bg-background rounded-2xl border border-border shadow-sm overflow-hidden mb-6">
                     <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                           <thead>
                              <tr className="bg-muted/50 border-b border-border">
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">#</th>
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Title</th>
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Your Answer</th>
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Correct Answer</th>
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider text-center">Difficulty</th>
                                 <th className="px-5 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Time</th>
                              </tr>
                           </thead>
                           <tbody className="divide-y divide-border/50">
                              {resultData.map((result, idx) => {
                                 const isCorrect = compareList(result.correctoption, result.selectedoption);
                                 const isQuestionFlagged = bookmarksEnabled && isFlagged(result.problemid);

                                 return (
                                    <tr
                                       key={result.problemid}
                                       data-tour={idx === 0 ? "result-table-first-row" : undefined}
                                       onClick={() => handleQuestionClick(
                                          result.problemid, result.type, result.title, result.text, result.diagram,
                                          result.options, result.selectedoption, result.correctoption, result.solution, result.metadata,
                                          ((result as any).problemtags || []).flatMap((pt: any) => [
                                             pt.tags.topic,
                                             pt.tags.theme,
                                             pt.tags.type,
                                             pt.tags.name,
                                          ]).filter((tag: string | null) => tag).map((t: string) => truncateBrackets(t)),
                                          result.options_type,
                                          result.difficulty,
                                          (result as any).parentTags || []
                                       )}
                                       className="group hover:bg-muted/30 cursor-pointer transition-colors"
                                    >
                                       <td className="px-5 py-4">
                                          <div className="flex items-center gap-2">
                                             <span className="text-sm font-medium text-muted-foreground">{idx + 1}</span>
                                             {isQuestionFlagged && (
                                                <Bookmark size={14} className="text-amber-500 fill-current" />
                                             )}
                                          </div>
                                       </td>
                                       <td className="px-5 py-4">
                                          <div className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                                             {truncateBrackets(truncateText(result.title, 40))}
                                          </div>
                                       </td>
                                       <td className="px-5 py-4">
                                          <div className="text-sm text-foreground flex flex-wrap gap-1">
                                             {result.selectedoption.length > 0 ? (
                                                result.selectedoption.map((opt, i) => (
                                                   <span key={i} className={`px-2 py-0.5 rounded-md text-[11px] font-medium border ${isCorrect ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
                                                      {truncateText(opt, 15)}
                                                   </span>
                                                ))
                                             ) : (
                                                <span className="text-muted-foreground italic">Skipped</span>
                                             )}
                                          </div>
                                       </td>
                                       <td className="px-5 py-4">
                                          <div className="text-sm text-foreground flex flex-wrap gap-1">
                                             {result.correctoption.map((opt, i) => (
                                                <span key={i} className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-emerald-50 border border-emerald-200 text-emerald-700">
                                                   {truncateText(opt, 15)}
                                                </span>
                                             ))}
                                          </div>
                                       </td>
                                       <td className="px-5 py-4 text-center">
                                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border tracking-wider ${(result.difficulty || 0) >= 4
                                             ? "bg-rose-50 text-rose-600 border-rose-100"
                                             : (result.difficulty || 0) >= 3
                                                ? "bg-amber-50 text-amber-600 border-amber-100"
                                                : "bg-emerald-50 text-emerald-600 border-emerald-100"
                                             }`}>
                                             {result.difficulty}
                                          </span>
                                       </td>
                                       <td className="px-5 py-4">
                                          <div className="flex items-center gap-1.5 text-sm text-muted-foreground whitespace-nowrap">
                                             <Clock size={12} />
                                             {result.timetaken}
                                          </div>
                                       </td>
                                    </tr>
                                 );
                              })}
                           </tbody>
                        </table>
                     </div>
                  </div>
               </div>
            </div>
         );
      }

      return (
         <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-muted-foreground font-medium animate-pulse">Analyzing results...</p>
         </div>
      );
   };

   const mainContent = (
      <div className={isFullPage
         ? "relative bg-background w-full h-full select-none flex flex-col pt-4 overflow-hidden"
         : "relative bg-background p-6 shadow-xl rounded-lg w-11/12 max-w-5xl h-5/6 select-none overflow-hidden border border-border"}>

         <div className={isFullPage
            ? "sticky top-0 left-0 right-0 bg-background/95 backdrop-blur-md p-4 border-b border-border/60 z-20 flex justify-between items-center transition-all px-6 sm:px-10 lg:px-16"
            : "absolute top-0 left-0 right-0 bg-background/80 backdrop-blur-md p-4 border-b border-border/60 z-10 flex justify-between items-center transition-all"}>

            <div className={isFullPage ? "flex flex-col max-w-7xl mx-auto w-full relative sm:flex-row sm:items-center sm:justify-between sm:gap-4" : "flex flex-col"}>
               <div className="flex flex-col">
                  <h1 className="text-xl font-bold text-foreground">
                     {questionDisplayProps ? "Question Analysis" : "Session Finalized"}
                  </h1>
                  {questionDisplayProps && (
                     <div className="flex items-center gap-3">
                        <p className="text-xs text-muted-foreground font-medium uppercase tracking-tight truncate max-w-[150px] sm:max-w-xs">
                           {truncateBrackets(truncateText(questionDisplayProps.title, 60))}
                        </p>
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-black border tracking-wider ${((questionDisplayProps.metadata as any)?.difficulty || 0) >= 4
                           ? "bg-rose-50 text-rose-600 border-rose-100"
                           : ((questionDisplayProps.metadata as any)?.difficulty || 0) >= 3
                              ? "bg-amber-50 text-amber-600 border-amber-100"
                              : "bg-emerald-50 text-emerald-600 border-emerald-100"
                           }`}>
                           LEVEL {((questionDisplayProps.metadata as any)?.difficulty || "N/A")}
                        </span>
                     </div>
                  )}
               </div>

               {isFullPage && (
                  <div className="flex items-center gap-2 mt-2 sm:mt-0">
                     {questionDisplayProps && (
                        <button
                           className="px-3 py-2 rounded-xl flex items-center gap-2 transition-all duration-300 font-bold text-sm shadow-sm bg-amber-50 text-amber-600 border border-amber-200 hover:bg-amber-100"
                           onClick={handleOpenFeedback}
                        >
                           <MessageSquareHeart size={16} />
                           <span>Rate</span>
                        </button>
                     )}
                     <button
                        className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all duration-300 font-bold text-sm shadow-sm ${questionDisplayProps
                           ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-[1.02] active:scale-95"
                           : "bg-rose-500/10 text-rose-600 hover:bg-rose-500/20 dark:bg-rose-500/20 dark:text-rose-400"
                           }`}
                        onClick={questionDisplayProps ? handleBack : handleClose}
                     >
                        {questionDisplayProps ? (
                           <>
                              <ArrowLeft size={16} />
                              <span>Back Overview</span>
                           </>
                        ) : (
                           <>
                              <X size={16} />
                              <span>{closeButtonText}</span>
                           </>
                        )}
                     </button>
                  </div>
               )}
            </div>

            {!isFullPage && (
               <div className="flex items-center gap-2">
                  {questionDisplayProps && (
                     <button
                        className="px-3 py-2 rounded-xl flex items-center gap-2 transition-all duration-300 font-bold text-sm shadow-sm bg-amber-50 text-amber-600 border border-amber-200 hover:bg-amber-100"
                        onClick={handleOpenFeedback}
                     >
                        <MessageSquareHeart size={16} />
                        <span>Rate</span>
                     </button>
                  )}
                  <button
                     className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all duration-300 font-bold text-sm shadow-sm ${questionDisplayProps
                        ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-[1.02] active:scale-95"
                        : "bg-rose-500/10 text-rose-600 hover:bg-rose-500/20 dark:bg-rose-500/20 dark:text-rose-400"
                        }`}
                     onClick={questionDisplayProps ? handleBack : handleClose}
                  >
                     {questionDisplayProps ? (
                        <>
                           <ArrowLeft size={16} />
                           <span>Back Overview</span>
                        </>
                     ) : (
                        <>
                           <X size={16} />
                           <span>{closeButtonText}</span>
                        </>
                     )}
                  </button>
               </div>
            )}
         </div>
         <div className={isFullPage ? "flex-grow min-h-0 flex flex-col" : "h-full pt-16 overflow-auto"}>{getContent()}</div>
      </div>
   );

   const feedbackModalElement = (showFeedbackModal && feedbackQuestionId) ? (
      <QuestionFeedbackModal
         questionId={feedbackQuestionId}
         isOpen={showFeedbackModal}
         onClose={handleCloseFeedback}
         onSubmit={handleFeedbackSubmit}
      />
   ) : null;

   if (isFullPage) {
      return (
         <>
            {mainContent}
            {feedbackModalElement}
         </>
      );
   }

   return (
      <>
         <div data-tour="result-window" className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
            {mainContent}
         </div>
         {feedbackModalElement}
      </>
   );
};

const StatCard = ({ label, value, icon, bg, border }: { label: string, value: string, icon: React.ReactNode, bg: string, border: string }) => (
   <div className={`p-5 rounded-2xl border ${border} ${bg} flex items-center gap-4 transition-all hover:shadow-md hover:-translate-y-0.5`}>
      <div className="p-3 bg-background rounded-xl shadow-sm">
         {icon}
      </div>
      <div>
         <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{label}</p>
         <p className="text-2xl font-black text-foreground">{value}</p>
      </div>
   </div>
);

export default ResultWindow;
