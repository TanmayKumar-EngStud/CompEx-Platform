import React, { useState, useEffect } from "react";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import {
   type HybridProblem,
   type ProblemsSet,
   type Problem,
   type ProblemsResponse,
} from "@/shared/stores/problems/cache";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import ArrowIcons from "@/shared/components/ui/icons/arrow-icons";
import {
   Table,
   TableBody,
   TableCell,
   TableHead,
   TableHeader,
   TableRow,
} from "@/shared/components/ui/table";
import { Button } from "@/shared/components/ui/button";
import clsx from "clsx";
import { truncateBrackets } from "@/shared/lib/utils/formatting";
import { motion, AnimatePresence } from "framer-motion";

const MotionTableRow = motion(TableRow);

const containerVariants = {
   hidden: { opacity: 0 },
   show: {
      opacity: 1,
      transition: {
         staggerChildren: 0.05
      }
   },
   exit: {
      opacity: 0,
      transition: {
         staggerChildren: 0.03,
         staggerDirection: -1
      }
   }
};

const itemVariants = {
   hidden: {
      opacity: 0,
      filter: "blur(10px)",
      y: 20,
      scale: 0.98
   },
   show: {
      opacity: 1,
      filter: "blur(0px)",
      y: 0,
      scale: 1,
      transition: {
         type: "spring",
         stiffness: 300,
         damping: 25
      }
   },
   exit: {
      opacity: 0,
      filter: "blur(10px)",
      scale: 0.98,
      transition: { duration: 0.2 }
   }
};

interface QueryDataProp {
   status: string;
   error: unknown;
   data: ProblemsResponse | undefined;
   previousData: ProblemsResponse | null;
}

const QuestionTable = React.memo(function QuestionTable({
   queryData,
   openQuestion,
   displaySolvedQuestions,
   showDifficulty = true,
   isShuffling = false,
}: {
   queryData: QueryDataProp;
   openQuestion: () => void;
   displaySolvedQuestions: boolean;
   showDifficulty?: boolean;
   isShuffling?: boolean;
}) {
   const [rows, setRows] = useState<HybridProblem[]>([]);
   function isProblemSet(item: HybridProblem) {
      if ("isExpanded" in item) {
         return true;
      } else {
         return false;
      }
   }
   useEffect(() => {
      if (queryData.data?.problemData) {
         setRows(queryData.data.problemData);
      }
   }, [queryData.data]);

   const toggleExpand = (index: number) => {
      const updatedRows = [...rows];
      if ("isExpanded" in updatedRows[index])
         updatedRows[index].isExpanded = !updatedRows[index].isExpanded;
      setRows(updatedRows);
   };

   const { status, error } = queryData;
   const { categoryIndex, sortOrder, setCategoryIndex, setSortOrder, pageSize } =
      usePaginationStore();
   const { start, setStart } = useNavigationStore();
   const { masterQuestionIds, currentPage } = usePaginationCacheStore();

   const headings = showDifficulty
      ? ["#", "Title", "Difficulty", "Added on"]
      : ["#", "Title", "Added on"];

   const handleSortClick = (
      category: "#" | "Title" | "Difficulty" | "Added on"
   ) => {
      if (category === "#") {
         return;
      }
      if (categoryIndex === headings.indexOf(category)) {
         if (sortOrder === 0) {
            setSortOrder(1);
         } else if (sortOrder === 1) {
            setSortOrder(-1);
         } else {
            setSortOrder(0);
         }
      } else {
         setCategoryIndex(headings.indexOf(category));
         setSortOrder(1);
      }
   };

   const renderSortArrows = (
      category: "#" | "Title" | "Difficulty" | "Added on"
   ) => {
      if (category === "#") {
         return <></>;
      }
      if (categoryIndex !== headings.indexOf(category)) {
         return <ArrowIcons up down />;
      }
      if (sortOrder === 1) {
         return <ArrowIcons up />;
      }
      if (sortOrder === -1) {
         return <ArrowIcons down />;
      }
      return <ArrowIcons up down />;
   };

   const onRowClick = (absoluteIndex: number, problemId: string | number) => {
      // Create flattened list from master question IDs to find the correct index
      const flattenedQuestionIds: number[] = [];
      masterQuestionIds.forEach((id) => {
         if (typeof id === "number") {
            flattenedQuestionIds.push(id);
         } else {
            // For parent-child questions, add all child question IDs
            Object.values(id)[0].forEach((childId) => {
               flattenedQuestionIds.push(childId);
            });
         }
      });

      // Find the index in the flattened list
      const flattenedIndex = flattenedQuestionIds.findIndex(
         (id) => id === parseInt(String(problemId), 10)
      );

      console.log("🔍 QUESTION TABLE CLICK DEBUG:", {
         problemId: problemId,
         absoluteIndex: absoluteIndex,
         flattenedIndex: flattenedIndex,
         flattenedQuestionIdsLength: flattenedQuestionIds.length,
         first10FlattenedIds: flattenedQuestionIds.slice(0, 10),
         clickedIdType: typeof problemId,
      });

      if (flattenedIndex >= 0) {
         console.log(
            `🎯 Question clicked: problemId=${problemId}, flattenedIndex=${flattenedIndex} (in flattened list of ${flattenedQuestionIds.length})`
         );
         setStart(flattenedIndex);
      } else {
         console.warn(
            `⚠️ Question ${problemId} not found in flattened list, using fallback index ${absoluteIndex}`
         );
         setStart(absoluteIndex);
      }
   };

   useEffect(() => {
      // Only auto-open question window if not currently shuffling
      if (start >= 0 && !isShuffling) {
         openQuestion();
      }
   }, [start, isShuffling]);

   // Helper function to get solved status styling
   const getSolvedStatusClasses = (
      item: HybridProblem,
      isParent: boolean = false
   ) => {
      if (!displaySolvedQuestions) return "";
      if (isParent) return ""; // Don't style parent rows

      const problem = item as Problem;
      if (problem.iscorrect === null || problem.iscorrect === undefined) {
         return ""; // Not attempted
      }

      return problem.iscorrect === true
         ? "bg-green-500/10 dark:bg-green-500/20 border-l-2 border-l-green-500"
         : "bg-red-500/10 dark:bg-red-500/20 border-l-2 border-l-red-500";
   };

   const showItsID = (row: HybridProblem) => {
      if (isProblemSet(row)) {
         return (row as ProblemsSet).problemsSetId;
      } else {
         return (row as Problem).problemid;
      }
   };
   /**
    * DifficultyBadge component for consistent, professional styling
    */
   const DifficultyBadge = ({ difficulty }: { difficulty: number | null | undefined }) => {
      const level = difficulty || 0;

      const getStyles = (val: number) => {
         switch (val) {
            case 1:
               return "bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400 border-blue-200/50 dark:border-blue-800/50";
            case 2:
               return "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400 border-emerald-200/50 dark:border-emerald-800/50";
            case 3:
               return "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400 border-amber-200/50 dark:border-amber-800/50";
            case 4:
               return "bg-orange-500/10 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400 border-orange-200/50 dark:border-orange-800/50";
            case 5:
               return "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400 border-rose-200/50 dark:border-rose-800/50";
            default:
               return "bg-muted text-muted-foreground border-border";
         }
      };

      return (
         <div className="flex justify-center w-full">
            <span
               className={clsx(
                  "inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-bold border transition-all duration-200 min-w-[24px]",
                  getStyles(level)
               )}
            >
               {level || "-"}
            </span>
         </div>
      );
   };
   // function to show the date
   function formatDate(isoDateString: string | null | undefined) {
      if (!isoDateString) {
         return "N/A";
      }

      try {
         const date = new Date(isoDateString);

         // Check if the date is valid
         if (isNaN(date.getTime())) {
            console.warn("Invalid date format:", isoDateString);
            return "Invalid Date";
         }

         const day = String(date.getUTCDate()).padStart(2, "0");
         const month = String(date.getUTCMonth() + 1).padStart(2, "0"); // Months are 0-indexed
         const year = date.getUTCFullYear();
         return `${day}/${month}/${year}`;
      } catch (error) {
         console.warn("Error formatting date:", isoDateString, error);
         return "Invalid Date";
      }
   }
   // Early return for null/undefined data - let parent handle loading states
   if (queryData === undefined || !queryData.data) {
      return null;
   }

   // Let parent DataLoader handle loading and error states
   if (status === "loading" || error) {
      return null;
   }

   if (status === "success") {
      return (
         <div className="space-y-4">
            <div className="rounded-md border border-border">
               <Table>
                  <TableHeader>
                     <TableRow className="hover:bg-muted/50">
                        {headings.map((heading) => {
                           const isCentered = heading === "#" || heading === "Difficulty";
                           return (
                              <TableHead key={heading}>
                                 <Button
                                    variant="ghost"
                                    className={clsx(
                                       "w-full text-foreground group",
                                       isCentered ? "justify-center" : "justify-between"
                                    )}
                                    onClick={() =>
                                       handleSortClick(
                                          heading as
                                          | "Title"
                                          | "Difficulty"
                                          | "Added on"
                                       )
                                    }
                                 >
                                    <div className="flex items-center gap-2">
                                       <span>{heading}</span>
                                       {renderSortArrows(
                                          heading as
                                          | "Title"
                                          | "Difficulty"
                                          | "Added on"
                                       )}
                                    </div>
                                 </Button>
                              </TableHead>
                           );
                        })}
                     </TableRow>
                  </TableHeader>
                  <TableBody>
                     <AnimatePresence mode="wait">
                        {rows.length > 0 ? (
                           rows.map((row, index) => {
                              return (
                                 <React.Fragment key={`parent-${index}-${showItsID(row)}`}>
                                    <MotionTableRow
                                       variants={itemVariants}
                                       initial="hidden"
                                       animate="show"
                                       exit="exit"
                                       className={`hover:bg-muted/50 ${isProblemSet(row) ? "bg-muted/20" : ""
                                          } ${getSolvedStatusClasses(
                                             row,
                                             isProblemSet(row)
                                          )}`}
                                       onClick={() => {
                                          if (isProblemSet(row)) {
                                             return toggleExpand(index);
                                          } else {
                                             return onRowClick(
                                                (row as Problem).absoluteIndex ||
                                                0,
                                                (row as Problem).problemid
                                             );
                                          }
                                       }}
                                    >
                                       <TableCell
                                          align="center"
                                          className="text-foreground"
                                       >
                                          {isProblemSet(row) && (
                                             <span className="mr-2 text-foreground">
                                                {(row as ProblemsSet).isExpanded
                                                   ? "▼"
                                                   : "▶"}
                                             </span>
                                          )}
                                          {(currentPage - 1) * pageSize + index + 1}
                                       </TableCell>
                                       <TableCell className="text-foreground">
                                          {showItsID(row) + " - " + truncateBrackets(row.title)}
                                       </TableCell>
                                       {showDifficulty && (
                                          <TableCell>
                                             <DifficultyBadge difficulty={row.difficulty} />
                                          </TableCell>
                                       )}
                                       <TableCell className="text-foreground">
                                          {isProblemSet(row)
                                             ? formatDate(
                                                (row as ProblemsSet).problems?.[0]?.addedDate ||
                                                (row as ProblemsSet).addedDate
                                             )
                                             : formatDate(
                                                (row as Problem).addedDate
                                             )}
                                       </TableCell>
                                    </MotionTableRow>
                                    {isProblemSet(row) &&
                                       (row as ProblemsSet).isExpanded && (
                                          <>
                                             {(row as ProblemsSet).problems?.map(
                                                (child, childIdx) => (
                                                   <MotionTableRow
                                                      key={`child-${index}-${childIdx}`}
                                                      variants={itemVariants}
                                                      initial="hidden"
                                                      animate="show"
                                                      exit="exit"
                                                      className={`hover:bg-muted/50 bg-muted/10 ${getSolvedStatusClasses(
                                                         child as HybridProblem,
                                                         false
                                                      )}`}
                                                      onClick={() =>
                                                         onRowClick(
                                                            child.absoluteIndex ||
                                                            0,
                                                            child.problemid
                                                         )
                                                      }
                                                   >
                                                      <TableCell className="text-foreground text-center">
                                                         {`${(currentPage - 1) * pageSize + index + 1}.${childIdx + 1
                                                            }`}
                                                      </TableCell>
                                                      <TableCell className="text-foreground">
                                                         <span className="ml-4">
                                                            {showItsID(child) +
                                                               " -> " +
                                                               truncateBrackets(child.title)}
                                                         </span>
                                                      </TableCell>
                                                      {showDifficulty && (
                                                         <TableCell>
                                                            <DifficultyBadge difficulty={child.difficulty} />
                                                         </TableCell>
                                                      )}
                                                      <TableCell className="text-foreground">
                                                         {formatDate(
                                                            child.addedDate
                                                         )}
                                                      </TableCell>
                                                   </MotionTableRow>
                                                )
                                             )}
                                          </>
                                       )}
                                 </React.Fragment>
                              );
                           })
                        ) : rows.length === 0 ? (
                           <TableRow>
                              <TableCell
                                 colSpan={showDifficulty ? 4 : 3}
                                 className="text-center py-4 text-muted-foreground"
                              >
                                 Content not available
                              </TableCell>
                           </TableRow>
                        ) : null}
                     </AnimatePresence>
                  </TableBody>
               </Table>
            </div>
         </div>
      );
   }
});

export default QuestionTable;
