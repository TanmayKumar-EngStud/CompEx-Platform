"use client";
import { useState, useEffect } from "react";

interface StreakData {
   currentstreak: number;
   solvedToday: boolean;
   totalDays: number;
}

export const useProblemsStreak = (userId: number = 1) => {
   const [streakData, setStreakData] = useState<StreakData>({
      currentstreak: 0,
      solvedToday: false,
      totalDays: 0,
   });
   const [loading, setLoading] = useState(true);
   const [error, setError] = useState<string | null>(null);

   const fetchStreak = async () => {
      try {
         setLoading(true);
         const response = await fetch(`/api/streaks?userId=${userId}`);
         
         if (!response.ok) {
            throw new Error("Failed to fetch streak data");
         }
         
         const data = await response.json();
         setStreakData({
            currentstreak: data.currentstreak,
            solvedToday: data.solvedToday,
            totalDays: data.totalDays,
         });
         setError(null);
      } catch (err) {
         setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
         setLoading(false);
      }
   };

   const incrementStreakForToday = () => {
      if (!streakData.solvedToday) {
         setStreakData(prev => ({
            ...prev,
            currentstreak: prev.currentstreak + 1,
            solvedToday: true,
            totalDays: prev.totalDays + 1,
         }));
      }
   };

   const shouldIncrementStreak = (): boolean => {
      return !streakData.solvedToday;
   };

   useEffect(() => {
      fetchStreak();
   }, [userId]);

   return {
      streakData,
      loading,
      error,
      incrementStreakForToday,
      shouldIncrementStreak,
      refetchStreak: fetchStreak,
   };
};