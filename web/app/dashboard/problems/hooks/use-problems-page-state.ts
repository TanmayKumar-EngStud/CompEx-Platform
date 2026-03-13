"use client";
import { useState } from "react";

export interface ProblemsPageState {
   displaySolvedQuestions: boolean;
   isQuestionWindowOpen: boolean;
   isResultWindowOpen: boolean;
   showTimer: boolean;
   showDifficulty: boolean;
   shuffledData: any;
   isShuffled: boolean;
   isShuffling: boolean;
   pendingLocalAttempts: Map<number, string[]> | null;
}

export function useProblemsPageState() {
   const [displaySolvedQuestions, setDisplaySolvedQuestions] =
      useState<boolean>(false);
   const [isQuestionWindowOpen, setIsQuestionWindowOpen] =
      useState<boolean>(false);
   const [isResultWindowOpen, setIsResultWindowOpen] = useState<boolean>(false);
   const [showTimer, setShowTimer] = useState<boolean>(true);
   const [showDifficulty, setShowDifficulty] = useState<boolean>(true);
   const [shuffledData, setShuffledData] = useState<any>(null);
   const [isShuffled, setIsShuffled] = useState<boolean>(false);
   const [isShuffling, setIsShuffling] = useState<boolean>(false);
   const [pendingLocalAttempts, setPendingLocalAttempts] = useState<Map<number, string[]> | null>(null);

   return {
      // State values
      displaySolvedQuestions,
      isQuestionWindowOpen,
      isResultWindowOpen,
      showTimer,
      showDifficulty,
      shuffledData,
      isShuffled,
      isShuffling,
      pendingLocalAttempts,

      // State setters
      setDisplaySolvedQuestions,
      setIsQuestionWindowOpen,
      setIsResultWindowOpen,
      setShowTimer,
      setShowDifficulty,
      setShuffledData,
      setIsShuffled,
      setIsShuffling,
      setPendingLocalAttempts,
   };
}
