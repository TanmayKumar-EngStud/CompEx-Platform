"use client";
import React, { useEffect, useState } from "react";
import { StreakIcon } from "@/shared/components/ui/icons/streak-icons";

interface ProblemsStreakProps {
   streak?: number;
   className?: string;
}

const ProblemsStreak: React.FC<ProblemsStreakProps> = ({
   streak = 0,
   className = "",
}) => {
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   if (!mounted) {
      return (
         <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-transparent"></div>
      );
   }

   return (
      <div
         className={`flex items-center gap-2 px-3 py-2 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 ${className}`}
         title={`Problems solving streak: ${streak} days`}
      >
         <StreakIcon />
         <span className="text-sm font-bold min-w-[20px] text-center">
            {streak}
         </span>
      </div>
   );
};

export default ProblemsStreak;
