"use client";
import React from "react";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useQuestionCacheStore } from "@/shared/stores/problems/question-cache";
import {
   useProblemsStore,
   type ProblemsState,
} from "@/shared/stores/problems/cache";

export function useProblemsShuffleLogic() {
   const { shuffleQuestions } = useProblemsStore();
   const { setQuestionIds } = useNavigationStore();
   const { clearCache } = useQuestionCacheStore();

   const handleShuffle = React.useCallback(
      (
         problemData: any,
         setShuffledData: React.Dispatch<React.SetStateAction<any>>,
         setIsShuffled: React.Dispatch<React.SetStateAction<boolean>>,
         setIsShuffling?: React.Dispatch<React.SetStateAction<boolean>>
      ) => {
         console.log("Handle shuffle called");

         // Set shuffling state to prevent auto-opening question window
         if (setIsShuffling) {
            setIsShuffling(true);
         }

         if (!problemData.fullData || problemData.fullData.length === 0) {
            console.log("No data available to shuffle");
            if (setIsShuffling) {
               setIsShuffling(false);
            }
            return;
         }

         const data = [...problemData.fullData];
         console.log("Shuffling", data.length, "items");

         // Helper function to check if a problem/problemset is solved
         const isSolved = (item: any): boolean => {
            if ("isExpanded" in item) {
               // For ProblemsSet, check if ALL child problems are solved
               return item.problems.every(
                  (problem: any) =>
                     problem.iscorrect !== null &&
                     problem.iscorrect !== undefined
               );
            } else {
               // For individual Problem
               return item.iscorrect !== null && item.iscorrect !== undefined;
            }
         };

         // Separate solved and unsolved items
         const solvedItems: any[] = [];
         const unsolvedItems: any[] = [];

         data.forEach((item) => {
            if (isSolved(item)) {
               solvedItems.push(item);
            } else {
               unsolvedItems.push(item);
            }
         });

         console.log(
            "Unsolved items:",
            unsolvedItems.length,
            "Solved items:",
            solvedItems.length
         );

         // Shuffle both arrays using Fisher-Yates algorithm
         const shuffleArray = (array: any[]): any[] => {
            const shuffled = [...array];
            for (let i = shuffled.length - 1; i > 0; i--) {
               const j = Math.floor(Math.random() * (i + 1));
               [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
            }
            return shuffled;
         };

         const shuffledUnsolved = shuffleArray(unsolvedItems);
         const shuffledSolved = shuffleArray(solvedItems);

         // Combine: unsolved questions first, then solved questions
         const shuffledProblems = [...shuffledUnsolved, ...shuffledSolved];

         // Reassign absolute indices after shuffling to maintain correct navigation
         let absoluteIndex = 0;
         const shuffledWithNewIndices = shuffledProblems.map((item) => {
            if ("isExpanded" in item) {
               // For ProblemsSet, update each child's absoluteIndex
               const problemSet = item as any;
               const updatedProblems = problemSet.problems.map(
                  (problem: any) => ({
                     ...problem,
                     absoluteIndex: absoluteIndex++,
                  })
               );
               return {
                  ...problemSet,
                  problems: updatedProblems,
                  absoluteIndex: absoluteIndex - updatedProblems.length, // Set to first child's index
               };
            } else {
               // For individual Problem
               return {
                  ...item,
                  absoluteIndex: absoluteIndex++,
               };
            }
         });

         console.log(
            "Setting shuffled data with",
            shuffledWithNewIndices.length,
            "items"
         );

         setShuffledData({
            problemData: shuffledWithNewIndices,
            totalProblems: shuffledWithNewIndices.length,
         });
         setIsShuffled(true);

         // Clear question cache to avoid stale data
         clearCache();

         // Update the questionIds in the store to maintain navigation order
         shuffleQuestions(shuffledWithNewIndices);

         // Extract question IDs from shuffled data for navigation
         const shuffledQuestionIds: (number | { [key: string]: number[] })[] =
            [];
         shuffledWithNewIndices.forEach((item) => {
            if ("isExpanded" in item) {
               // For ProblemsSet, create object with problemsSetId as key and child problem IDs as value
               const problemSet = item as any;
               const childIds = problemSet.problems.map(
                  (problem: any) => problem.problemid
               );
               shuffledQuestionIds.push({
                  [problemSet.problemsSetId]: childIds,
               });
            } else {
               // For individual Problem, add the problemid directly
               shuffledQuestionIds.push(item.problemid);
            }
         });

         // Update navigation store with new shuffled question IDs
         setQuestionIds(shuffledQuestionIds);

         // Don't reset start index during shuffling to prevent auto-opening question window
         // The user can manually click on questions after shuffling

         // Clear shuffling state after a short delay to allow state to settle
         if (setIsShuffling) {
            setTimeout(() => {
               setIsShuffling(false);
            }, 100);
         }
      },
      [shuffleQuestions, clearCache, setQuestionIds]
   );

   return {
      handleShuffle,
   };
}
