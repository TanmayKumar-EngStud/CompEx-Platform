"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PaginationProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import {
   ChevronLeft,
   ChevronRight,
   ChevronsLeft,
   ChevronsRight,
} from "lucide-react";

interface AnimatedPaginationProps extends Omit<PaginationProps, "size"> {
   windowSize?: number;
   size?: number;
   localAttempts?: Map<number, string[]>;
   resultCorrectnessData?: Map<number, boolean>;
   isResultWindow?: boolean;
}

const AnimatedPagination: React.FC<AnimatedPaginationProps> = ({
   questionIds,
   currentQuestionId,
   onPageChange,
   windowSize = 9,
   localAttempts,
   resultCorrectnessData,
   isResultWindow = false,
}) => {
   const { isFlagged, bookmarksEnabled, getAttemptForProblem } = useAttemptsStore();
   const [isCyclicTransition, setIsCyclicTransition] = useState(false);

   // 1. Flatten and unique question IDs
   const allQuestions = useMemo(() => {
      const flattened: number[] = [];
      const seen = new Set<number>();

      questionIds.forEach((id) => {
         if (typeof id === "number") {
            if (!seen.has(id)) {
               flattened.push(id);
               seen.add(id);
            }
         } else {
            Object.values(id)[0].forEach((nestedId) => {
               if (!seen.has(nestedId)) {
                  flattened.push(nestedId);
                  seen.add(nestedId);
               }
            });
         }
      });
      return flattened;
   }, [questionIds]);

   const totalQuestions = allQuestions.length;
   const currentIndex = allQuestions.findIndex((id) => id === currentQuestionId);

   // 2. Window Calculation (Absolute Track Approach)
   const { visibleQuestions, windowStart } = useMemo(() => {
      if (totalQuestions <= windowSize) {
         return { visibleQuestions: allQuestions, windowStart: 0 };
      }

      const halfWindow = Math.floor(windowSize / 2);
      let start = currentIndex - halfWindow;

      if (start < 0) start = 0;
      if (start + windowSize > totalQuestions) start = totalQuestions - windowSize;

      // Render a slightly larger window to prevent gaps during animation
      const buffer = 3;
      const renderStart = Math.max(0, start - buffer);
      const renderEnd = Math.min(totalQuestions, start + windowSize + buffer);

      return {
         visibleQuestions: allQuestions.slice(renderStart, renderEnd),
         windowStart: start,
      };
   }, [allQuestions, totalQuestions, currentIndex, windowSize]);

   const buttonSize = 48;
   const gap = 4;
   const buttonWithGap = buttonSize + gap;

   // Track offset for continuous sliding
   const trackX = -(windowStart * buttonWithGap);
   // Highlighter position (relative to the track)
   const highlighterX = currentIndex * buttonWithGap;

   const navigate = useCallback(
      (direction: "super-left" | "left" | "right" | "super-right") => {
         let newIndex: number;
         switch (direction) {
            case "super-left": newIndex = 0; break;
            case "left":
               newIndex = currentIndex > 0 ? currentIndex - 1 : totalQuestions - 1;
               if (currentIndex === 0) {
                  setIsCyclicTransition(true);
                  setTimeout(() => setIsCyclicTransition(false), 800);
               }
               break;
            case "right":
               newIndex = currentIndex < totalQuestions - 1 ? currentIndex + 1 : 0;
               if (currentIndex === totalQuestions - 1) {
                  setIsCyclicTransition(true);
                  setTimeout(() => setIsCyclicTransition(false), 800);
               }
               break;
            case "super-right": newIndex = totalQuestions - 1; break;
            default: return;
         }
         onPageChange(allQuestions[newIndex]);
      },
      [currentIndex, totalQuestions, allQuestions, onPageChange]
   );

   const getFontSize = useCallback((questionNumber: number) => {
      const length = questionNumber.toString().length;
      if (length <= 2) return "text-sm";
      if (length === 3) return "text-xs";
      return "text-[10px]";
   }, []);

   return (
      <div className="flex items-center justify-center space-x-2 py-2 select-none">
         {/* Super Left */}
         {totalQuestions > 1 && (
            <button
               onClick={() => navigate("super-left")}
               className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground transition-colors disabled:opacity-30"
               disabled={currentIndex === 0}
            >
               <ChevronsLeft size={16} />
            </button>
         )}

         {/* Left */}
         {totalQuestions > 1 && (
            <button
               onClick={() => navigate("left")}
               className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground transition-colors"
            >
               <ChevronLeft size={16} />
            </button>
         )}

         {/* Pinned Pagination Track Container */}
         <div
            className="relative overflow-hidden h-12"
            style={{ width: `${windowSize * buttonWithGap - gap}px` }}
         >
            {/* Cyclic transition indicator */}
            <AnimatePresence>
               {isCyclicTransition && (
                  <motion.div
                     className="absolute inset-0 border-2 border-primary rounded-lg pointer-events-none z-10"
                     initial={{ opacity: 0, scale: 0.8 }}
                     animate={{ opacity: 1, scale: 1.05 }}
                     exit={{ opacity: 0, scale: 1 }}
                     transition={{ duration: 0.4 }}
                  />
               )}
            </AnimatePresence>

            {/* Continuous Sliding Track */}
            <motion.div
               className="relative h-full"
               initial={false}
               animate={{ x: trackX }}
               transition={{
                  type: "tween",
                  ease: [0.4, 0.0, 0.2, 1.0],
                  duration: 0.8,
               }}
            >
               {/* Independent Highlighter - The blue selection that moves quickly */}
               <motion.div
                  className="absolute top-0 bg-primary rounded-lg shadow-lg z-10"
                  initial={false}
                  animate={{
                     x: highlighterX,
                     width: buttonSize,
                     height: buttonSize
                  }}
                  transition={{
                     type: "tween",
                     ease: [0.4, 0.0, 0.2, 1.0],
                     duration: 0.35, // Faster than the track slide
                  }}
               >
                  <motion.div
                     className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent rounded-lg"
                     animate={{ x: ["-100%", "100%"] }}
                     transition={{ duration: 0.8, repeat: Infinity, repeatDelay: 2 }}
                  />
               </motion.div>

               {visibleQuestions.map((questionId) => {
                  const qIndex = allQuestions.findIndex(id => id === questionId);
                  const isCurrent = questionId === currentQuestionId;
                  const questionPosition = qIndex + 1;
                  const isBkmpark = bookmarksEnabled && isFlagged(questionId);
                  const isCorrect = resultCorrectnessData?.get(questionId);
                  const solved = getAttemptForProblem(questionId) || (localAttempts?.has(questionId) && (localAttempts.get(questionId)?.length ?? 0) > 0);

                  return (
                     <button
                        key={questionId}
                        onClick={() => onPageChange(questionId)}
                        className={`
                            absolute top-0 flex items-center justify-center border-2 rounded-lg font-bold transition-colors duration-200
                            ${getFontSize(questionPosition)}
                            ${isCurrent ? "text-primary-foreground border-transparent z-20" :
                              isResultWindow && isCorrect !== undefined ?
                                 (isCorrect ? "bg-green-100 text-green-800 border-green-400" : "bg-red-100 text-red-800 border-red-400") :
                                 solved ? "bg-green-100 text-green-800 border-green-400" : "bg-background text-foreground border-border hover:bg-muted"}
                        `}
                        style={{
                           width: `${buttonSize}px`,
                           height: `${buttonSize}px`,
                           left: `${qIndex * buttonWithGap}px`,
                        }}
                     >
                        {isBkmpark && (
                           <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full border border-background shadow-sm z-30" />
                        )}
                        <span className="relative z-20">{questionPosition}</span>
                     </button>
                  );
               })}
            </motion.div>
         </div>

         {/* Right */}
         {totalQuestions > 1 && (
            <button
               onClick={() => navigate("right")}
               className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground transition-colors"
            >
               <ChevronRight size={16} />
            </button>
         )}

         {/* Super Right */}
         {totalQuestions > 1 && (
            <button
               onClick={() => navigate("super-right")}
               className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground transition-colors disabled:opacity-30"
               disabled={currentIndex === totalQuestions - 1}
            >
               <ChevronsRight size={16} />
            </button>
         )}
      </div>
   );
};

export default AnimatedPagination;
