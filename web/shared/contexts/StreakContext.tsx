"use client";
import React, { createContext, useContext } from "react";
import { useProblemsStreak } from "@/shared/hooks/useProblemsStreak";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";

interface StreakContextType {
   streakData: {
      currentstreak: number;
      solvedToday: boolean;
      totalDays: number;
   };
   loading: boolean;
   error: string | null;
   incrementStreakForToday: () => void;
   shouldIncrementStreak: () => boolean;
   refetchStreak: () => Promise<void>;
}

const StreakContext = createContext<StreakContextType | undefined>(undefined);

export const StreakProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
   const { userId } = useAttemptsStore();
   const streakHook = useProblemsStreak(userId);
   
   return (
      <StreakContext.Provider value={streakHook}>
         {children}
      </StreakContext.Provider>
   );
};

export const useStreak = () => {
   const context = useContext(StreakContext);
   if (context === undefined) {
      throw new Error('useStreak must be used within a StreakProvider');
   }
   return context;
};