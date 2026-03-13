import { PaginationProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import { useEffect } from "react";
import { useAttemptStore } from "@/features/question-solving/hooks/(pagination)/problemDefinition";

const Pagination: React.FC<PaginationProps> = ({
   questionIds,
   currentQuestionId,
   size,
   onPageChange,
}) => {
   const { isFlagged, bookmarksEnabled } = useAttemptStore();
   // Flatten the questionIds array to handle nested structures
   const flattenQuestionIds = (
      ids: (number | { [key: string]: number[] })[]
   ) => {
      const flattened: number[] = [];
      ids.forEach((id) => {
         if (typeof id === "number") {
            flattened.push(id);
         } else {
            Object.values(id)[0].forEach((nestedId) => {
               flattened.push(nestedId);
            });
         }
      });
      return flattened;
   };

   const pureRange = flattenQuestionIds(questionIds);
   const totalQuestions = pureRange.length;
   const currentIndex = pureRange.findIndex((id) => id === currentQuestionId);
   const getPaginationRange = () => {
      const halfSize = Math.floor(size / 2);
      let start = Math.max(0, currentIndex - halfSize);
      let end = Math.min(totalQuestions, start + size);

      // Adjust start if we're near the end
      if (end === totalQuestions) {
         start = Math.max(0, end - size);
      }

      const range = pureRange.slice(start, end);
      const paginationRange: (number | string)[] = [...range];

      // Add first page and ellipsis if necessary
      if (start > 0) {
         if (start > 1) {
            paginationRange.unshift("...");
         }
         paginationRange.unshift(pureRange[0]);
      }

      // Add last page and ellipsis if necessary
      if (end < totalQuestions) {
         if (end < totalQuestions - 1) {
            paginationRange.push("...");
         }
         paginationRange.push(pureRange[totalQuestions - 1]);
      }

      return paginationRange;
   };

   const paginationRange = getPaginationRange();

   return (
      <div className="flex space-x-2 items-center">
         <button
            onClick={() => onPageChange(pureRange[0])}
            className={`p-2 border rounded-lg bg-background border-border hover:bg-muted ${
               currentIndex === 0
                  ? "bg-primary/10 text-primary"
                  : "text-foreground"
            }`}
            disabled={currentIndex === 0}
         >
            &lt;&lt;
         </button>
         <button
            onClick={() =>
               onPageChange(pureRange[Math.max(0, currentIndex - 1)])
            }
            className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground"
            disabled={currentIndex === 0}
         >
            &lt;
         </button>
         {paginationRange.map((id, index) => {
            const isCurrentQuestion = currentQuestionId === id;
            const isQuestionFlagged = typeof id === "number" && bookmarksEnabled && isFlagged(id);
            
            return (
               <button
                  key={index}
                  onClick={() => {
                     console.log("id on click:- ", id);
                     typeof id === "number" && onPageChange(id);
                  }}
                  className={`p-2 border rounded-lg ${
                     isCurrentQuestion
                        ? "bg-primary/10 border-2 border-primary font-bold text-primary"
                        : isQuestionFlagged
                        ? "bg-background border-2 border-yellow-400 dark:border-yellow-500 hover:bg-muted text-foreground"
                        : "bg-background border-border hover:bg-muted text-foreground"
                  }`}
                  disabled={typeof id !== "number"}
               >
                  {id}
               </button>
            );
         })}
         <button
            onClick={() =>
               onPageChange(
                  pureRange[Math.min(totalQuestions - 1, currentIndex + 1)]
               )
            }
            className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground"
            disabled={currentIndex === totalQuestions - 1}
         >
            &gt;
         </button>
         <button
            onClick={() => onPageChange(pureRange[totalQuestions - 1])}
            className="p-2 border rounded-lg bg-background border-border hover:bg-muted text-foreground"
            disabled={currentIndex === totalQuestions - 1}
         >
            &gt;&gt;
         </button>
      </div>
   );
};

export default Pagination;
