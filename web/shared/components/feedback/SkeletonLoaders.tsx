"use client";

import React from "react";
import { motion } from "framer-motion";

// Base skeleton component with shimmer animation
const Skeleton = React.memo(
   ({
      className = "",
      variant = "default",
   }: {
      className?: string;
      variant?: "default" | "rounded" | "circle" | "text";
   }) => {
      const baseClasses = "bg-muted animate-pulse";
      const variantClasses = {
         default: "rounded",
         rounded: "rounded-lg",
         circle: "rounded-full",
         text: "rounded h-4",
      };

      return (
         <motion.div
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            initial={{ opacity: 0.6 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{
               duration: 1.5,
               repeat: Infinity,
               ease: "easeInOut",
            }}
         />
      );
   }
);

Skeleton.displayName = "Skeleton";

// Tag section skeleton loader
export const TagSectionSkeleton = React.memo(() => {
   return (
      <motion.div
         className="w-full space-y-4"
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ duration: 0.3 }}
      >
         <div className="flex flex-wrap gap-3">
            {Array.from({ length: 8 }).map((_, index) => (
               <Skeleton key={index} className="h-10 w-24" variant="rounded" />
            ))}
         </div>
         <div className="flex justify-end mt-5 gap-4 items-center">
            <Skeleton className="h-4 w-32" variant="text" />
            <Skeleton className="h-6 w-12" variant="rounded" />
         </div>
      </motion.div>
   );
});

TagSectionSkeleton.displayName = "TagSectionSkeleton";

// Question table skeleton loader
export const QuestionTableSkeleton = React.memo(() => {
   return (
      <motion.div
         className="space-y-4"
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ duration: 0.3 }}
      >
         <div className="rounded-md border border-border">
            {/* Table Header */}
            <div className="border-b border-border p-4">
               <div className="flex justify-between">
                  {Array.from({ length: 4 }).map((_, index) => (
                     <Skeleton
                        key={index}
                        className="h-6 w-20"
                        variant="text"
                     />
                  ))}
               </div>
            </div>

            {/* Table Rows */}
            <div className="divide-y divide-border">
               {Array.from({ length: 10 }).map((_, rowIndex) => (
                  <motion.div
                     key={rowIndex}
                     className="p-4 flex justify-between items-center"
                     initial={{ opacity: 0, y: 10 }}
                     animate={{ opacity: 1, y: 0 }}
                     transition={{ delay: rowIndex * 0.05 }}
                  >
                     <Skeleton className="h-4 w-8" variant="text" />
                     <Skeleton className="h-4 w-48" variant="text" />
                     <Skeleton className="h-6 w-8" variant="circle" />
                     <Skeleton className="h-4 w-20" variant="text" />
                  </motion.div>
               ))}
            </div>
         </div>

         {/* Pagination Skeleton */}
         <div className="flex justify-center">
            <div className="flex space-x-2">
               {Array.from({ length: 5 }).map((_, index) => (
                  <Skeleton key={index} className="h-8 w-8" variant="rounded" />
               ))}
            </div>
         </div>
      </motion.div>
   );
});

QuestionTableSkeleton.displayName = "QuestionTableSkeleton";

// Calendar skeleton loader
export const CalendarSkeleton = () => {
   return (
      <motion.div
         className="max-w-md min-w-[28rem] mt-10 mx-auto p-4 bg-card text-card-foreground rounded-lg shadow-md border border-border"
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ duration: 0.3 }}
      >
         {/* Calendar Header - matches calendar.tsx renderHeader */}
         <div className="flex justify-between items-center mb-4">
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-6 w-32" variant="text" />
            <Skeleton className="h-8 w-8 rounded-full" />
         </div>

         {/* Days Header - matches calendar.tsx renderDays */}
         <div className="grid grid-cols-7 mb-2">
            {Array.from({ length: 7 }).map((_, index) => (
               <Skeleton
                  key={index}
                  className="h-10 w-10 mx-auto"
                  variant="text"
               />
            ))}
         </div>

         {/* Calendar Grid - matches calendar.tsx renderCells (6 weeks x 7 days) */}
         <div className="space-y-0">
            {Array.from({ length: 6 }).map((_, weekIndex) => (
               <div key={weekIndex} className="grid grid-cols-7">
                  {Array.from({ length: 7 }).map((_, dayIndex) => (
                     <Skeleton
                        key={dayIndex}
                        className="h-10 w-10 mx-auto rounded-full"
                     />
                  ))}
               </div>
            ))}
         </div>
      </motion.div>
   );
};

CalendarSkeleton.displayName = "CalendarSkeleton";

// Generic content skeleton for panels
export const ContentSkeleton = React.memo(
   ({
      rows = 3,
      cols = 1,
      className = "",
   }: {
      rows?: number;
      cols?: number;
      className?: string;
   }) => {
      return (
         <motion.div
            className={`space-y-4 ${className}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
         >
            {Array.from({ length: rows }).map((_, rowIndex) => (
               <div key={rowIndex} className={`grid grid-cols-${cols} gap-4`}>
                  {Array.from({ length: cols }).map((_, colIndex) => (
                     <Skeleton
                        key={colIndex}
                        className="h-16 w-full"
                        variant="rounded"
                     />
                  ))}
               </div>
            ))}
         </motion.div>
      );
   }
);

ContentSkeleton.displayName = "ContentSkeleton";

export default Skeleton;
